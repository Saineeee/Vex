import unittest
from unittest.mock import MagicMock
import sys
import os

# 1. Define a real class for Cog with necessary methods to avoid AttributeError during class definition
class Cog:
    @staticmethod
    def listener(*args, **kwargs):
        return lambda func: func

# 2. Set up the mock structure
mock_discord = MagicMock()
mock_commands = MagicMock()
mock_commands.Cog = Cog
mock_ext = MagicMock()
mock_ext.commands = mock_commands
mock_app_commands = MagicMock()

# 3. Patch sys.modules BEFORE importing the cog
# We use a context manager in a common setup if possible, but here we do it at module level
# and ensure we clean up if needed, though for a dedicated test file it's usually okay.
sys.modules["discord"] = mock_discord
sys.modules["discord.ext"] = mock_ext
sys.modules["discord.ext.commands"] = mock_commands
sys.modules["discord.app_commands"] = mock_app_commands

# 4. Now import the real Leveling class from the codebase
# Ensure we are importing the one we just patched for
if 'cogs.leveling' in sys.modules:
    del sys.modules['cogs.leveling']

from cogs.leveling import Leveling

class TestLeveling(unittest.TestCase):
    def setUp(self):
        # Mock bot and database
        self.bot = MagicMock()
        self.bot.db = {"levels": MagicMock()}
        self.cog = Leveling(self.bot)

    def test_calc_level(self):
        """Test the level calculation logic with various XP values."""
        test_cases = [
            (0, 0),        # 0.1 * sqrt(0) = 0
            (50, 0),       # 0.1 * sqrt(50) ≈ 0.707 -> 0
            (100, 1),      # 0.1 * sqrt(100) = 1.0 -> 1
            (200, 1),      # 0.1 * sqrt(200) ≈ 1.414 -> 1
            (400, 2),      # 0.1 * sqrt(400) = 2.0 -> 2
            (900, 3),      # 0.1 * sqrt(900) = 3.0 -> 3
            (1000, 3),     # 0.1 * sqrt(1000) ≈ 3.162 -> 3
            (2500, 5),     # 0.1 * sqrt(2500) = 5.0 -> 5
            (10000, 10),   # 0.1 * sqrt(10000) = 10.0 -> 10
        ]

        for xp, expected_level in test_cases:
            with self.subTest(xp=xp):
                self.assertEqual(self.cog.calc_level(xp), expected_level)

if __name__ == "__main__":
    unittest.main()
