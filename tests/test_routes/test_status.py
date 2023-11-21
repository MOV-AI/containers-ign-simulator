import unittest
from unittest import mock
from simulator_api.entrypoint import app

class TestStatus(unittest.TestCase):

    # Bad_url should return 400
    def test_status_get_call_bad_url(self):

        with app.test_client() as client:
            response = client.get('/api/v1/dummy-command')
            self.assertEqual(response.status_code, 400)

    # Comm test get without id task should return 200
    def test_status_get_call_comm_test_no_id(self):

        with app.test_client() as client:
            response = client.get('/api/v1/communication-test')
            self.assertEqual(response.status_code, 200)
            self.assertIn("Celery tasks:", response.data.decode('utf-8'))

    # Comm test get wit bad id task should return 404 Not Found
    @mock.patch('simulator_api.commands.communication_test.communication_test.AsyncResult')
    def test_status_get_call_comm_test_bad_id(self, mock_communication_test_async_result):

        bad_task_id = 1

        # Mock behaviour of communication test : should return PENDING if 1 is bad id
        mock_celery_task_obj = mock.MagicMock()
        mock_celery_task_obj.state = "PENDING"
        mock_communication_test_async_result.return_value = mock_celery_task_obj

        with app.test_client() as client:
            response = client.get(f'/api/v1/communication-test/{bad_task_id}')
            self.assertEqual(response.status_code, 404)
            print(response.data.decode('utf-8'))
            self.assertIn(f"Task ID {bad_task_id} not found.", response.data.decode('utf-8'))

    # Bad parameters should return 400 Bad Request
    def test_status_post_call_comm_test_bad_params(self):

        bad_params_echo_topic = "echo-topic=4"
        bad_params_publish_topic = "publish-topic=bad_topic"
        bad_params_world_name = "world-name=5/bad"
        bad_params_timeout = "timeout=a"
        bad_param_interval_timeout = "timeout=40000"

        with app.test_client() as client:
            for bad_param in [
                bad_params_echo_topic,
                bad_params_publish_topic,
                bad_params_world_name,
                bad_params_timeout,
            ]:
                response = client.post(f'/api/v1/communication-test?{bad_param}')
                self.assertEqual(response.status_code, 400)
                self.assertIn("Not valid", response.data.decode('utf-8'))

            response = client.post(f'/api/v1/communication-test?{bad_param_interval_timeout}')
            self.assertEqual(response.status_code, 400)
            self.assertIn("Timeout larger than maximum allowed (15): ", response.data.decode('utf-8'))

    # Bad parameters should return 400 Bad Request
    def test_status_post_call_echo_topic_bad_params(self):

        bad_params_echo_topic = "topic=4&timeout=5"
        bad_params_timeout = "topic=/clock&timeout=a"
        bad_param_interval_timeout = "topic=/clock&timeout=40000"

        with app.test_client() as client:
            for bad_param in [bad_params_echo_topic, bad_params_timeout]:
                response = client.post(f'/api/v1/topic-echo?{bad_param}')
                self.assertEqual(response.status_code, 400)
                self.assertIn("Not valid", response.data.decode('utf-8'))

            response = client.post(f'/api/v1/topic-echo?{bad_param_interval_timeout}')
            self.assertEqual(response.status_code, 400)
            self.assertIn("Timeout larger than maximum allowed (15): ", response.data.decode('utf-8'))

    # Bad parameters should return 400 Bad Request
    def test_status_post_call_publish_topic_bad_params(self):

        bad_params_publish_topic = "topic=4&message=XXX&msgtype=XXXX"

        with app.test_client() as client:
            response = client.post(f'/api/v1/topic-publish?{bad_params_publish_topic}')
            self.assertEqual(response.status_code, 400)
            self.assertIn("Not valid topic: 4", response.data.decode('utf-8'))
