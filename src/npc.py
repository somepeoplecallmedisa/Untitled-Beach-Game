import pygame
from pytmx import TiledObject

from engine._types import EventInfo, Position
from engine.animations import Animation
from engine.camera import Camera
from engine.enums import EntityStates
from engine.utils import Expansion, render_outline_text, reverse_animation
from src.common import FONT_PATH
from src.player import Player

pygame.font.init()


class TalkingNPC:
    TEXT_WRAPLENGTH = 196

    def __init__(self, assets: dict, obj: TiledObject):
        self.animations = {
            EntityStates.IDLE: Animation(assets[f"{obj.name}_idle"], 1),
            EntityStates.TALK: Animation(assets[f"{obj.name}_talk"], 0.2),
        }

        self.state = EntityStates.IDLE

        self.rect = pygame.Rect((obj.x, obj.y), (32, 32))
        self.pos = pygame.Vector2(self.rect.topleft)

        self.image = pygame.Surface((32, 32))
        pygame.draw.rect(self.image, "green", (0, 0, 32, 32), 1)

        self.render_text(obj.properties["text"])

        self.interacting = False

    def render_text(self, text: str):
        font = pygame.Font(FONT_PATH, 16)
        self.text_surf = render_outline_text(text, font, "white")

        text_rect = self.text_surf.get_rect(
            midbottom=(self.rect.centerx, self.rect.top - 5)
        )
        self.text_pos = pygame.Vector2(text_rect.topleft)

        self.alpha_expansion = Expansion(0, 0, 255, 25)
        self.text_surf.set_alpha(int(self.alpha_expansion.number))

    def handle_states(self):
        self.state = EntityStates.TALK if self.interacting else EntityStates.IDLE

    def update(self, event_info: EventInfo, player: Player):
        self.interacting = self.rect.colliderect(player.rect)

        self.alpha_expansion.update(self.interacting, event_info["dt"])
        self.text_surf.set_alpha(int(self.alpha_expansion.number))

        self.handle_states()

    def draw(self, screen: pygame.Surface, camera: Camera, event_info: EventInfo):
        self.animations[self.state].play(
            screen, camera.apply(self.pos), event_info["dt"]
        )
        screen.blit(self.text_surf, camera.apply(self.text_pos))


class QuestGiverNPC(TalkingNPC):
    def __init__(self, assets: dict, obj):
        super().__init__(assets, obj)

        self.item = obj.properties["item"]

    def update(self, event_info: EventInfo, player: Player):
        super().update(event_info, player)

        if self.interacting and self.item not in player.inventory:
            player.inventory.append(self.item)


class QuestReceiverNPC(TalkingNPC):
    def __init__(self, assets: dict, obj):
        super().__init__(assets, obj)

        self.item = obj.properties["item"]
        self.text_if_item = obj.properties["text_if_item"]
        self.text_rendered = False

    def update(self, event_info: EventInfo, player: Player):
        super().update(event_info, player)

        # if player finished the quest and the text
        # hasn't been rendered already
        if (
            self.interacting
            and self.item in player.inventory
            and not self.text_rendered
        ):
            self.text_rendered = True
            self.render_text(self.text_if_item)
