import unittest
from unittest.mock import MagicMock, AsyncMock, patch
from agent_sigpesq.strategies.research_groups_strategy import ResearchGroupsDownloadStrategy

class TestResearchGroupsDownloadStrategy(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.strategy = ResearchGroupsDownloadStrategy()
        self.mock_page = AsyncMock()
        self.reports_dir = "/tmp/reports"

    @patch('agent_sigpesq.strategies.research_groups_strategy.ResearchGroupsDownloadStrategy._handle_download_and_move')
    @patch('agent_sigpesq.strategies.research_groups_strategy.ResearchGroupsDownloadStrategy._ensure_accordion_open')
    async def test_download_success(self, mock_ensure_accordion, mock_handle_download):
        # Setup mocks
        mock_handle_download.return_value = True

        # Execute
        result = await self.strategy.download(self.mock_page, self.reports_dir)

        # Verify
        self.assertTrue(result)
        
        # Verify interactions
        mock_ensure_accordion.assert_called_once()
        mock_handle_download.assert_called_once()
        
    async def test_download_failure(self):
        # We can implement specific failure logic if needed, 
        # but the abstract base handles most logic now. 
        # Here we just verify the strategy catches exception
        self.mock_page.click.side_effect = Exception("General Error")
        
        # We need to mock internal methods or let them run to fail
        # If we let them run, _ensure_accordion_open might call click
        
        # Let's mock _ensure_accordion_open to fail
        with patch('agent_sigpesq.strategies.research_groups_strategy.ResearchGroupsDownloadStrategy._ensure_accordion_open') as mock_open:
            mock_open.side_effect = Exception("Accordion Error")
            result = await self.strategy.download(self.mock_page, self.reports_dir)
            self.assertFalse(result)
