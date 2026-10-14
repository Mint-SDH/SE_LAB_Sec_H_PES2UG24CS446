"""
GameEngine: owns the paddle, ball, and bricks, orchestrating game flow.
"""

import pygame

from game.paddle import Paddle
from game.ball import Ball
from game.brick import Brick, NormalBrick, StrongBrick, UnbreakableBrick
from game.collision import handle_ball_brick_collision
from game.renderer import WIDTH, HEIGHT

BRICK_ROWS = 4
BRICK_COLS = 8
BRICK_WIDTH = 68
BRICK_HEIGHT = 22
BRICK_GAP = 6
BRICK_TOP_MARGIN = 55
MAX_LIVES = 3


class GameEngine:
    def __init__(self):
        self.paddle = Paddle(x=WIDTH / 2, y=HEIGHT - 30)
        self.ball = Ball(x=WIDTH / 2, y=HEIGHT - 50)
        self.bricks = self._build_bricks()
        self.lives = MAX_LIVES
        self.score = 0
        self.combo = 0
        self.game_state = "playing"  # "playing", "game_over", "won"

    def _build_bricks(self):
        bricks = []
        total_width = BRICK_COLS * (BRICK_WIDTH + BRICK_GAP) - BRICK_GAP
        start_x = (WIDTH - total_width) / 2

        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                x = start_x + col * (BRICK_WIDTH + BRICK_GAP)
                y = BRICK_TOP_MARGIN + row * (BRICK_HEIGHT + BRICK_GAP)

                if row == 0:
                    # Top row: Strong bricks (requires 2 hits, deep blue)
                    brick = StrongBrick(x, y, BRICK_WIDTH, BRICK_HEIGHT, hits_remaining=2)
                elif row == 2 and col in (2, 5):
                    # Obstacle bricks: Unbreakable (indestructible steel slate)
                    brick = UnbreakableBrick(x, y, BRICK_WIDTH, BRICK_HEIGHT)
                else:
                    # All normal bricks share the same consistent color (1 hit toughness)
                    brick = NormalBrick(x, y, BRICK_WIDTH, BRICK_HEIGHT)

                bricks.append(brick)
        return bricks

    def _reset_ball(self):
        """Reset ball and paddle to the starting position."""
        self.paddle.x = WIDTH / 2
        self.ball = Ball(x=WIDTH / 2, y=HEIGHT - 50)

    def restart(self):
        """Restart the entire game with fresh state."""
        self.lives = MAX_LIVES
        self.score = 0
        self.combo = 0
        self.game_state = "playing"
        self._reset_ball()
        self.bricks = self._build_bricks()

    def handle_input(self, keys_pressed):
        if self.game_state != "playing":
            return

        dx = 0
        if keys_pressed[pygame.K_LEFT]:
            dx -= self.paddle.speed
        if keys_pressed[pygame.K_RIGHT]:
            dx += self.paddle.speed
        self.paddle.move(dx, WIDTH)

    def handle_keydown(self, key):
        if self.game_state in ("game_over", "won"):
            if key in (pygame.K_r, pygame.K_SPACE, pygame.K_RETURN):
                self.restart()
        else:
            if key == pygame.K_r:
                self.restart()

    def update(self):
        if self.game_state != "playing":
            return

        self.ball.update()
        self.ball.bounce_off_walls(WIDTH)

        # Paddle collision
        if self.ball.get_rect().colliderect(self.paddle.get_rect()) and self.ball.vy > 0:
            self.ball.bounce_off_paddle(self.paddle.get_rect())

        # Brick collisions
        for brick in list(self.bricks):
            if handle_ball_brick_collision(self.ball, brick):
                destroyed = brick.hit()
                if not brick.is_unbreakable():
                    # Consecutive brick hits increase combo multiplier
                    self.combo += 1
                    base_pts = 100 if destroyed else 50
                    self.score += base_pts * self.multiplier

                    # Once hits are used up, remove brick from play
                    if destroyed or brick.hits_remaining <= 0:
                        self.bricks.remove(brick)
                break

        # Check win condition: all breakable bricks destroyed
        breakable_left = [b for b in self.bricks if not b.is_unbreakable()]
        if len(breakable_left) == 0:
            self.game_state = "won"
            return

        # Check if ball falls below paddle (life lost)
        if self.ball.is_below(HEIGHT):
            self.lives -= 1
            self.combo = 0  # Missing the ball resets the combo
            if self.lives > 0:
                self._reset_ball()
            else:
                self.game_state = "game_over"

    @property
    def multiplier(self):
        return max(1, self.combo)

    @property
    def breakable_count(self):
        return len([b for b in self.bricks if not b.is_unbreakable()])

    def draw(self, surface, font):
        from game import renderer
        renderer.draw_scene(surface, self.paddle, self.ball, self.bricks)
        renderer.draw_hud(
            surface,
            font,
            score=self.score,
            multiplier=self.multiplier,
            combo=self.combo,
            lives=self.lives,
            bricks_left=self.breakable_count,
        )

        if self.game_state == "game_over":
            renderer.draw_game_over(surface, font, self.score)
        elif self.game_state == "won":
            renderer.draw_victory(surface, font, self.score)
