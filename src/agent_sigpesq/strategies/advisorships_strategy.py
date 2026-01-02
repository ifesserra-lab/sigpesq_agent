from .report_download_strategy import ReportDownloadStrategy

class AdvisorshipsDownloadStrategy(ReportDownloadStrategy):
    def get_category_name(self) -> str:
        return "Advisorships"
        
    def get_button_id(self) -> str:
        return "btnEmitirOrientacoes"
        
    def download(self, driver, reports_dir: str) -> bool:
        print(f"Processing {self.get_category_name()}...")
        return True
