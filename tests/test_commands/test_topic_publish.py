import unittest

from simulator_api.commands.topic_publish import TopicPublish

class TestCommandTopicPublish(unittest.TestCase):

    def test_post_execute_topic_publish(self):

        command = TopicPublish()

        response = command.post_execute_latest({"topic": "dummmy", "message": "dummy", "msgtype": "dummy-type"}, "arg", "arg")
        self.assertEqual(response.status_code, 200)
        # Response is dictionary with 3 elements
        self.assertEqual(len(list(response.content.keys())),3)
        # Keys of dictionary are name, status and message.
        for key in response.content.keys():
            self.assertIn(key, ['status', 'name', 'message'])