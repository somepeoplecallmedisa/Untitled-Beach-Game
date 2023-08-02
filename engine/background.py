from typing import Sequence, Tuple

import pygame


class ParallaxBackground:
    def __init__(
        self,
        #                      layer           speed
        layers: Sequence[Tuple[pygame.Surface, float]],
    ):
        self.layers = layers

    def draw_layer(
        self,
        screen: pygame.Surface,
        layer: pygame.Surface,
        scroll: pygame.Vector2,
        speed: float,
    ):
        width = screen.get_width()
        x = -scroll[0] * speed

        x %= width

        if abs(x) <= width:
            screen.blit(layer, (x, 0))
        if x != 0:
            screen.blit(layer, (x - width, 0))

    def draw(self, screen: pygame.Surface, world_scroll: pygame.Vector2):
        for layer, speed in self.layers:
            self.draw_layer(screen, layer, world_scroll, speed)
