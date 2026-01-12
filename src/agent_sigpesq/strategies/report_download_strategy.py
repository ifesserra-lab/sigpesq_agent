"""
Module defining the abstract strategy for report downloads using Playwright.

This module provides the interface `ReportDownloadStrategy` that all specific
report category strategies must implement.
"""

from abc import ABC, abstractmethod
import os
import asyncio
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

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
    async def download(self, page: Page, reports_dir: str) -> bool:
        """
        Executes the download process for this specific strategy.

        Args:
            page: The Playwright Page instance.
            reports_dir (str): The absolute path to the directory where reports should be saved.

        Returns:
            bool: True if the download was successful, False otherwise.
        """
        pass

class BasePlaywrightStrategy(ReportDownloadStrategy):
    """
    Base strategy providing common Playwright operations for report downloads.
    """

    async def _ensure_accordion_open(self, page: Page, button_id: str, accordion_text: str):
        """
        Ensures the accordion section containing the desired button is open.
        """
        try:
            # Check if button is visible
            is_visible = await page.is_visible(f"#{button_id}")
            if is_visible:
                return

            print(f"Button {button_id} not visible, attempting to open accordion '{accordion_text}'...")
            xpath = f"//div[contains(@class, 'accordionHeader') and contains(., '{accordion_text}')]"
            
            # Click the header
            await page.click(xpath)
            
            # Wait for button to become visible (animation)
            try:
                await page.wait_for_selector(f"#{button_id}", state="visible", timeout=5000)
            except PlaywrightTimeoutError:
                print(f"Warning: Button {button_id} still not visible after clicking accordion.")
                
        except Exception as e:
            print(f"Error opening accordion '{accordion_text}': {e}")

    async def _handle_download_and_move(self, page: Page, selector: str, download_dir: str, target_subdir: str) -> bool:
        """
        Handles the download event and moves the file to the target directory.
        """
        try:
            print(f"Waiting for download for target: {target_subdir}...")
            
            # Ensure target directory exists
            if not os.path.exists(target_subdir):
                os.makedirs(target_subdir)

            async with page.expect_download(timeout=60000) as download_info:
                # Trigger the download
                await page.click(selector)
            
            download = await download_info.value
            
            # Use original filename from server
            original_filename = download.suggested_filename
            dest_path = os.path.join(target_subdir, original_filename)
            
            # Handle overwrite
            if os.path.exists(dest_path):
                os.remove(dest_path)
                
            await download.save_as(dest_path)
            print(f"Successfully downloaded and saved to: {dest_path}")
            return True
            
        except Exception as e:
            print(f"Error during download handling: {e}")
            return False
