"""
collision: ball-vs-brick collision handling.
"""


def handle_ball_brick_collision(ball, brick):
    """
    If the ball overlaps the brick, bounce it off in the correct direction and return True.
    Determines collision side (horizontal vs. vertical) based on overlap depth.
    """
    ball_rect = ball.get_rect()
    brick_rect = brick.get_rect()

    if not ball_rect.colliderect(brick_rect):
        return False

    # Overlaps from all 4 sides
    overlap_left = ball_rect.right - brick_rect.left
    overlap_right = brick_rect.right - ball_rect.left
    overlap_top = ball_rect.bottom - brick_rect.top
    overlap_bottom = brick_rect.bottom - ball_rect.top

    min_x = min(overlap_left, overlap_right)
    min_y = min(overlap_top, overlap_bottom)

    if min_x < min_y:
        # Side collision (left or right)
        if overlap_left < overlap_right:
            ball.x = brick_rect.left - ball.radius
            ball.vx = -abs(ball.vx)
        else:
            ball.x = brick_rect.right + ball.radius
            ball.vx = abs(ball.vx)
    else:
        # Top or bottom collision
        if overlap_top < overlap_bottom:
            ball.y = brick_rect.top - ball.radius
            ball.vy = -abs(ball.vy)
        else:
            ball.y = brick_rect.bottom + ball.radius
            ball.vy = abs(ball.vy)

    return True
