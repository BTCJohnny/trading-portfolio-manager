# src/portfolio_manager/connectors/sheets_connector.py
"""
Google Sheets connector for the trading portfolio manager.
"""
import gspread
from google.oauth2.service_account import Credentials
from typing import Optional, List, Dict, Any
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class SheetsConnector:
    """Google Sheets API connector with error handling and logging."""
    
    def __init__(self, credentials_path: str, spreadsheet_url: str):
        """
        Initialize Google Sheets connector.
        
        Args:
            credentials_path: Path to service account credentials JSON
            spreadsheet_url: URL of the Google Spreadsheet
        """
        self.credentials_path = credentials_path
        self.spreadsheet_url = spreadsheet_url
        self.gc = None
        self.spreadsheet = None
        self._connect()
    
    def _connect(self) -> None:
        """Establish connection to Google Sheets."""
        try:
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            creds = Credentials.from_service_account_file(
                self.credentials_path, 
                scopes=scope
            )
            self.gc = gspread.authorize(creds)
            self.spreadsheet = self.gc.open_by_url(self.spreadsheet_url)
            
            logger.info(f"Connected to Google Sheets: {self.spreadsheet.title}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Google Sheets: {e}")
            raise
    
    def get_or_create_worksheet(self, title: str, rows: int = 1000, cols: int = 20) -> gspread.Worksheet:
        """
        Get existing worksheet or create new one.
        
        Args:
            title: Worksheet title
            rows: Number of rows (for new sheets)
            cols: Number of columns (for new sheets)
        
        Returns:
            Worksheet object
        """
        try:
            worksheet = self.spreadsheet.worksheet(title)
            logger.info(f"Found existing worksheet: {title}")
            return worksheet
        except gspread.WorksheetNotFound:
            logger.info(f"Creating new worksheet: {title}")
            worksheet = self.spreadsheet.add_worksheet(title=title, rows=rows, cols=cols)
            return worksheet
        except Exception as e:
            logger.error(f"Error accessing worksheet {title}: {e}")
            raise
    
    def update_range(self, worksheet: gspread.Worksheet, range_name: str, values: List[List]) -> bool:
        """
        Update a range of cells in the worksheet.
        
        Args:
            worksheet: Target worksheet
            range_name: Range to update (e.g., 'A1:C3')
            values: 2D list of values
        
        Returns:
            True if successful
        """
        try:
            worksheet.update(range_name, values)
            logger.debug(f"Updated range {range_name} in {worksheet.title}")
            return True
        except Exception as e:
            logger.error(f"Failed to update range {range_name}: {e}")
            return False
    
    def append_row(self, worksheet: gspread.Worksheet, values: List) -> bool:
        """
        Append a row to the worksheet.
        
        Args:
            worksheet: Target worksheet
            values: List of values to append
        
        Returns:
            True if successful
        """
        try:
            worksheet.append_row(values)
            logger.debug(f"Appended row to {worksheet.title}")
            return True
        except Exception as e:
            logger.error(f"Failed to append row: {e}")
            return False
