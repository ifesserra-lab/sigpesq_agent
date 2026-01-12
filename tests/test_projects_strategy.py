import unittest
from unittest.mock import MagicMock, AsyncMock, patch
from agent_sigpesq.strategies.projects_strategy import ProjectsDownloadStrategy

class TestProjectsDownloadStrategy(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.strategy = ProjectsDownloadStrategy()
        self.mock_page = AsyncMock()
        self.reports_dir = "/tmp/reports"

    @patch('agent_sigpesq.strategies.projects_strategy.ProjectsDownloadStrategy._handle_download_and_move')
    @patch('agent_sigpesq.strategies.projects_strategy.ProjectsDownloadStrategy._ensure_accordion_open')
    async def test_download_success(self, mock_ensure_accordion, mock_handle_download):
        # Setup mocks
        mock_handle_download.return_value = True

        # Execute
        result = await self.strategy.download(self.mock_page, self.reports_dir)

        # Verify
        self.assertTrue(result)
        mock_ensure_accordion.assert_called_once()
        mock_handle_download.assert_called_once()
        
    async def test_download_failure(self):
         with patch('agent_sigpesq.strategies.projects_strategy.ProjectsDownloadStrategy._ensure_accordion_open') as mock_open:
            mock_open.side_effect = Exception("Accordion Error")
            result = await self.strategy.download(self.mock_page, self.reports_dir)
            self.assertFalse(result)
