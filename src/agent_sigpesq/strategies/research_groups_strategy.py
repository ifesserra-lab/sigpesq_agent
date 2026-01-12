import os
from playwright.async_api import Page
from .report_download_strategy import BasePlaywrightStrategy

class ResearchGroupsDownloadStrategy(BasePlaywrightStrategy):
    """
    Strategy for downloading reports related to Research Groups.
    """
    
    def get_category_name(self) -> str:
        """Returns the category name 'Research Groups'."""
        return "Research Groups"
        
    def get_button_id(self) -> str:
        """Returns the button ID for Research Groups."""
        return "ContentPlaceHolder_btnRel_GruposPesquisa" 
        
    async def download(self, page: Page, reports_dir: str) -> bool:
        """
        Executes the download simulation for Research Groups.
        """
        print(f"Processing {self.get_category_name()}...")
        
        try:
            # 1. Prepare target subdirectory
            reports_subdir = os.path.join(reports_dir, "research_group")

            button_id = self.get_button_id()
            
            # 2. Ensure accordion is open
            await self._ensure_accordion_open(page, button_id, "Grupos de Pesquisa")

            # 3. Handle download
            selector = f"#{button_id}"
            return await self._handle_download_and_move(page, selector, reports_dir, reports_subdir)
            
        except Exception as e:
            print(f"Error downloading {self.get_category_name()}: {e}")
            return False
