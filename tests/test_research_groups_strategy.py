import unittest
from unittest.mock import MagicMock, patch
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from agent_sigpesq.strategies.research_groups_strategy import ResearchGroupsDownloadStrategy

class TestResearchGroupsDownloadStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = ResearchGroupsDownloadStrategy()
        self.mock_driver = MagicMock()
        self.reports_dir = "/tmp/reports"

    @patch('agent_sigpesq.strategies.research_groups_strategy.WebDriverWait')
    @patch('agent_sigpesq.strategies.research_groups_strategy.ResearchGroupsDownloadStrategy._wait_and_move_file')
    def test_download_success(self, mock_wait_and_move, MockWebDriverWait):
        # Setup mocks
        mock_wait_instance = MockWebDriverWait.return_value
        mock_element = MagicMock()
        mock_wait_instance.until.return_value = mock_element
        mock_wait_and_move.return_value = True

        # Execute
        result = self.strategy.download(self.mock_driver, self.reports_dir)

        # Verify
        self.assertTrue(result)
        
        # Verify accordion interaction
        # Note: _ensure_accordion_open is called internally
        
        # Verify download button click
        # The exact call arguments depend on implementation details of _ensure_accordion_open
        # checking specifically for the download button click
        button_id = self.strategy.get_button_id()
        # Ensure we verified expected conditions containing the button ID
        self.assertTrue(mock_wait_instance.until.called)
        mock_element.click.assert_called()
        
        # Verify file move
        mock_wait_and_move.assert_called_with(self.reports_dir, "/tmp/reports/research_group")

    @patch('agent_sigpesq.strategies.research_groups_strategy.WebDriverWait')
    def test_download_failure(self, MockWebDriverWait):
        # Setup failure
        mock_wait_instance = MockWebDriverWait.return_value
        mock_wait_instance.until.side_effect = Exception("Element not found")

        # Execute
        result = self.strategy.download(self.mock_driver, self.reports_dir)

        # Verify
        self.assertFalse(result)
