# scripts/setup_portfolio.py
#!/usr/bin/env python3
"""
Setup script for initializing the trading portfolio manager.
"""
import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from portfolio_manager.core.portfolio_manager import PortfolioManager
from portfolio_manager.utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    """Main setup function."""
    print("=" * 60)
    print("TRADING PORTFOLIO MANAGER - SETUP")
    print("=" * 60)
    
    try:
        # Initialize portfolio manager
        print("\n1. Initializing portfolio manager...")
        portfolio = PortfolioManager()
        
        # Set up portfolio structure
        print("2. Setting up portfolio structure...")
        portfolio.setup_portfolio()
        
        # Display setup completion info
        print("\n" + "=" * 60)
        print("SETUP COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
        print("\nNext steps:")
        print("1. Open your Google Sheets document")
        print("2. Review the Portfolio Dashboard sheet")
        print("3. Check individual wallet sheets")
        print("4. Create pie chart manually (see dashboard instructions)")
        print("5. Run 'python scripts/run_updates.py' to test updates")
        
        # Display portfolio summary
        summary = portfolio.get_portfolio_summary()
        print(f"\nPortfolio created with {summary.get('num_wallets', 0)} wallets:")
        for wallet in summary.get('wallets', []):
            print(f"  - {wallet['name']}")
        
        print(f"\nSpreadsheet URL: {portfolio.config['spreadsheet_url']}")
        
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        print(f"\nERROR: Setup failed - {e}")
        print("Please check your configuration and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
