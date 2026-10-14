"""
renderer: all pygame drawing lives here, kept separate from game logic.
"""

import pygame

WIDTH, HEIGHT = 640, 520
WINDOW_SIZE = (WIDTH, HEIGHT)

COLOR_BG = (20, 20, 32)
COLOR_PADDLE = (80, 180, 255)
COLOR_PADDLE_ACCENT = (160, 220, 255)
COLOR_BALL = (245, 245, 250)
COLOR_TEXT = (255, 255, 255)
COLOR_GOLD = (255, 215, 0)
COLOR_RED = (255, 80, 80)
COLOR_GREEN = (80, 230, 140)


def draw_brick(surface, brick):
    """Draw a brick with visual styling based on its type and damage state."""
    rect = brick.get_rect()
    brick_type = getattr(brick, "brick_type", "normal")

    if brick_type == "unbreakable":
        # Unbreakable: Dark slate steel with silver border, center bar, and corner rivets
        pygame.draw.rect(surface, (95, 100, 110), rect, border_radius=2)
        pygame.draw.rect(surface, (185, 190, 200), rect, width=2, border_radius=2)
        # Center metallic divider
        pygame.draw.line(surface, (150, 155, 165), (rect.left + 5, rect.centery), (rect.right - 5, rect.centery), 2)
        # Corner rivets
        for cx, cy in [
            (rect.left + 5, rect.top + 5),
            (rect.right - 6, rect.top + 5),
            (rect.left + 5, rect.bottom - 6),
            (rect.right - 6, rect.bottom - 6),
        ]:
            pygame.draw.circle(surface, (215, 220, 230), (cx, cy), 2)

    elif brick_type == "strong":
        # Strong: Reinforced blue border and visible crack when damaged
        pygame.draw.rect(surface, brick.color, rect, border_radius=3)
        # 3D bevel top highlight
        pygame.draw.line(surface, (180, 220, 255), (rect.left + 2, rect.top + 1), (rect.right - 2, rect.top + 1), 2)
        # Outer border
        pygame.draw.rect(surface, (20, 60, 120), rect, width=2, border_radius=3)

        # If damaged, draw visible crack pattern
        if getattr(brick, "hits_remaining", 2) < getattr(brick, "max_hits", 2):
            crack_points = [
                (rect.left + 12, rect.top + 2),
                (rect.left + 24, rect.centery + 2),
                (rect.centerx + 4, rect.centery - 2),
                (rect.right - 14, rect.bottom - 3),
            ]
            pygame.draw.lines(surface, (255, 255, 255), False, crack_points, 2)
        else:
            # Undamaged: inner reinforced plate line
            inner_rect = rect.inflate(-8, -6)
            pygame.draw.rect(surface, (30, 90, 160), inner_rect, width=1)

    else:
        # Normal brick: Solid vibrant color with 3D bevel highlight
        pygame.draw.rect(surface, brick.color, rect, border_radius=2)
        # Top and left highlight
        hl_color = tuple(min(255, c + 45) for c in brick.color)
        pygame.draw.line(surface, hl_color, (rect.left + 1, rect.top + 1), (rect.right - 1, rect.top + 1), 2)
        pygame.draw.line(surface, hl_color, (rect.left + 1, rect.top + 1), (rect.left + 1, rect.bottom - 1), 1)
        # Dark outline
        border_color = tuple(max(0, c - 50) for c in brick.color)
        pygame.draw.rect(surface, border_color, rect, width=1, border_radius=2)


def draw_scene(surface, paddle, ball, bricks):
    surface.fill(COLOR_BG)

    # Bricks
    for brick in bricks:
        draw_brick(surface, brick)

    # Paddle with highlight
    p_rect = paddle.get_rect()
    pygame.draw.rect(surface, COLOR_PADDLE, p_rect, border_radius=4)
    pygame.draw.line(surface, COLOR_PADDLE_ACCENT, (p_rect.left + 4, p_rect.top + 2), (p_rect.right - 4, p_rect.top + 2), 2)

    # Ball
    pygame.draw.circle(surface, COLOR_BALL, (int(ball.x), int(ball.y)), ball.radius)
    pygame.draw.circle(surface, (200, 200, 215), (int(ball.x), int(ball.y)), ball.radius, width=1)


def draw_hud(surface, font, score, multiplier, combo, lives, bricks_left):
    """Draw the top HUD bar displaying score, combo multiplier, lives, and bricks left."""
    # Top HUD background line
    pygame.draw.line(surface, (45, 45, 60), (0, 38), (WIDTH, 38), 1)

    # Score
    draw_text(surface, font, f"Score: {score}", (15, 10), COLOR_TEXT)

    # Multiplier / Combo
    mult_text = f"Multiplier: {multiplier}x"
    mult_color = COLOR_GOLD if multiplier > 1 else (180, 180, 190)
    draw_text(surface, font, mult_text, (180, 10), mult_color)

    # Lives
    heart_symbols = "♥ " * max(0, lives)
    draw_text(surface, font, f"Lives: {heart_symbols.strip()}", (370, 10), COLOR_RED)

    # Bricks left
    draw_text(surface, font, f"Bricks: {bricks_left}", (530, 10), COLOR_TEXT)


def draw_game_over(surface, font, score):
    """Draw a Game Over overlay with restart instructions."""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((10, 10, 20, 200))
    surface.blit(overlay, (0, 0))

    big_font = pygame.font.SysFont("consolas", 40, bold=True)
    title = big_font.render("GAME OVER", True, COLOR_RED)
    title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
    surface.blit(title, title_rect)

    score_surf = font.render(f"Final Score: {score}", True, COLOR_TEXT)
    score_rect = score_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 5))
    surface.blit(score_surf, score_rect)

    prompt_surf = font.render("Press [R] or [SPACE] to Restart", True, COLOR_GOLD)
    prompt_rect = prompt_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 45))
    surface.blit(prompt_surf, prompt_rect)


def draw_victory(surface, font, score):
    """Draw a Victory overlay when all breakable bricks are cleared."""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((10, 10, 20, 200))
    surface.blit(overlay, (0, 0))

    big_font = pygame.font.SysFont("consolas", 36, bold=True)
    title = big_font.render("VICTORY! ALL BRICKS CLEARED!", True, COLOR_GOLD)
    title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
    surface.blit(title, title_rect)

    score_surf = font.render(f"Final Score: {score}", True, COLOR_GREEN)
    score_rect = score_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 5))
    surface.blit(score_surf, score_rect)

    prompt_surf = font.render("Press [R] or [SPACE] to Play Again", True, COLOR_TEXT)
    prompt_rect = prompt_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 45))
    surface.blit(prompt_surf, prompt_rect)


def draw_text(surface, font, text, pos, color=COLOR_TEXT):
    surface.blit(font.render(text, True, color), pos)


def draw_banner(surface, font, text):
    surf = font.render(text, True, COLOR_GOLD)
    rect = surf.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
    surface.blit(surf, rect)
