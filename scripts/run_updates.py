# scripts/run_updates.py
#!/usr/bin/env python3
"""
Script for running portfolio updates and testing bot connections.
"""
import sys
import time
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from portfolio_manager.core.portfolio_manager import PortfolioManager
from portfolio_manager.connectors.bot_connector import BotConnector
from portfolio_manager.utils.logger import setup_logger

logger = setup_logger(__name__)

def add_sample_trades(portfolio: PortfolioManager) -> None:
    """Add sample trades for testing."""
    print("Adding sample trades...")
    
    sample_trades = [
        {
            'wallet': 'Wallet_Arbitrage',
            'trade': {
                'date': '2024-06-15',
                'action': 'BUY',
                'asset': 'BTC',
                'quantity': 0.5,
                'price': 67000,
                'notes': 'Initial BTC position'
            }
        },
        {
            'wallet': 'Wallet_DCA',
            'trade': {
                'date': '2024-06-16',
                'action': 'BUY',
                'asset': 'ETH',
                'quantity': 5,
                'price': 3500,
                'notes': 'DCA ETH purchase'
            }
        },
        {
            'wallet': 'Wallet_Grid',
            'trade': {
                'date': '2024-06-17',
                'action': 'BUY',
                'asset': 'SOL',
                'quantity': 100,
                'price': 150,
                'notes': 'Grid bot SOL entry'
            }
        }
    ]
    
    for trade_info in sample_trades:
        success = portfolio.add_trade(trade_info['wallet'], trade_info['trade'])
        if success:
            print(f"✓ Added trade: {trade_info['trade']['action']} {trade_info['trade']['asset']}")
        else:
            print(f"✗ Failed to add trade to {trade_info['wallet']}")

def test_bot_connector(portfolio: PortfolioManager) -> None:
    """Test bot connector functionality."""
    print("\nTesting bot connector...")
    
    # Initialize bot connector
    bot_connector = BotConnector(portfolio)
    
    # Register test bots
    bots = [
        ('TestBot_Arbitrage', 'Wallet_Arbitrage'),
        ('TestBot_DCA', 'Wallet_DCA'),
        ('TestBot_Grid', 'Wallet_Grid')
    ]
    
    for bot_name, wallet_name in bots:
        bot_connector.register_bot(bot_name, wallet_name)
        print(f"✓ Registered bot: {bot_name}")
    
    # Simulate bot updates
    print("\nSimulating bot trades...")
    results = bot_connector.update_all_bots()
    
    for bot_name, success in results.items():
        status = "✓" if success else "✗"
        print(f"{status} {bot_name}: {'Success' if success else 'Failed'}")

def main():
    """Main execution function."""
    print("=" * 60)
    print("TRADING PORTFOLIO MANAGER - UPDATE TEST")
    print("=" * 60)
    
    try:
        # Initialize portfolio manager
        print("\n1. Initializing portfolio manager...")
        portfolio = PortfolioManager()
        
        # Add sample trades
        print("\n2. Adding sample trades...")
        add_sample_trades(portfolio)
        
        # Test bot connector
        print("\n3. Testing bot connector...")
        test_bot_connector(portfolio)
        
        # Update dashboard
        print("\n4. Updating portfolio dashboard...")
        success = portfolio.update_dashboard()
        if success:
            print("✓ Dashboard updated successfully")
        else:
            print("✗ Dashboard update failed")
        
        # Display portfolio summary
        print("\n5. Portfolio Summary:")
        print("-" * 40)
        summary = portfolio.get_portfolio_summary()
        
        print(f"Total Portfolio Value: ${summary.get('total_portfolio_value', 0):,.2f}")
        print(f"Total Invested: ${summary.get('total_invested', 0):,.2f}")
        print(f"Total Return: ${summary.get('total_return', 0):,.2f}")
        print(f"Total Return %: {summary.get('total_return_pct', 0):.2f}%")
        print(f"Number of Wallets: {summary.get('num_wallets', 0)}")
        
        print("\nWallet Performance:")
        for wallet in summary.get('wallets', []):
            print(f"  {wallet['name']}: ${wallet['current_value']:,.2f} "
                  f"({wallet['total_return_pct']:.2f}%)")
        
        print("\n" + "=" * 60)
        print("UPDATE TEST COMPLETED!")
        print("=" * 60)
        print("\nCheck your Google Sheets to see the updates.")
        
    except Exception as e:
        logger.error(f"Update test failed: {e}")
        print(f"\nERROR: Update test failed - {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
