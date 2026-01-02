"""
Strategy implementation for downloading Advisorships reports.
"""

from .report_download_strategy import BaseSeleniumStrategy
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

class AdvisorshipsDownloadStrategy(BaseSeleniumStrategy):
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
        """
        print(f"Processing {self.get_category_name()}...")
        
        try:
            wait = WebDriverWait(driver, 20)
            button_id = self.get_button_id()
            
            # 1. Ensure accordion is open
            self._ensure_accordion_open(wait, button_id, "Orientações")

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

                # Re-locate element to avoid StaleElementReferenceException
                dropdown_element = wait.until(EC.presence_of_element_located((By.ID, dropdown_id)))
                select = Select(dropdown_element)
                select.select_by_value(year)
                time.sleep(1) # Wait for selection to apply if needed

                # Click Download
                print(f"Clicking button {button_id} for year {year}...")
                btn = wait.until(EC.element_to_be_clickable((By.ID, button_id)))
                btn.click()
                
                # 4. Wait for download and move file
                if self._wait_and_move_file(reports_dir, year_dir):
                    download_count += 1
                else:
                    print(f"Failed to download report for {year}")
            
            return download_count > 0

        except Exception as e:
            print(f"Error downloading {self.get_category_name()}: {e}")
            return False
