from typing import Union

import pygame

from engine._types import Position
from engine.animations import Animation
from engine.tilemap import TileLayerMap
from src.common import TILE_SIZE


def render_outline_text(text: str, font: pygame.Font, color, wraplength=196, width=1):
    rendered_text = font.render(text, False, color, wraplength=wraplength)
    outline = font.render(text, False, "black", wraplength=wraplength)

    master_surf = pygame.Surface(
        (rendered_text.get_width() + width * 2, rendered_text.get_height() + width * 2),
        pygame.SRCALPHA,
    )
    offsets = (
        (0, width),
        (width, 0),
        (width * 2, width),
        (width, width * 2),
    )
    for point in offsets:
        master_surf.blit(outline, point)
    master_surf.blit(rendered_text, (width, width))

    return master_surf


def reverse_animation(anim: Animation):
    """Reverse frames in a given Animation"""

    new_frames = [pygame.transform.flip(frame, True, False) for frame in anim.frames]

    return Animation(new_frames, anim.speed)


def get_neighboring_tiles(tilemap: TileLayerMap, radius: int, tile_pos: pygame.Vector2):
    """
    Gets the nearest `radius` tiles from `tile_pos`

    Parameters:
        tilemap: The tilemap class to extract the information
        radius: The desired radius of tiles to include
        tile_pos: The tile position
    """
    neighboring_tile_entities = []

    for x in range(int(tile_pos.x) - radius, int(tile_pos.x) + radius + 1):
        for y in range(int(tile_pos.y) - radius, int(tile_pos.y) + radius + 1):
            try:
                tile = tilemap.tiles[(x, y)]
            except KeyError:
                # Outside map boundaries (for some reason)
                continue

            neighboring_tile_entities.append(tile)

    return neighboring_tile_entities


def pixel_to_tile(
    pixel_pos: Position,
) -> pygame.Vector2:
    return pygame.Vector2(
        round(pixel_pos.x / TILE_SIZE), round(pixel_pos.y / TILE_SIZE)
    )


class Expansion:
    """
    Number expansion and contraption
    """

    def __init__(
        self,
        number: float,
        lower_limit: float,
        upper_limit: float,
        speed: float,
    ):
        self.number = number
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        self.speed = speed

    def update(self, cond: bool, dt: float):
        if cond:
            if self.number < self.upper_limit:
                self.number += self.speed * dt
        else:
            if self.number > self.lower_limit:
                self.number -= self.speed * dt
