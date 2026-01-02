"""
Strategy implementation for downloading Research Projects reports.
"""

from .report_download_strategy import BaseSeleniumStrategy
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ProjectsDownloadStrategy(BaseSeleniumStrategy):
    """
    Strategy for downloading reports related to Research Projects.
    """

    def get_category_name(self) -> str:
        """Returns the category name 'Research Projects'."""
        return "Research Projects"
        
    def get_button_id(self) -> str:
        """Returns the button ID for Research Projects."""
        return "ContentPlaceHolder_btnRel_Projetos"
        
    def download(self, driver, reports_dir: str) -> bool:
        """
        Executes the download simulation for Research Projects.
        """
        print(f"Processing {self.get_category_name()}...")
        
        try:
            # 1. Prepare target subdirectory
            reports_subdir = os.path.join(reports_dir, "research_projects")
            
            wait = WebDriverWait(driver, 20)
            button_id = self.get_button_id()
            
            # 2. Ensure accordion is open
            self._ensure_accordion_open(wait, button_id, "Projetos de Pesquisa")
            
            # 3. Click the download button
            print(f"Clicking button {button_id}...")
            btn = wait.until(EC.element_to_be_clickable((By.ID, button_id)))
            btn.click()
            
            # 4. Wait for download and move file
            return self._wait_and_move_file(reports_dir, reports_subdir)
            
        except Exception as e:
            print(f"Error downloading {self.get_category_name()}: {e}")
            return False
