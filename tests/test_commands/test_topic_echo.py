import unittest
from unittest import mock

from simulator_api.commands.topic_echo import TopicEcho

mock_celery_task_obj = mock.MagicMock()
mock_celery_task_obj.id = 12345
mock_celery_task_obj.state = "SUCCESS"
mock_celery_task_obj.info = {'status': "SUCCESS", 'info': "hello"}

class TestCommandTopicEcho(unittest.TestCase):

    @mock.patch('simulator_api.commands.topic_echo.echo_topic.apply_async')    
    def test_post_execute_communication_test(self, mock_echo_topic_async_result):

        mock_echo_topic_async_result.return_value = mock_celery_task_obj

        command = TopicEcho()

        # put request
        response = command.post_execute_latest({"topic": "dummmy", "message": "dummy", "msgtype": "dummy-type"}, "arg", "arg")
        mock_echo_topic_async_result.assert_called_once()
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.content, {'task_id': 12345})

    @mock.patch('simulator_api.commands.topic_echo.echo_topic.AsyncResult')    
    def test_post_execute_communication_test(self, mock_echo_topic_async_result):

        mock_echo_topic_async_result.return_value = mock_celery_task_obj

        command = TopicEcho()

        # put request
        response = command.get_execute_latest("arg", 12345)
        mock_echo_topic_async_result.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, {'status': "SUCCESS", 'info': "hello"})
