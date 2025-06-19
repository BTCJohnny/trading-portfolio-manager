# src/portfolio_manager/core/dashboard.py
"""
Portfolio dashboard management for Google Sheets.
"""
from datetime import datetime
from typing import List, Dict, Any
import gspread
from ..connectors.sheets_connector import SheetsConnector
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class PortfolioDashboard:
    """Manages the main portfolio dashboard sheet."""
    
    def __init__(self, sheets_connector: SheetsConnector):
        """
        Initialize dashboard manager.
        
        Args:
            sheets_connector: Connected SheetsConnector instance
        """
        self.connector = sheets_connector
        self.worksheet = None
        logger.info("Portfolio dashboard manager initialized")
    
    def create_dashboard_sheet(self) -> gspread.Worksheet:
        """
        Create or update the main dashboard sheet.
        
        Returns:
            Dashboard worksheet
        """
        logger.info("Creating/updating portfolio dashboard sheet")
        
        self.worksheet = self.connector.get_or_create_worksheet("Portfolio Dashboard")
        
        # Clear existing content
        self.worksheet.clear()
        
        # Set up headers and structure
        headers = [
            ["TRADING PORTFOLIO DASHBOARD", "", "", "", "", "", "", ""],
            ["Last Updated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["PORTFOLIO SUMMARY", "", "", "", "WALLET PERFORMANCE", "", "", ""],
            ["Total Portfolio Value:", "=SUM(F8:F50)", "", "", "Wallet Name", "Current Value", "Total Return %", "APY %"],
            ["Total Invested:", "=SUM(E8:E50)", "", "", "", "", "", ""],
            ["Total P&L:", "=B5-B6", "", "", "", "", "", ""],
            ["Overall Return %:", "=IF(B6>0,(B7/B6)*100,0)", "", "", "", "", "", ""],
        ]
        
        # Update headers
        for i, row in enumerate(headers):
            range_name = f'A{i+1}:H{i+1}'
            self.connector.update_range(self.worksheet, range_name, [row])
        
        # Apply formatting
        self._format_dashboard()
        
        logger.info("Dashboard sheet created successfully")
        return self.worksheet
    
    def _format_dashboard(self) -> None:
        """Apply formatting to the dashboard."""
        try:
            # Title formatting
            self.worksheet.format('A1:H1', {
                'backgroundColor': {'red': 0.2, 'green': 0.2, 'blue': 0.8},
                'textFormat': {
                    'foregroundColor': {'red': 1, 'green': 1, 'blue': 1},
                    'bold': True,
                    'fontSize': 14
                },
                'horizontalAlignment': 'CENTER'
            })
            
            # Section headers
            self.worksheet.format('A4:D4', {
                'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9},
                'textFormat': {'bold': True}
            })
            
            self.worksheet.format('E4:H4', {
                'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9},
                'textFormat': {'bold': True}
            })
            
            # Performance table headers
            self.worksheet.format('E5:H5', {
                'backgroundColor': {'red': 0.8, 'green': 0.8, 'blue': 0.8},
                'textFormat': {'bold': True}
            })
            
            logger.debug("Dashboard formatting applied")
            
        except Exception as e:
            logger.warning(f"Could not apply dashboard formatting: {e}")
    
    def update_wallet_summary(self, wallet_data: List[Dict[str, Any]]) -> bool:
        """
        Update the wallet performance summary table.
        
        Args:
            wallet_data: List of wallet performance dictionaries
        
        Returns:
            True if successful
        """
        try:
            start_row = 8
            
            for i, wallet in enumerate(wallet_data):
                row_num = start_row + i
                values = [
                    wallet.get('name', ''),
                    wallet.get('current_value', 0),
                    wallet.get('total_return_pct', 0),
                    wallet.get('apy', 0)
                ]
                
                range_name = f'E{row_num}:H{row_num}'
                self.connector.update_range(self.worksheet, range_name, [values])
            
            # Update timestamp
            timestamp_range = 'B2'
            timestamp_value = [[datetime.now().strftime("%Y-%m-%d %H:%M:%S")]]
            self.connector.update_range(self.worksheet, timestamp_range, timestamp_value)
            
            logger.info(f"Updated wallet summary with {len(wallet_data)} wallets")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update wallet summary: {e}")
            return False
    
    def create_portfolio_pie_chart_instructions(self) -> str:
        """
        Return instructions for creating pie chart in Google Sheets.
        
        Returns:
            Instructions string
        """
        instructions = """
        PIE CHART CREATION INSTRUCTIONS:
        1. Select data range E8:F50 (Wallet Name and Current Value columns)
        2. Go to Insert > Chart
        3. Choose Pie Chart from chart types
        4. Position chart in area J1:P15
        5. Customize title: "Portfolio Allocation"
        6. Enable data labels to show percentages
        """
        logger.info("Pie chart instructions generated")
        return instructions
