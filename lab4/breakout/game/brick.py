"""
Brick: destructible and indestructible blocks for Breakout.
"""

import pygame


class Brick:
    """Base class for all bricks."""

    def __init__(self, x, y, width, height, hits_remaining=1, color=(200, 90, 90), brick_type="normal"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.max_hits = hits_remaining
        self.hits_remaining = hits_remaining
        self.color = color
        self.brick_type = brick_type

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def hit(self):
        """
        Called when a ball hits this brick.
        Reduces hits_remaining (if breakable) and returns True if destroyed.
        """
        if self.is_unbreakable():
            return False
        self.hits_remaining -= 1
        return self.is_destroyed()

    def is_destroyed(self):
        """Check if the brick has run out of hits."""
        if self.is_unbreakable():
            return False
        return self.hits_remaining <= 0

    def is_unbreakable(self):
        """Check if this brick is indestructible."""
        return self.brick_type == "unbreakable"


class NormalBrick(Brick):
    """Normal brick: destroyed after a single hit."""

    def __init__(self, x, y, width, height, color=(230, 75, 75)):
        super().__init__(x, y, width, height, hits_remaining=1, color=color, brick_type="normal")


class StrongBrick(Brick):
    """Strong brick: requires multiple hits (default 2) before it is destroyed."""

    def __init__(self, x, y, width, height, hits_remaining=2, color=(50, 140, 225)):
        super().__init__(x, y, width, height, hits_remaining=hits_remaining, color=color, brick_type="strong")
        self.initial_color = color

    def hit(self):
        destroyed = super().hit()
        # When damaged, shift color and appearance to visually indicate damage
        if not destroyed and self.hits_remaining == 1:
            self.color = (130, 195, 245)
        return destroyed


class UnbreakableBrick(Brick):
    """Unbreakable brick: never destroyed no matter how many times it is hit."""

    def __init__(self, x, y, width, height, color=(125, 130, 140)):
        super().__init__(x, y, width, height, hits_remaining=float("inf"), color=color, brick_type="unbreakable")

    def hit(self):
        # Indestructible
        return False

    def is_destroyed(self):
        return False
