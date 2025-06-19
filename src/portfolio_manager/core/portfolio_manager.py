# src/portfolio_manager/core/portfolio_manager.py
"""
Main portfolio manager orchestrating all components.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from ..connectors.sheets_connector import SheetsConnector
from .dashboard import PortfolioDashboard
from .wallet_manager import WalletManager
from ..utils.logger import setup_logger
from ..utils.helpers import load_config, validate_config, ensure_credentials_exist

logger = setup_logger(__name__)

class PortfolioManager:
    """
    Main portfolio manager class that orchestrates all components.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize portfolio manager.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path)
        validate_config(self.config)
        
        # Ensure credentials exist
        if not ensure_credentials_exist(self.config['credentials_path']):
            raise FileNotFoundError(f"Credentials file not found: {self.config['credentials_path']}")
        
        # Initialize connections
        self.sheets_connector = SheetsConnector(
            self.config['credentials_path'],
            self.config['spreadsheet_url']
        )
        
        # Initialize components
        self.dashboard = PortfolioDashboard(self.sheets_connector)
        self.wallet_managers: Dict[str, WalletManager] = {}
        
        logger.info("Portfolio manager initialized successfully")
    
    def setup_portfolio(self) -> None:
        """Set up the complete portfolio structure."""
        logger.info("Setting up portfolio structure...")
        
        # Create dashboard
        self.dashboard.create_dashboard_sheet()
        
        # Create wallet sheets
        for wallet_name in self.config['wallets'].keys():
            self.add_wallet(wallet_name)
        
        # Initial dashboard update
        self.update_dashboard()
        
        logger.info("Portfolio setup completed")
    
    def add_wallet(self, wallet_name: str) -> WalletManager:
        """
        Add a new wallet to the portfolio.
        
        Args:
            wallet_name: Name of the wallet
        
        Returns:
            WalletManager instance
        """
        if wallet_name not in self.wallet_managers:
            self.wallet_managers[wallet_name] = WalletManager(
                self.sheets_connector, 
                wallet_name
            )
            logger.info(f"Added wallet: {wallet_name}")
        
        return self.wallet_managers[wallet_name]
    
    def get_wallet_manager(self, wallet_name: str) -> Optional[WalletManager]:
        """
        Get wallet manager for a specific wallet.
        
        Args:
            wallet_name: Name of the wallet
        
        Returns:
            WalletManager instance or None
        """
        return self.wallet_managers.get(wallet_name)
    
    def add_trade(self, wallet_name: str, trade_data: Dict[str, Any]) -> bool:
        """
        Add a trade to a specific wallet.
        
        Args:
            wallet_name: Target wallet name
            trade_data: Trade information dictionary
        
        Returns:
            True if successful
        """
        wallet_manager = self.get_wallet_manager(wallet_name)
        if not wallet_manager:
            logger.error(f"Wallet not found: {wallet_name}")
            return False
        
        success = wallet_manager.add_trade(trade_data)
        if success:
            logger.info(f"Trade added to {wallet_name}: {trade_data.get('action')} {trade_data.get('asset')}")
        
        return success
    
    def update_dashboard(self) -> bool:
        """
        Update the portfolio dashboard with current data.
        
        Returns:
            True if successful
        """
        try:
            logger.info("Updating portfolio dashboard...")
            
            # Collect performance data from all wallets
            wallet_data = []
            for wallet_name, manager in self.wallet_managers.items():
                performance = manager.get_wallet_performance()
                wallet_data.append(performance)
            
            # Update dashboard
            success = self.dashboard.update_wallet_summary(wallet_data)
            
            if success:
                logger.info("Portfolio dashboard updated successfully")
            else:
                logger.error("Failed to update portfolio dashboard")
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating dashboard: {e}")
            return False
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive portfolio summary.
        
        Returns:
            Portfolio summary dictionary
        """
        try:
            total_value = 0
            total_invested = 0
            wallet_summaries = []
            
            for wallet_name, manager in self.wallet_managers.items():
                performance = manager.get_wallet_performance()
                wallet_summaries.append(performance)
                
                total_value += performance['current_value']
                total_invested += performance['initial_investment']
            
            total_return = total_value - total_invested
            total_return_pct = 0
            if total_invested > 0:
                total_return_pct = (total_return / total_invested) * 100
            
            summary = {
                'timestamp': datetime.now().isoformat(),
                'total_portfolio_value': total_value,
                'total_invested': total_invested,
                'total_return': total_return,
                'total_return_pct': total_return_pct,
                'num_wallets': len(self.wallet_managers),
                'wallets': wallet_summaries
            }
            
            logger.debug(f"Portfolio summary generated: {summary}")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating portfolio summary: {e}")
            return {}
    
    def run_update_cycle(self) -> bool:
        """
        Run a complete update cycle for the portfolio.
        
        Returns:
            True if successful
        """
        logger.info("Starting portfolio update cycle...")
        
        try:
            # Update dashboard with latest data
            success = self.update_dashboard()
            
            if success:
                logger.info("Portfolio update cycle completed successfully")
            else:
                logger.error("Portfolio update cycle failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Error in update cycle: {e}")
            return False
