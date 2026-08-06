"""Capability Manager for Chinu AI."""

import random


class CapabilityManager:
    """Manages the assistant's capabilities and can describe them."""

    def __init__(self):
        """Initialize the CapabilityManager."""
        self.capabilities = [
            "open applications",
            "search Google",
            "play YouTube videos",
            "manage files",
            "control your computer",
        ]
        self.intros = [
            "I can",
            "I'm able to",
            "I can help you with things like",
        ]
        self.outros = [
            "and I'm learning new things every day, bhai.",
            "and I'm always getting better, bro.",
            "and I'm constantly being updated with new skills, dada.",
        ]

    def get_capabilities_description(self) -> str:
        """
        Generates a natural language description of the assistant's capabilities.

        Returns:
            A string describing the assistant's capabilities.
        """
        random.shuffle(self.capabilities)
        intro = random.choice(self.intros)
        outro = random.choice(self.outros)
        
        # Join all but the last capability with a comma
        capabilities_str = ", ".join(self.capabilities[:-1])
        
        # Add the last capability with 'and'
        capabilities_str += f", and {self.capabilities[-1]}"
        
        return f"{intro} {capabilities_str}, {outro}"