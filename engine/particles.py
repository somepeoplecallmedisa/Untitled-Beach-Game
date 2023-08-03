import pygame
from engine._types import Position
from engine.camera import Camera

class FadingOutText:
    def __init__(
        self,
        image: pygame.Surface,
        pos: Position,
        alpha_speed: int,
        starting_alpha: int = 255,
        lifespan: int = 0,
    ):
        self.image = image
        self.alpha = starting_alpha
        self.pos = pygame.Vector2(pos)
        self.alpha_speed = alpha_speed
        self.alive = True

    def update(self, delta_time: float):
        self.alpha -= self.alpha_speed * delta_time
        self.image.set_alpha(self.alpha)

        if self.alpha <= 0:
            self.alive = False

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.pos)