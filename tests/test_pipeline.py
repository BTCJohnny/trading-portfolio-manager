# tests/test_pipeline.py
#!/usr/bin/env python3
"""
Test script to verify all pipeline connections and imports work correctly.
This test runs WITHOUT requiring Google Sheets credentials.
"""
import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """Test that all imports work correctly."""
    print("Testing imports...")
    
    try:
        # Test logger import
        from portfolio_manager.utils.logger import setup_logger
        print("✓ Logger import successful")
        
        # Test helpers import
        from portfolio_manager.utils.helpers import load_config, validate_config, ensure_credentials_exist
        print("✓ Helpers import successful")
        
        # Test sheets connector import
        from portfolio_manager.connectors.sheets_connector import SheetsConnector
        print("✓ Sheets connector import successful")
        
        # Test dashboard import
        from portfolio_manager.core.dashboard import PortfolioDashboard
        print("✓ Dashboard import successful")
        
        # Test wallet manager import
        from portfolio_manager.core.wallet_manager import WalletManager
        print("✓ Wallet manager import successful")
        
        # Test portfolio manager import (this will fail without config, but import should work)
        from portfolio_manager.core.portfolio_manager import PortfolioManager
        print("✓ Portfolio manager import successful")
        
        # Test bot connector import
        from portfolio_manager.connectors.bot_connector import BotConnector
        print("✓ Bot connector import successful")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error during import: {e}")
        return False

def test_logger():
    """Test logger functionality."""
    print("\nTesting logger...")
    
    try:
        from portfolio_manager.utils.logger import setup_logger
        
        # Create test logger
        logger = setup_logger("test_logger", "DEBUG")
        
        # Test different log levels
        logger.debug("Debug message test")
        logger.info("Info message test")
        logger.warning("Warning message test")
        
        print("✓ Logger functionality works")
        return True
        
    except Exception as e:
        print(f"✗ Logger test failed: {e}")
        return False

def test_config_helpers():
    """Test configuration helper functions."""
    print("\nTesting config helpers...")
    
    try:
        from portfolio_manager.utils.helpers import validate_config, ensure_credentials_exist
        
        # Test config validation with valid config
        valid_config = {
            'spreadsheet_url': 'https://example.com',
            'credentials_path': '/fake/path',
            'wallets': {'test_wallet': {}}
        }
        
        result = validate_config(valid_config)
        if result:
            print("✓ Config validation works with valid config")
        
        # Test config validation with invalid config
        try:
            invalid_config = {'missing_keys': True}
            validate_config(invalid_config)
            print("✗ Config validation should have failed")
            return False
        except ValueError:
            print("✓ Config validation correctly rejects invalid config")
        
        # Test credentials check with non-existent file
        creds_exist = ensure_credentials_exist('/fake/nonexistent/path')
        if not creds_exist:
            print("✓ Credentials check correctly identifies missing file")
        
        return True
        
    except Exception as e:
        print(f"✗ Config helpers test failed: {e}")
        return False

def test_class_instantiation():
    """Test that classes can be instantiated without Google Sheets connection."""
    print("\nTesting class instantiation (without Google Sheets)...")
    
    try:
        from portfolio_manager.connectors.bot_connector import BotConnector
        
        # Create a mock portfolio manager
        class MockPortfolioManager:
            def add_wallet(self, wallet_name):
                return f"Mock wallet: {wallet_name}"
        
        mock_pm = MockPortfolioManager()
        
        # Test bot connector instantiation
        bot_connector = BotConnector(mock_pm)
        print("✓ BotConnector instantiation successful")
        
        # Test bot registration
        bot_connector.register_bot("test_bot", "test_wallet")
        print("✓ Bot registration successful")
        
        # Test bot simulation
        trade_data = bot_connector.simulate_bot_trade("test_bot")
        if trade_data:
            print("✓ Trade simulation successful")
            print(f"   Sample trade: {trade_data['action']} {trade_data['asset']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Class instantiation test failed: {e}")
        return False

def test_directory_structure():
    """Test that all required directories exist."""
    print("\nTesting directory structure...")
    
    required_dirs = [
        "src/portfolio_manager",
        "src/portfolio_manager/core",
        "src/portfolio_manager/connectors", 
        "src/portfolio_manager/utils",
        "config",
        "logs",
        "tests",
        "scripts"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        full_path = Path(__file__).parent.parent / dir_path
        if not full_path.exists():
            missing_dirs.append(dir_path)
        else:
            print(f"✓ {dir_path} exists")
    
    if missing_dirs:
        print(f"✗ Missing directories: {missing_dirs}")
        return False
    
    return True

def test_required_files():
    """Test that all required files exist."""
    print("\nTesting required files...")
    
    required_files = [
        "src/portfolio_manager/__init__.py",
        "src/portfolio_manager/core/__init__.py",
        "src/portfolio_manager/connectors/__init__.py",
        "src/portfolio_manager/utils/__init__.py",
        "src/portfolio_manager/utils/logger.py",
        "src/portfolio_manager/utils/helpers.py",
        "src/portfolio_manager/connectors/sheets_connector.py",
        "src/portfolio_manager/core/dashboard.py",
        "src/portfolio_manager/core/wallet_manager.py",
        "src/portfolio_manager/core/portfolio_manager.py",
        "src/portfolio_manager/connectors/bot_connector.py",
        "scripts/setup_portfolio.py",
        "scripts/run_updates.py",
        "config/config.example.json",
        "requirements.txt"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = Path(__file__).parent.parent / file_path
        if not full_path.exists():
            missing_files.append(file_path)
        else:
            print(f"✓ {file_path} exists")
    
    if missing_files:
        print(f"✗ Missing files: {missing_files}")
        return False
    
    return True

def test_example_config():
    """Test that example config file is valid JSON."""
    print("\nTesting example config file...")
    
    try:
        import json
        
        config_path = Path(__file__).parent.parent / "config" / "config.example.json"
        
        if not config_path.exists():
            print("✗ config.example.json not found")
            return False
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print("✓ config.example.json is valid JSON")
        
        # Check required keys
        required_keys = ['spreadsheet_url', 'credentials_path', 'wallets']
        for key in required_keys:
            if key in config:
                print(f"✓ Required key '{key}' found in config")
            else:
                print(f"✗ Required key '{key}' missing from config")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Example config test failed: {e}")
        return False

def main():
    """Main test function."""
    print("=" * 60)
    print("TRADING PORTFOLIO MANAGER - PIPELINE TEST")
    print("=" * 60)
    print("This test verifies all files are connected properly")
    print("WITHOUT requiring Google Sheets credentials.")
    print("=" * 60)
    
    tests = [
        ("Directory Structure", test_directory_structure),
        ("Required Files", test_required_files),
        ("Example Config", test_example_config),
        ("Imports", test_imports),
        ("Logger", test_logger),
        ("Config Helpers", test_config_helpers),
        ("Class Instantiation", test_class_instantiation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'-' * 40}")
        print(f"Running: {test_name}")
        print(f"{'-' * 40}")
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("Your pipeline is properly connected.")
        print("\nNext steps:")
        print("1. Set up Google Sheets API credentials")
        print("2. Configure config/config.json")
        print("3. Run: python scripts/setup_portfolio.py")
    else:
        print(f"\n❌ {total - passed} tests failed.")
        print("Please fix the issues above before proceeding.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
