import unittest
import asyncio
from app.core.context import RollingWindowManager
from app.core.renderer import VoiceRenderer
from app.core.router import graph


class TestCoreModules(unittest.TestCase):

    def setUp(self):
        self.context_mgr = RollingWindowManager(max_turns=3)
        self.renderer = VoiceRenderer()

    def test_context_rolling_window(self):
        sender_id = "test_user_1"
        self.context_mgr.add_turn(sender_id, "user", "hello")
        self.context_mgr.add_turn(sender_id, "assistant", "hi")
        self.context_mgr.add_turn(sender_id, "user", "how are you?")
        self.context_mgr.add_turn(sender_id, "assistant", "good")
        self.context_mgr.add_turn(sender_id, "user", "tell me a joke")

        history = self.context_mgr.get_context(sender_id)
        # Should roll and keep only last 3 items
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0]["content"], "how are you?")
        self.assertEqual(history[2]["content"], "tell me a joke")

    def test_renderer_casual(self):
        # Formality level 1: casual
        bubbles = self.renderer.render("You are going to be honest with people.", formality_level=1)
        self.assertTrue(len(bubbles) >= 1)
        rendered_text = " ".join(bubbles)
        # Should be lowered, replaced with slang
        self.assertIn("u", rendered_text)
        self.assertIn("gonna", rendered_text)
        self.assertIn("tbh", rendered_text)

    def test_renderer_professional(self):
        # Formality level 5: professional
        bubbles = self.renderer.render("hello, it is done.", formality_level=5)
        self.assertTrue(len(bubbles) >= 1)
        rendered_text = "\n".join(bubbles)
        # Should capitalize first sentence, append period
        self.assertTrue(rendered_text.startswith("Hello") or "Hello" in rendered_text)
        self.assertTrue(rendered_text.strip().endswith("regards,") or rendered_text.strip().endswith(".") or "Sincerely" in rendered_text)

    def test_router_flow_mock(self):
        # Test executing the compiled LangGraph with mock input
        # Note: We run it using asyncio since LangGraph is async-ready
        async def run_flow():
            inputs = {
                "query": "hello there!",
                "sender_id": "test_user_2",
                "route": "",
                "evidence": "",
                "confidence": 0.0,
                "raw_response": "",
                "final_response": []
            }
            # Execute compiled graph
            result = await graph.ainvoke(inputs)
            self.assertIn("final_response", result)
            self.assertTrue(len(result["final_response"]) > 0)

        asyncio.run(run_flow())


if __name__ == "__main__":
    unittest.main()
