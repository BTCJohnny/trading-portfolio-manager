# src/portfolio_manager/__init__.py
"""
Trading Portfolio Manager - Main Package
"""

__version__ = "1.0.0"
__author__ = "Trading Portfolio Manager"

# Import main classes for easier access
try:
    from .core.portfolio_manager import PortfolioManager
    from .core.dashboard import PortfolioDashboard
    from .core.wallet_manager import WalletManager
    from .connectors.bot_connector import BotConnector
    from .connectors.sheets_connector import SheetsConnector
    from .utils.logger import setup_logger
    from .utils.helpers import load_config, validate_config, ensure_credentials_exist
    
    __all__ = [
        'PortfolioManager',
        'PortfolioDashboard', 
        'WalletManager',
        'BotConnector',
        'SheetsConnector',
        'setup_logger',
        'load_config',
        'validate_config',
        'ensure_credentials_exist'
    ]
except ImportError:
    # Handle import errors gracefully during development
    pass
