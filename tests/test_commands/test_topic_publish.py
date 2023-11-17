import unittest

from simulator_api.commands.topic_publish import TopicPublish


class TestCommandTopicPublish(unittest.TestCase):
    def test_post_execute_topic_publish(self):

        input_topic = "/dummy"
        input_message = "dummy"
        input_msgtype = "dummy-type"
        # Expected results without ignition installed
        expected_command = f'ign topic -p \"{input_message}\" -t {input_topic} --msgtype {input_msgtype}'
        expected_status = "ERROR"
        expected_exitcode = 127  # command not found

        command = TopicPublish()

        response = command.post_execute_latest(
            {"topic": input_topic, "message": input_message, "msgtype": input_msgtype}, "arg", "arg"
        )
        self.assertEqual(response.status_code, 200)
        # Response is dictionary with 4 elements
        self.assertEqual(len(list(response.content.keys())), 4)
        # Keys of dictionary are command, status, exitcode and output.
        result = response.content
        self.assertEqual(result['command'], expected_command)
        self.assertEqual(result['status'], expected_status)
        self.assertEqual(expected_exitcode, result['exitcode'])
