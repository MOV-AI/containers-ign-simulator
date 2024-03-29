import unittest
from unittest import mock

from simulator_api.commands.topic_echo import TopicEcho
from simulator_api.celery_tasks.tasks import echo_topic

mock_celery_task_obj = mock.MagicMock()
mock_celery_task_obj.id = 12345
mock_celery_task_obj.state = "SUCCESS"
mock_celery_task_obj.info = {'status': "SUCCESS", 'info': "hello"}


class TestCommandTopicEcho(unittest.TestCase):
    @mock.patch('simulator_api.commands.topic_echo.echo_topic.apply_async')
    def test_post_execute_communication_test(self, mock_echo_topic_async_result):
        mock_echo_topic_async_result.return_value = mock_celery_task_obj

        input_topic = "/dummy"
        input_timeout = 1

        command = TopicEcho()

        # put request
        response = command.post_execute_latest(
            {"topic": input_topic, "timeout": input_timeout}, None, None
        )
        mock_echo_topic_async_result.assert_called_once()
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.content, {'task_id': 12345})

    @mock.patch('simulator_api.commands.topic_echo.echo_topic.AsyncResult')
    def test_get_execute_communication_test(self, mock_echo_topic_async_result):
        mock_echo_topic_async_result.return_value = mock_celery_task_obj

        command = TopicEcho()

        # put request
        response = command.get_execute_latest(None, 12345)
        mock_echo_topic_async_result.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, {'status': "SUCCESS", 'info': "hello"})

    @mock.patch('simulator_api.commands.topic_echo.echo_topic.update_state')
    def test_communication_test(self, mock_echo_topic_update):
        input_topic = "/dummy"
        # Expected results without ignition installed
        expected_command = f'ign topic -e -n 1 -t {input_topic}'
        expected_status = "ERROR"
        expected_exitcode = 127  # command not found

        result = echo_topic(input_topic, 1)
        self.assertEqual(len(list(result.keys())), 4)
        # Keys of dictionary are command, status, exitcode and output.
        self.assertEqual(result['command'], expected_command)
        self.assertEqual(result['status'], expected_status)
        self.assertEqual(expected_exitcode, result['exitcode'])
