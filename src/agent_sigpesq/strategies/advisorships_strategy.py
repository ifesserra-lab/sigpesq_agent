import os
import asyncio
from playwright.async_api import Page
from .report_download_strategy import BasePlaywrightStrategy

class AdvisorshipsDownloadStrategy(BasePlaywrightStrategy):
    """
    Strategy for downloading reports related to Student Advisorships (Orientacoes),
    iterating through available years.
    """

    def get_category_name(self) -> str:
        """Returns the category name 'Advisorships'."""
        return "Advisorships"
        
    def get_button_id(self) -> str:
        """Returns the button ID for Advisorships."""
        return "ContentPlaceHolder_btnRel_Orientacoes"
        
    async def download(self, page: Page, reports_dir: str) -> bool:
        """
        Executes the download process for Advisorships.
        """
        print(f"Processing {self.get_category_name()}...")
        
        try:
            button_id = self.get_button_id()
            
            # 1. Ensure accordion is open
            await self._ensure_accordion_open(page, button_id, "Orientações")
            
            # 2. Get year dropdown
            year_select_id = "ContentPlaceHolder_ddlRelOrientacao_Ano"
            
            # Check if dropdown exists
            if not await page.is_visible(f"#{year_select_id}"):
                print(f"Year dropdown {year_select_id} not found.")
                return False

            # Get all options using evaluation
            options = await page.eval_on_selector_all(
                f"#{year_select_id} option", 
                "elements => elements.map(e => e.value)"
            )
            
            # Filter valid years (exclude empty valued or "Select" options)
            years = [opt for opt in options if opt and opt.isdigit()]
            years.sort() # Ensure order
            
            print(f"Found years: {years}")
            
            success_count = 0
            
            for year in years:
                try:
                    print(f"Processing Year: {year}")
                    
                    # Select year
                    await page.select_option(f"#{year_select_id}", value=year)
                    
                    # Need to wait for postback/loading masking if likely
                    # Assuming standard ASP.NET behavior, might need a small wait or check for loading mask
                    # await page.wait_for_timeout(1000) 
                    
                    # Prepare subdirectory
                    year_subdir = os.path.join(reports_dir, "advisorships", year)
                    
                    print(f"Clicking button {button_id} for year {year}...")
                    
                    # Handle download
                    selector = f"#{button_id}"
                    if await self._handle_download_and_move(page, selector, reports_dir, year_subdir):
                        success_count += 1
                    else:
                        print(f"Failed to download report for {year}")
                        
                except Exception as e:
                    print(f"Error processing year {year}: {e}")
                    
            if success_count > 0:
                print(f"Successfully downloaded {success_count} advisorship reports.")
                return True
            else:
                print("No advisorship reports downloaded successfully.")
                return False
                
        except Exception as e:
            print(f"Error downloading {self.get_category_name()}: {e}")
            return False
