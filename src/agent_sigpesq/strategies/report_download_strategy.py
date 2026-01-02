from abc import ABC, abstractmethod

class ReportDownloadStrategy(ABC):
    """
    Abstract base class for report download strategies.
    """
    
    @abstractmethod
    def get_category_name(self) -> str:
        """Returns the name of the report category."""
        pass
        
    @abstractmethod
    def get_button_id(self) -> str:
        """Returns the ID of the button to initiate download/generation."""
        pass
        
    @abstractmethod
    def download(self, driver, reports_dir: str) -> bool:
        """
        Executes the download process for this specific strategy.
        Returns True if successful, False otherwise.
        """
        pass
