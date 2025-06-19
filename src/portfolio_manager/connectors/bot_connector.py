# src/portfolio_manager/connectors/bot_connector.py
"""
Trading bot connector for automated trade updates.
"""
import time
import random
from datetime import datetime
from typing import Dict, Any, Optional, List
import requests
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class BotConnector:
    """Connector for integrating with trading bots."""
    
    def __init__(self, portfolio_manager):
        """
        Initialize bot connector.
        
        Args:
            portfolio_manager: PortfolioManager instance
        """
        self.portfolio_manager = portfolio_manager
        self.registered_bots: Dict[str, Dict[str, Any]] = {}
        logger.info("Bot connector initialized")
    
    def register_bot(self, bot_name: str, wallet_name: str, 
                    api_endpoint: Optional[str] = None, 
                    api_key: Optional[str] = None) -> None:
        """
        Register a trading bot with the portfolio.
        
        Args:
            bot_name: Unique bot identifier
            wallet_name: Associated wallet name
            api_endpoint: Bot's API endpoint (optional)
            api_key: API key for bot authentication (optional)
        """
        self.registered_bots[bot_name] = {
            'wallet_name': wallet_name,
            'api_endpoint': api_endpoint,
            'api_key': api_key,
            'last_update': None,
            'status': 'registered'
        }
        
        # Ensure wallet exists
        self.portfolio_manager.add_wallet(wallet_name)
        
        logger.info(f"Registered bot '{bot_name}' with wallet '{wallet_name}'")
    
    def simulate_bot_trade(self, bot_name: str) -> Optional[Dict[str, Any]]:
        """
        Simulate trade data for testing purposes.
        
        Args:
            bot_name: Name of the bot
        
        Returns:
            Simulated trade data or None
        """
        if bot_name not in self.registered_bots:
            logger.error(f"Bot '{bot_name}' not registered")
            return None
        
        # Simulate realistic trading data
        assets = ['BTC', 'ETH', 'SOL', 'MATIC', 'LINK', 'AVAX', 'DOT', 'ADA']
        actions = ['BUY', 'SELL']
        
        trade_data = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'action': random.choice(actions),
            'asset': random.choice(assets),
            'quantity': round(random.uniform(0.01, 10), 4),
            'price': round(random.uniform(50, 5000), 2),
            'notes': f'Simulated trade from {bot_name}'
        }
        
        # Calculate total value
        trade_data['total_value'] = trade_data['quantity'] * trade_data['price']
        
        logger.debug(f"Simulated trade for {bot_name}: {trade_data}")
        return trade_data
    
    def fetch_bot_trades(self, bot_name: str) -> List[Dict[str, Any]]:
        """
        Fetch trades from a bot's API endpoint.
        
        Args:
            bot_name: Name of the bot
        
        Returns:
            List of trade data dictionaries
        """
        if bot_name not in self.registered_bots:
            logger.error(f"Bot '{bot_name}' not registered")
            return []
        
        bot_config = self.registered_bots[bot_name]
        api_endpoint = bot_config.get('api_endpoint')
        
        if not api_endpoint:
            logger.warning(f"No API endpoint configured for bot '{bot_name}', using simulation")
            simulated_trade = self.simulate_bot_trade(bot_name)
            return [simulated_trade] if simulated_trade else []
        
        try:
            # Prepare headers
            headers = {'Content-Type': 'application/json'}
            if bot_config.get('api_key'):
                headers['Authorization'] = f"Bearer {bot_config['api_key']}"
            
            # Make API request
            response = requests.get(
                api_endpoint,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            trades_data = response.json()
            
            # Validate and format trades data
            if isinstance(trades_data, list):
                validated_trades = []
                for trade in trades_data:
                    if self._validate_trade_data(trade):
                        validated_trades.append(trade)
                    else:
                        logger.warning(f"Invalid trade data from {bot_name}: {trade}")
                
                logger.info(f"Fetched {len(validated_trades)} trades from {bot_name}")
                return validated_trades
            else:
                logger.error(f"Unexpected response format from {bot_name}: {type(trades_data)}")
                return []
                
        except requests.RequestException as e:
            logger.error(f"Failed to fetch trades from {bot_name}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching trades from {bot_name}: {e}")
            return []
    
    def _validate_trade_data(self, trade_data: Dict[str, Any]) -> bool:
        """
        Validate trade data structure.
        
        Args:
            trade_data: Trade data dictionary
        
        Returns:
            True if valid
        """
        required_fields = ['action', 'asset', 'quantity', 'price']
        
        for field in required_fields:
            if field not in trade_data:
                return False
        
        # Validate data types
        try:
            float(trade_data['quantity'])
            float(trade_data['price'])
            
            if trade_data['action'].upper() not in ['BUY', 'SELL']:
                return False
                
        except (ValueError, TypeError):
            return False
        
        return True
    
    def process_bot_trades(self, bot_name: str) -> bool:
        """
        Process trades from a specific bot.
        
        Args:
            bot_name: Name of the bot
        
        Returns:
            True if successful
        """
        if bot_name not in self.registered_bots:
            logger.error(f"Bot '{bot_name}' not registered")
            return False
        
        try:
            wallet_name = self.registered_bots[bot_name]['wallet_name']
            trades = self.fetch_bot_trades(bot_name)
            
            success_count = 0
            for trade_data in trades:
                success = self.portfolio_manager.add_trade(wallet_name, trade_data)
                if success:
                    success_count += 1
            
            # Update bot status
            self.registered_bots[bot_name]['last_update'] = datetime.now().isoformat()
            self.registered_bots[bot_name]['status'] = 'active'
            
            logger.info(f"Processed {success_count}/{len(trades)} trades for {bot_name}")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error processing trades for {bot_name}: {e}")
            self.registered_bots[bot_name]['status'] = 'error'
            return False
    
    def update_all_bots(self) -> Dict[str, bool]:
        """
        Update trades from all registered bots.
        
        Returns:
            Dictionary mapping bot names to success status
        """
        logger.info("Updating all registered bots...")
        
        results = {}
        for bot_name in self.registered_bots.keys():
            try:
                success = self.process_bot_trades(bot_name)
                results[bot_name] = success
                
                # Small delay to prevent rate limiting
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error updating bot {bot_name}: {e}")
                results[bot_name] = False
        
        successful_updates = sum(results.values())
        logger.info(f"Updated {successful_updates}/{len(results)} bots successfully")
        
        return results
    
    def get_bot_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status of all registered bots.
        
        Returns:
            Dictionary with bot status information
        """
        return self.registered_bots.copy()
