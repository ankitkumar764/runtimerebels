import unittest
from app.workers.delays import calculate_typing_delay, calculate_bubble_delay
from app.workers.tasks import process_message_task


class TestWorkers(unittest.TestCase):

    def test_typing_delay_bounds(self):
        # Short reply
        delay_short = calculate_typing_delay("hey")
        # Long reply
        delay_long = calculate_typing_delay(
            "This is a very long response designed to test the upper boundary of our typing delay limits. "
            "It should theoretically calculate a much higher delay, but be clamped by the settings limits."
        )

        # Min delay default is 30, max is 120
        self.assertGreaterEqual(delay_short, 30.0)
        self.assertLessEqual(delay_short, 120.0)
        self.assertGreaterEqual(delay_long, 30.0)
        self.assertLessEqual(delay_long, 120.0)

    def test_bubble_delay(self):
        self.assertEqual(calculate_bubble_delay(), 0.4)

    def test_process_message_task_execution(self):
        # Execute the task directly in synchronous test mode
        message_data = {
            "platform": "telegram",
            "sender_id": "test_user_3",
            "sender_name": "Test User",
            "content": "hello there!",
        }

        # This should execute the entire pipeline with stub triggers
        # It shouldn't crash and should execute in-memory pipeline
        try:
            process_message_task(message_data)
            success = True
        except Exception as e:
            success = False
            print(f"Task execution failed: {e}")

        self.assertTrue(success)


if __name__ == "__main__":
    unittest.main()
