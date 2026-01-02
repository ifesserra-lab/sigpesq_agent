"""
Strategy implementation for downloading Advisorships reports.
"""

from .report_download_strategy import ReportDownloadStrategy
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

class AdvisorshipsDownloadStrategy(ReportDownloadStrategy):
    """
    Strategy for downloading reports related to Advisorships.
    """

    def get_category_name(self) -> str:
        """Returns the category name 'Advisorships'."""
        return "Advisorships"
        
    def get_button_id(self) -> str:
        """Returns the button ID for Advisorships."""
        return "ContentPlaceHolder_btnRel_Orientacoes"
        
    def download(self, driver, reports_dir: str) -> bool:
        """
        Executes the download simulation for Advisorships.

        Args:
            driver: The Selenium WebDriver instance.
            reports_dir (str): The target directory for the report.

        Returns:
            bool: Always True (simulation).
        """
        print(f"Processing {self.get_category_name()}...")
        
        try:
            wait = WebDriverWait(driver, 20)
            button_id = self.get_button_id()
            
            # 1. Ensure accordion is open
            try:
                # Check if button is visible
                wait.until(EC.visibility_of_element_located((By.ID, button_id)))
            except:
                print("Button not visible, attempting to open accordion...")
                # Find header containing "Orientações"
                xpath = "//div[contains(@class, 'accordionHeader') and contains(., 'Orientações')]"
                header = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                header.click()
                time.sleep(1) # Wait for animation

            # 2. Find Year Dropdown
            dropdown_id = "ContentPlaceHolder_ddlRelOrientacao_Ano"
            dropdown_element = wait.until(EC.presence_of_element_located((By.ID, dropdown_id)))
            select = Select(dropdown_element)
            
            # Get all options first to avoid stale element reference
            options_values = [option.get_attribute("value") for option in select.options]
            
            download_count = 0
            
            # 3. Iterate through each year
            for year in options_values:
                print(f"Processing Year: {year}")
                
                # Check for year-specific directory
                year_dir = os.path.join(reports_dir, "advisorships", year)
                if not os.path.exists(year_dir):
                    os.makedirs(year_dir)

                # Re-locate element to avoid StaleElementReferenceException
                dropdown_element = wait.until(EC.presence_of_element_located((By.ID, dropdown_id)))
                select = Select(dropdown_element)
                select.select_by_value(year)
                time.sleep(1) # Wait for selection to apply if needed

                # Click Download
                print(f"Clicking button {button_id} for year {year}...")
                btn = wait.until(EC.element_to_be_clickable((By.ID, button_id)))
                btn.click()
                
                # Wait for download
                if self._wait_and_move_file(reports_dir, year_dir):
                    download_count += 1
                else:
                    print(f"Failed to download report for {year}")
            
            return download_count > 0

        except Exception as e:
            print(f"Error downloading {self.get_category_name()}: {e}")
            return False

    def _wait_and_move_file(self, download_dir: str, target_dir: str, timeout: int = 60) -> bool:
        """Waits for download and moves file to target directory."""
        print(f"Waiting for download for target: {target_dir}...")
        start_time = time.time()
        initial_files = set(os.listdir(download_dir))
        
        while time.time() - start_time < timeout:
            current_files = set(os.listdir(download_dir))
            new_files = current_files - initial_files
            
            if any(f.endswith('.crdownload') or f.endswith('.tmp') for f in new_files):
                time.sleep(1)
                continue
                
            if new_files:
                downloaded_file = list(new_files)[0]
                src_path = os.path.join(download_dir, downloaded_file)
                dest_path = os.path.join(target_dir, downloaded_file)
                
                if os.path.exists(dest_path):
                    os.remove(dest_path)
                    
                os.rename(src_path, dest_path)
                print(f"Successfully downloaded and moved to: {dest_path}")
                return True
                
            time.sleep(1)
            
        print("Timeout waiting for download.")
        return False
