# src/portfolio_manager/utils/helpers.py
"""
Helper utilities for the trading portfolio manager.
"""
import json
import os
from pathlib import Path
from typing import Dict, Any
from .logger import setup_logger

logger = setup_logger(__name__)

def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load configuration from JSON file.
    
    Args:
        config_path: Path to config file (defaults to config/config.json)
    
    Returns:
        Configuration dictionary
    """
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent.parent / "config" / "config.json"
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in configuration file: {e}")
        raise

def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate configuration dictionary.
    
    Args:
        config: Configuration dictionary
    
    Returns:
        True if valid, raises exception if invalid
    """
    required_keys = ['spreadsheet_url', 'credentials_path', 'wallets']
    
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required configuration key: {key}")
    
    if not config['wallets']:
        raise ValueError("At least one wallet must be configured")
    
    logger.info("Configuration validation passed")
    return True

def ensure_credentials_exist(credentials_path: str) -> bool:
    """
    Check if Google Sheets credentials file exists.
    
    Args:
        credentials_path: Path to credentials file
    
    Returns:
        True if file exists
    """
    if not os.path.exists(credentials_path):
        logger.error(f"Credentials file not found: {credentials_path}")
        return False
    
    logger.info(f"Credentials file found: {credentials_path}")
    return True
