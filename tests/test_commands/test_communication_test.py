import unittest
from unittest import mock

from simulator_api.commands.communication_test import CommunicationTest
from simulator_api.celery_tasks.tasks import communication_test

mock_celery_task_obj = mock.MagicMock()
mock_celery_task_obj.id = 12345
mock_celery_task_obj.state = "SUCCESS"
mock_celery_task_obj.info = {'status': "SUCCESS", 'info': "hello"}


class TestCommandCommunicationTest(unittest.TestCase):
    @mock.patch('simulator_api.commands.communication_test.communication_test.apply_async')
    def test_post_execute_communication_test(self, mock_communincation_test_async_result):
        mock_communincation_test_async_result.return_value = mock_celery_task_obj

        command = CommunicationTest()

        # put request
        response = command.post_execute_latest(None, None, None)
        mock_communincation_test_async_result.assert_called_once()
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.content, {'task_id': 12345})

    @mock.patch('simulator_api.commands.communication_test.communication_test.AsyncResult')
    def test_get_execute_communication_test(self, mock_communincation_test_async_result):
        mock_communincation_test_async_result.return_value = mock_celery_task_obj

        command = CommunicationTest()

        # put request
        response = command.get_execute_latest(None, 12345)
        mock_communincation_test_async_result.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, {'status': "SUCCESS", 'info': "hello"})

    @mock.patch('simulator_api.commands.communication_test.communication_test.update_state')
    def test_communication_test(self, mock_communication_test_update):
        result = communication_test()
        # Expected results without ignition installed
        self.assertEqual(result['status'], "ERROR")
        for task_result in result['checklist']:
            self.assertEqual(task_result['status'], "ERROR")
