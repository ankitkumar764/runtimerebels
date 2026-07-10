import random
import re
from typing import List
import logging

logger = logging.getLogger(__name__)

# Slang mappings for casual/vibe dials
CASUAL_SLANG = {
    "you": "u",
    "are": "r",
    "to": "2",
    "for": "4",
    "people": "ppl",
    "because": "cuz",
    "going to": "gonna",
    "want to": "wanna",
    "don't know": "idk",
    "to be honest": "tbh",
    "laughing my ass off": "lmao",
    "oh my god": "omg",
    "laugh out loud": "lol",
    "in my opinion": "imo",
}

PROFESSIONAL_GREETINGS = ["Hello,", "Dear sender,", "Greetings,", "Hope you are well."]
PROFESSIONAL_SIGNATURES = [
    "Best regards,",
    "Sincerely,",
    "Thank you,",
    "Respectfully,",
]


class VoiceRenderer:
    """Renders responses in the user's specific voice based on the formality dial."""

    def render(selfself, text: str, formality_level: int = 3) -> List[str]:
        """Applies formality adjustments, slang mapping, casing, and splits bubbles."""
        if not text:
            return []

        # 1. Apply Formality Dial & Slang Mapping
        adjusted_text = text
        if formality_level <= 2:
            # Casual Dial
            adjusted_text = self._to_casual(adjusted_text)
        elif formality_level >= 4:
            # Professional Dial
            adjusted_text = self._to_professional(adjusted_text)

        # 2. Bubble Splitting: if text is long, split into 2-3 fragments
        bubbles = self._split_bubbles(adjusted_text)
        logger.info(
            f"Rendered voice at formality {formality_level}. Split response into {len(bubbles)} bubbles."
        )
        return bubbles

    def _to_casual(self, text: str) -> str:
        """Converts text to casual/slang style."""
        # Convert to lowercase mostly
        text = text.lower()

        # Remove terminal periods
        if text.endswith("."):
            text = text[:-1]

        # Apply casual slang mappings
        for original, slang in CASUAL_SLANG.items():
            pattern = re.compile(r"\b" + re.escape(original) + r"\b", re.IGNORECASE)
            text = pattern.sub(slang, text)

        # Add casual punctuation or suffix sometimes
        if random.random() < 0.3:
            suffixes = [" lol", " tbh", " ig", " fr"]
            text += random.choice(suffixes)

        return text

    def _to_professional(self, text: str) -> str:
        """Enforces formal sentence case, greetings, and punctuation."""
        # Ensure capitalization
        text = text.strip()
        if not text.endswith((".", "!", "?")):
            text += "."

        # Capitalize first letter of sentences
        sentences = [s.strip().capitalize() for s in text.split(".") if s.strip()]
        text = ". ".join(sentences) + "." if sentences else text

        # Add professional wrapper (20% chance or if length is short)
        if len(text) < 50:
            greeting = random.choice(PROFESSIONAL_GREETINGS)
            signature = random.choice(PROFESSIONAL_SIGNATURES)
            text = f"{greeting}\n\n{text}\n\n{signature}"

        return text

    def _split_bubbles(self, text: str) -> List[str]:
        """Splits long text into multiple bubbles if text length is greater than 80 chars."""
        # Clean double newlines first
        text = text.replace("\n\n", "\n")

        # If short, return single bubble
        if len(text) <= 80:
            return [text.strip()]

        # Split on sentence boundaries, list items, or newlines
        splits = re.split(r"(?<=[.!?])\s+|\n", text)
        bubbles = []
        current_bubble = ""

        for part in splits:
            part = part.strip()
            if not part:
                continue

            if len(current_bubble) + len(part) <= 100:
                if current_bubble:
                    current_bubble += " " + part
                else:
                    current_bubble = part
            else:
                if current_bubble:
                    bubbles.append(current_bubble)
                current_bubble = part

        if current_bubble:
            bubbles.append(current_bubble)

        # Ensure we don't have too many bubbles (max 3)
        if len(bubbles) > 3:
            # Merge extra bubbles
            merged = []
            merged.append(bubbles[0])
            merged.append(" ".join(bubbles[1:3]))
            merged.append(" ".join(bubbles[3:]))
            bubbles = [b for b in merged if b.strip()]

        return bubbles


voice_renderer = VoiceRenderer()
