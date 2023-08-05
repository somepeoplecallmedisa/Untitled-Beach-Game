import pygame

from engine._types import Position


class Camera:
    """
    Handles camera movement.
    The main advantage of this class over a simple Vector2 is ease of use
    """

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.scroll = pygame.Vector2(0, -48)
        self.screen_rect = pygame.Rect(self.scroll, (self.width, self.height))

    def apply(self, target_pos: Position) -> Position:
        """
        Adjusts the target pos to the current camera pos

        Parameters:
            target_pos: the target position to adjust
        """

        pos = (
            (target_pos[0] - self.scroll[0]),
            (target_pos[1] - self.scroll[1]),
        )
        return pos

    def adjust_to(self, dt: float, target_pos: pygame.Rect) -> None:
        """
        Smoothly adjusts the camera pos to the target pos

        Parameters:
            dt: deltatime
            target_pos: the target position to adjust to
        """

        self.scroll.x += (target_pos.x - self.scroll.x - self.width // 2) // 1
        self.scroll.y += (
            (target_pos.y - self.scroll.y - self.height // 1.5)
        ) // 1  # * dt

        self.scroll.y = min(self.scroll.y, 128)

        # this just works i dunno why
        self.screen_rect.center = self.apply(target_pos.topleft)
        self.screen_rect.y -= 24
