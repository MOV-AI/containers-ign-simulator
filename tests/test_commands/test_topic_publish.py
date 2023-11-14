import unittest

from simulator_api.commands.topic_publish import TopicPublish

class TestCommandTopicPublish(unittest.TestCase):

    def test_post_execute_topic_publish(self):

        input_topic = "/dummy"
        input_message = "dummy"
        input_msgtype = "dummy-type"
        # Expected results without ignition installed
        expected_name = f"publish_{input_topic}"
        expected_status = "ERROR"
        expected_message = f"The command 'ign topic -p \"{input_message}\" -t {input_topic} --msgtype {input_msgtype}' returned a non-zero exit status"      

        command = TopicPublish()

        response = command.post_execute_latest({"topic": input_topic, "message": input_message, "msgtype": input_msgtype}, "arg", "arg")
        self.assertEqual(response.status_code, 200)
        # Response is dictionary with 3 elements
        self.assertEqual(len(list(response.content.keys())),3)
        # Keys of dictionary are name, status and message.
        result = response.content
        self.assertEqual(result['name'],expected_name)
        self.assertEqual(result['status'],expected_status)
        self.assertIn(expected_message,result['message'])