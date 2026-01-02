"""
Strategy implementation for downloading Research Projects reports.
"""

from .report_download_strategy import ReportDownloadStrategy

class ProjectsDownloadStrategy(ReportDownloadStrategy):
    """
    Strategy for downloading reports related to Research Projects.
    """

    def get_category_name(self) -> str:
        """Returns the category name 'Research Projects'."""
        return "Research Projects"
        
    def get_button_id(self) -> str:
        """Returns the button ID for Research Projects."""
        return "btnEmitirProjetos"
        
    def download(self, driver, reports_dir: str) -> bool:
        """
        Executes the download simulation for Research Projects.

        Args:
            driver: The Selenium WebDriver instance.
            reports_dir (str): The target directory for the report.

        Returns:
            bool: Always True (simulation).
        """
        print(f"Processing {self.get_category_name()}...")
        return True
