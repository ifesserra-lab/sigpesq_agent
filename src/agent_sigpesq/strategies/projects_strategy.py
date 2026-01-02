from .report_download_strategy import ReportDownloadStrategy

class ProjectsDownloadStrategy(ReportDownloadStrategy):
    def get_category_name(self) -> str:
        return "Research Projects"
        
    def get_button_id(self) -> str:
        return "btnEmitirProjetos"
        
    def download(self, driver, reports_dir: str) -> bool:
        print(f"Processing {self.get_category_name()}...")
        return True
