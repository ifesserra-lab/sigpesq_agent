"""
Strategy implementation for downloading Research Projects reports.
"""

from .report_download_strategy import ReportDownloadStrategy
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ProjectsDownloadStrategy(ReportDownloadStrategy):
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

        Args:
            driver: The Selenium WebDriver instance.
            reports_dir (str): The target directory for the report.

        Returns:
            bool: Always True (simulation).
        """
        print(f"Processing {self.get_category_name()}...")
        
        try:
            # 1. Prepare target subdirectory
            # User wants: reports/research_projects
            reports_subdir = os.path.join(reports_dir, "research_projects")
            if not os.path.exists(reports_subdir):
                os.makedirs(reports_subdir)

            wait = WebDriverWait(driver, 20)
            button_id = self.get_button_id()
            
            # 2. Ensure accordion is open
            try:
                # Check if button is visible
                wait.until(EC.visibility_of_element_located((By.ID, button_id)))
            except:
                print("Button not visible, attempting to open accordion...")
                # Find header containing "Projetos de Pesquisa"
                xpath = "//div[contains(@class, 'accordionHeader') and contains(., 'Projetos de Pesquisa')]"
                header = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                header.click()
                time.sleep(1) # Wait for animation
            
            # 3. Click the download button
            print(f"Clicking button {button_id}...")
            btn = wait.until(EC.element_to_be_clickable((By.ID, button_id)))
            btn.click()
            
            # 4. Wait for download and move file
            print("Waiting for download to complete...")
            max_wait = 60
            start_time = time.time()
            initial_files = set(os.listdir(reports_dir))
            
            while time.time() - start_time < max_wait:
                current_files = set(os.listdir(reports_dir))
                new_files = current_files - initial_files
                
                # Check for crdownload/tmp files
                if any(f.endswith('.crdownload') or f.endswith('.tmp') for f in new_files):
                    time.sleep(1)
                    continue
                    
                if new_files:
                    # Valid new file found in main reports_dir
                    downloaded_file = list(new_files)[0]
                    src_path = os.path.join(reports_dir, downloaded_file)
                    
                    # Move to reports/research_projects
                    dest_path = os.path.join(reports_subdir, downloaded_file)
                    
                    # Handle overwrite if exists
                    if os.path.exists(dest_path):
                        os.remove(dest_path)
                        
                    os.rename(src_path, dest_path)
                    print(f"Successfully downloaded and moved to: {dest_path}")
                    return True
                    
                time.sleep(1)
                
            print("Timeout waiting for download.")
            return False
            
        except Exception as e:
            print(f"Error downloading {self.get_category_name()}: {e}")
            return False
