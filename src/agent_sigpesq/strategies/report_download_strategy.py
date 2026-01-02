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

import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BaseSeleniumStrategy(ReportDownloadStrategy):
    """
    Base strategy providing common Selenium operations for report downloads.
    """

    def _ensure_accordion_open(self, wait: WebDriverWait, button_id: str, accordion_text: str):
        """
        Ensures the accordion section containing the desired button is open.
        """
        try:
            # Check if button is visible first
            try:
                wait.until(EC.visibility_of_element_located((By.ID, button_id)))
                return # Already visible/open
            except:
                pass # Proceed to open

            print(f"Button {button_id} not visible, attempting to open accordion '{accordion_text}'...")
            xpath = f"//div[contains(@class, 'accordionHeader') and contains(., '{accordion_text}')]"
            header = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            header.click()
            time.sleep(1) # Wait for animation
        except Exception as e:
            print(f"Error opening accordion '{accordion_text}': {e}")

    def _wait_and_move_file(self, download_dir: str, target_dir: str, timeout: int = 60) -> bool:
        """
        Waits for a file to appear in the download directory and moves it to the target directory.
        """
        print(f"Waiting for download for target: {target_dir}...")
        
        # Ensure target directory exists
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        start_time = time.time()
        initial_files = set(os.listdir(download_dir))
        
        while time.time() - start_time < timeout:
            current_files = set(os.listdir(download_dir))
            new_files = current_files - initial_files
            
            # Check for crdownload/tmp files
            if any(f.endswith('.crdownload') or f.endswith('.tmp') for f in new_files):
                time.sleep(1)
                continue
                
            if new_files:
                downloaded_file = list(new_files)[0]
                src_path = os.path.join(download_dir, downloaded_file)
                dest_path = os.path.join(target_dir, downloaded_file)
                
                # Handle overwrite if exists
                if os.path.exists(dest_path):
                    os.remove(dest_path)
                    
                os.rename(src_path, dest_path)
                print(f"Successfully downloaded and moved to: {dest_path}")
                return True
                
            time.sleep(1)
            
        print("Timeout waiting for download.")
        return False
