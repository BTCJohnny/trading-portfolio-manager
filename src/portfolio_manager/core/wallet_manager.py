# src/portfolio_manager/core/wallet_manager.py
"""
Wallet sheet management for individual trading bot portfolios.
"""
from datetime import datetime
from typing import Dict, Any, Optional, List
import gspread
from ..connectors.sheets_connector import SheetsConnector
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class WalletManager:
    """Manages individual wallet/bot sheets with trade tracking and performance metrics."""
    
    def __init__(self, sheets_connector: SheetsConnector, wallet_name: str):
        """
        Initialize wallet manager.
        
        Args:
            sheets_connector: Connected SheetsConnector instance
            wallet_name: Name of the wallet/bot
        """
        self.connector = sheets_connector
        self.wallet_name = wallet_name
        self.worksheet = None
        self._setup_wallet_sheet()
        logger.info(f"Wallet manager initialized for: {wallet_name}")
    
    def _setup_wallet_sheet(self) -> None:
        """Set up or get existing wallet sheet."""
        self.worksheet = self.connector.get_or_create_worksheet(self.wallet_name)
        
        # Check if sheet is already set up by looking for our headers
        try:
            cell_value = self.worksheet.acell('A1').value
            if cell_value and "WALLET SUMMARY" in cell_value:
                logger.info(f"Wallet sheet {self.wallet_name} already configured")
                return
        except:
            pass
        
        # Set up new sheet structure
        self._create_sheet_structure()
    
    def _create_sheet_structure(self) -> None:
        """Create the structure for a new wallet sheet."""
        logger.info(f"Setting up new structure for wallet: {self.wallet_name}")
        
        # Clear existing content
        self.worksheet.clear()
        
        # Wallet summary section
        summary_headers = [
            [f"{self.wallet_name} - WALLET SUMMARY", "", "", "", "", "", "", ""],
            ["Initial Investment:", "=SUMPRODUCT((B6:B1000=\"BUY\")*(F6:F1000))", "Current Value:", "=IF(ROW(G1000:G6)>0,INDEX(G6:G1000,COUNTA(G6:G1000)),0)", "Total Return:", "=D2-B2", "APY:", "=IF(AND(B2>0,D2>0,COUNTA(A6:A1000)>0),POWER((D2/B2),(365/MAX(1,DAYS(TODAY(),MIN(A6:A1000)))))-1,0)*100"],
            ["", "", "", "", "", "", "", ""],
            ["TRADE LOG", "", "", "", "", "", "", ""],
            ["Date", "Action", "Asset", "Quantity", "Price", "Total Value", "Running Balance", "Notes"]
        ]
        
        # Write headers
        for i, row in enumerate(summary_headers):
            range_name = f'A{i+1}:H{i+1}'
            self.connector.update_range(self.worksheet, range_name, [row])
        
        # Apply formatting
        self._format_wallet_sheet()
    
    def _format_wallet_sheet(self) -> None:
        """Apply formatting to the wallet sheet."""
        try:
            # Title formatting
            self.worksheet.format('A1:H1', {
                'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.2},
                'textFormat': {
                    'foregroundColor': {'red': 1, 'green': 1, 'blue': 1},
                    'bold': True,
                    'fontSize': 12
                },
                'horizontalAlignment': 'CENTER'
            })
            
            # Trade log header
            self.worksheet.format('A4:H4', {
                'backgroundColor': {'red': 0.8, 'green': 0.8, 'blue': 0.8},
                'textFormat': {'bold': True}
            })
            
            # Column headers
            self.worksheet.format('A5:H5', {
                'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9},
                'textFormat': {'bold': True}
            })
            
            logger.debug(f"Formatting applied to wallet sheet: {self.wallet_name}")
            
        except Exception as e:
            logger.warning(f"Could not apply formatting to {self.wallet_name}: {e}")
    
    def add_trade(self, trade_data: Dict[str, Any]) -> bool:
        """
        Add a new trade to the wallet sheet.
        
        Args:
            trade_data: Dictionary containing trade information
        
        Returns:
            True if successful
        """
        try:
            # Find next empty row (starting from row 6)
            values = self.worksheet.get_all_values()
            next_row = max(6, len([row for row in values if any(row)]) + 1)
            
            # Calculate total value if not provided
            quantity = float(trade_data.get('quantity', 0))
            price = float(trade_data.get('price', 0))
            total_value = trade_data.get('total_value', quantity * price)
            
            # Prepare trade row
            trade_row = [
                trade_data.get('date', datetime.now().strftime('%Y-%m-%d')),
                trade_data.get('action', '').upper(),  # BUY/SELL
                trade_data.get('asset', ''),
                quantity,
                price,
                total_value,
                self._calculate_running_balance_formula(next_row),
                trade_data.get('notes', '')
            ]
            
            # Add trade to sheet
            range_name = f'A{next_row}:H{next_row}'
            success = self.connector.update_range(self.worksheet, range_name, [trade_row])
            
            if success:
                logger.info(f"Added trade to {self.wallet_name}: {trade_data.get('action')} {trade_data.get('asset')}")
                return True
            else:
                logger.error(f"Failed to add trade to {self.wallet_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding trade to {self.wallet_name}: {e}")
            return False
    
    def _calculate_running_balance_formula(self, row_num: int) -> str:
        """
        Calculate running balance formula for a given row.
        
        Args:
            row_num: Row number for the formula
        
        Returns:
            Excel formula string
        """
        if row_num == 6:  # First trade row
            return "=IF(B6=\"BUY\",F6,IF(B6=\"SELL\",-F6,0))"
        else:
            return f"=G{row_num-1}+IF(B{row_num}=\"BUY\",F{row_num},IF(B{row_num}=\"SELL\",-F{row_num},0))"
    
    def get_wallet_performance(self) -> Dict[str, Any]:
        """
        Get wallet performance metrics.
        
        Returns:
            Dictionary with performance data
        """
        try:
            # Get values from summary section
            initial_investment = self._get_cell_value('B2', default=0)
            current_value = self._get_cell_value('D2', default=0)
            total_return = self._get_cell_value('F2', default=0)
            apy = self._get_cell_value('H2', default=0)
            
            # Calculate additional metrics
            total_return_pct = 0
            if initial_investment > 0:
                total_return_pct = ((current_value / initial_investment) - 1) * 100
            
            performance_data = {
                'name': self.wallet_name,
                'initial_investment': initial_investment,
                'current_value': current_value,
                'total_return': total_return,
                'total_return_pct': total_return_pct,
                'apy': apy
            }
            
            logger.debug(f"Performance data retrieved for {self.wallet_name}: {performance_data}")
            return performance_data
            
        except Exception as e:
            logger.error(f"Error getting performance data for {self.wallet_name}: {e}")
            return {
                'name': self.wallet_name,
                'initial_investment': 0,
                'current_value': 0,
                'total_return': 0,
                'total_return_pct': 0,
                'apy': 0
            }
    
    def _get_cell_value(self, cell_address: str, default: float = 0) -> float:
        """
        Get numeric value from a cell with error handling.
        
        Args:
            cell_address: Cell address (e.g., 'B2')
            default: Default value if cell is empty or error
        
        Returns:
            Numeric value from cell
        """
        try:
            value = self.worksheet.acell(cell_address).value
            if value is None or value == '':
                return default
            
            # Handle different value types
            if isinstance(value, str):
                # Remove currency symbols and commas
                cleaned_value = value.replace('$', '').replace(',', '').replace('%', '')
                return float(cleaned_value)
            
            return float(value)
            
        except Exception as e:
            logger.warning(f"Could not get value from {cell_address} in {self.wallet_name}: {e}")
            return default
    
    def get_trade_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get trade history from the wallet sheet.
        
        Args:
            limit: Maximum number of trades to return
        
        Returns:
            List of trade dictionaries
        """
        try:
            # Get all values starting from row 6 (first trade row)
            all_values = self.worksheet.get_all_values()
            
            if len(all_values) < 6:
                return []
            
            # Extract trade data (skip header rows)
            trade_rows = all_values[5:]  # Start from row 6 (index 5)
            trades = []
            
            for row in trade_rows:
                if not any(row[:6]):  # Skip empty rows
                    continue
                
                try:
                    trade = {
                        'date': row[0],
                        'action': row[1],
                        'asset': row[2],
                        'quantity': float(row[3]) if row[3] else 0,
                        'price': float(row[4]) if row[4] else 0,
                        'total_value': float(row[5]) if row[5] else 0,
                        'running_balance': float(row[6]) if row[6] else 0,
                        'notes': row[7] if len(row) > 7 else ''
                    }
                    trades.append(trade)
                except (ValueError, IndexError) as e:
                    logger.warning(f"Skipping invalid trade row in {self.wallet_name}: {e}")
                    continue
            
            # Apply limit if specified
            if limit and len(trades) > limit:
                trades = trades[-limit:]  # Get most recent trades
            
            logger.debug(f"Retrieved {len(trades)} trades for {self.wallet_name}")
            return trades
            
        except Exception as e:
            logger.error(f"Error getting trade history for {self.wallet_name}: {e}")
            return []
