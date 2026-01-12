import unittest
from unittest.mock import MagicMock, patch, call
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from agent_sigpesq.strategies.advisorships_strategy import AdvisorshipsDownloadStrategy

class TestAdvisorshipsDownloadStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = AdvisorshipsDownloadStrategy()
        self.mock_driver = MagicMock()
        self.reports_dir = "/tmp/reports"

    @patch('agent_sigpesq.strategies.advisorships_strategy.WebDriverWait')
    @patch('agent_sigpesq.strategies.advisorships_strategy.Select')
    @patch('agent_sigpesq.strategies.advisorships_strategy.AdvisorshipsDownloadStrategy._wait_and_move_file')
    def test_download_success(self, mock_wait_and_move, MockSelect, MockWebDriverWait):
        # Setup mocks
        mock_wait_instance = MockWebDriverWait.return_value
        mock_element = MagicMock()
        mock_element.tag_name = "select"  # Critical for Select class check
        mock_wait_instance.until.return_value = mock_element
        
        # Setup mocked Select
        mock_select_instance = MockSelect.return_value
        # Mock options: e.g., 2024 and 2025
        option1 = MagicMock()
        option1.get_attribute.return_value = "2024"
        option2 = MagicMock()
        option2.get_attribute.return_value = "2025"
        mock_select_instance.options = [option1, option2]
        
        mock_wait_and_move.return_value = True

        # Execute
        result = self.strategy.download(self.mock_driver, self.reports_dir)

        # Verify
        self.assertTrue(result)
        
        # Verify loop execution (should happen twice)
        # Select.select_by_value should be called for each year
        mock_select_instance.select_by_value.assert_has_calls([call("2024"), call("2025")])
        
        # Verify file moves
        mock_wait_and_move.assert_has_calls([
            call(self.reports_dir, "/tmp/reports/advisorships/2024"),
            call(self.reports_dir, "/tmp/reports/advisorships/2025")
        ])

    @patch('agent_sigpesq.strategies.advisorships_strategy.WebDriverWait')
    @patch('agent_sigpesq.strategies.advisorships_strategy.Select')
    @patch('agent_sigpesq.strategies.advisorships_strategy.AdvisorshipsDownloadStrategy._wait_and_move_file')
    def test_partial_download_success(self, mock_wait_and_move, MockSelect, MockWebDriverWait):
        """Test case where one year fails but overall process returns true if at least one succeeds"""
        mock_wait_instance = MockWebDriverWait.return_value
        mock_element = MagicMock()
        mock_element.tag_name = "select"
        mock_wait_instance.until.return_value = mock_element
        
        mock_select_instance = MockSelect.return_value
        option1 = MagicMock()
        option1.get_attribute.return_value = "2024"
        option2 = MagicMock()
        option2.get_attribute.return_value = "2025"
        mock_select_instance.options = [option1, option2]
        
        # Fail first download, succeed second
        mock_wait_and_move.side_effect = [False, True]

        result = self.strategy.download(self.mock_driver, self.reports_dir)

        self.assertTrue(result)
        
    @patch('agent_sigpesq.strategies.advisorships_strategy.WebDriverWait')
    def test_download_critical_failure(self, MockWebDriverWait):
        # Setup failure
        mock_wait_instance = MockWebDriverWait.return_value
        mock_wait_instance.until.side_effect = Exception("Critical Error")

        # Execute
        result = self.strategy.download(self.mock_driver, self.reports_dir)

        # Verify
        self.assertFalse(result)
