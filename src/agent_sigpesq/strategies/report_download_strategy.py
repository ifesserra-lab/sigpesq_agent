"""
Module defining the abstract strategy for report downloads.

This module provides the interface `ReportDownloadStrategy` that all specific
report category strategies must implement.
"""

from abc import ABC, abstractmethod

class ReportDownloadStrategy(ABC):
    """
    Abstract base class for report download strategies.
    
    This class defines the methods required to implement a download strategy
    for a specific category of reports on the Sigpesq portal.
    """
    
    @abstractmethod
    def get_category_name(self) -> str:
        """
        Returns the human-readable name of the report category.

        Returns:
            str: The name of the category (e.g., "Research Groups").
        """
        pass
        
    @abstractmethod
    def get_button_id(self) -> str:
        """
        Returns the ID of the HTML button to initiate the report generation/download.

        Returns:
            str: The DOM ID of the button.
        """
        pass
        
    @abstractmethod
    def download(self, driver, reports_dir: str) -> bool:
        """
        Executes the download process for this specific strategy.

        Args:
            driver: The Selenium WebDriver instance.
            reports_dir (str): The absolute path to the directory where reports should be saved.

        Returns:
            bool: True if the download (or simulation) was successful, False otherwise.
        """
        pass
