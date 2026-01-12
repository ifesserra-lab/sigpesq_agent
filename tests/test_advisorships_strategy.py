import unittest
from unittest.mock import MagicMock, AsyncMock, patch, call
from agent_sigpesq.strategies.advisorships_strategy import AdvisorshipsDownloadStrategy

class TestAdvisorshipsDownloadStrategy(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.strategy = AdvisorshipsDownloadStrategy()
        self.mock_page = AsyncMock()
        self.reports_dir = "/tmp/reports"

    @patch('agent_sigpesq.strategies.advisorships_strategy.AdvisorshipsDownloadStrategy._handle_download_and_move')
    @patch('agent_sigpesq.strategies.advisorships_strategy.AdvisorshipsDownloadStrategy._ensure_accordion_open')
    async def test_download_success(self, mock_ensure_accordion, mock_handle_download):
        # Setup mocks
        mock_handle_download.return_value = True
        
        # Mock year dropdown existence
        self.mock_page.is_visible.return_value = True
        
        # Mock eval_on_selector_all to return years
        self.mock_page.eval_on_selector_all.return_value = ["2024", "2025"]

        # Execute
        result = await self.strategy.download(self.mock_page, self.reports_dir)

        # Verify
        self.assertTrue(result)
        
        # Verify year selection
        expected_calls = [
            call("#ContentPlaceHolder_ddlAno", value="2024"),
            call("#ContentPlaceHolder_ddlAno", value="2025")
        ]
        self.mock_page.select_option.assert_has_calls(expected_calls)
        
        # Verify download calls
        self.assertEqual(mock_handle_download.call_count, 2)
        
    async def test_download_failure(self):
         with patch('agent_sigpesq.strategies.advisorships_strategy.AdvisorshipsDownloadStrategy._ensure_accordion_open') as mock_open:
            mock_open.side_effect = Exception("Accordion Error")
            result = await self.strategy.download(self.mock_page, self.reports_dir)
            self.assertFalse(result)
