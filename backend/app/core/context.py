from collections import deque
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class RollingWindowManager:
    """Manages the last 5 turns of conversation context per sender/user."""

    def __init__(self, max_turns: int = 5):
        self.max_turns = max_turns
        self.history: Dict[str, deque] = {}

    def add_turn(self, sender_id: str, role: str, content: str):
        """Appends a conversation turn (role: 'user' or 'assistant') to the history."""
        if sender_id not in self.history:
            self.history[sender_id] = deque(maxlen=self.max_turns)

        self.history[sender_id].append({"role": role, "content": content})
        logger.info(
            f"Added turn to context window for user {sender_id}. Current size: {len(self.history[sender_id])}"
        )

    def get_context(self, sender_id: str) -> List[Dict[str, str]]:
        """Returns the conversation history for the sender."""
        if sender_id not in self.history:
            return []
        return list(self.history[sender_id])

    def clear_context(self, sender_id: str):
        """Clears context history for the sender."""
        if sender_id in self.history:
            self.history[sender_id].clear()
            logger.info(f"Cleared context window for user {sender_id}")


# Singleton instance of context manager
context_manager = RollingWindowManager()
