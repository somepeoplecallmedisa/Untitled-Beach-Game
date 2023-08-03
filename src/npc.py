from typing import Sequence

import pygame
from pytmx import TiledObject

from engine._types import EventInfo, Position
from engine.animations import Animation
from engine.camera import Camera
from engine.utils import Expansion, render_outline_text, reverse_animation
from src.common import FONT_PATH
from src.player import Player

pygame.font.init()


class TalkingNPC:
    TEXT_WRAPLENGTH = 196
    FONT = pygame.Font(FONT_PATH, 8)

    def __init__(self, assets: dict, obj: TiledObject):
        self.animations = {
            "left_idle": Animation(assets[f"{obj.name}_idle"], 0.1),
            "left_talk": Animation(assets[f"{obj.name}_talk"], 0.6),
        }
        self.animations |= {
            "right_idle": reverse_animation(self.animations["left_idle"]),
            "right_talk": reverse_animation(self.animations["left_talk"])
        }

        self.state = "left_idle"

        # in case the object's size is incorrect
        obj_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
        self.rect = (
            self.animations["left_idle"]
            .frames[0]
            .get_rect(midbottom=(obj_rect.midbottom))
        )

        self.pos = pygame.Vector2(self.rect.topleft)

        # alpha expansion for the text
        self.alpha_expansion = Expansion(0, 0, 255, 25)

        # two newlines indicate a line said by the NPC
        lines = obj.properties["text"].split("\n\n")
        self.render_text_default(lines)

        self.interacting = False
        self.talking = False

    def render_text_default(self, lines: Sequence[str]):
        """
        Renders the NPC's speech and inserts a default line at the start
        """
        self.lines = [render_outline_text(line, self.FONT, "white") for line in lines]

        # start at a default line
        default_text = render_outline_text("Press E to talk", self.FONT, "white")
        self.lines.insert(0, default_text)

        self.line_index = 0
        self.text_surf = self.lines[self.line_index]

        self.text_surf.set_alpha(int(self.alpha_expansion.number))

    def render_text(self, lines: Sequence[str]):
        """
        Renders the NPC's speech and (no default line)
        """
        self.lines = [render_outline_text(line, self.FONT, "white") for line in lines]

        self.line_index = 0
        self.text_surf = self.lines[self.line_index]

        self.text_surf.set_alpha(int(self.alpha_expansion.number))

    def handle_states(self, player: Player):
        direction = "left"
        if player.rect.x > self.pos.x:
            direction = "right"

        action = "talk" if self.interacting and self.talking else "idle"

        self.state = f"{direction}_{action}"

    def update(self, event_info: EventInfo, player: Player):
        self.interacting = self.rect.colliderect(player.rect)

        # handle E key presses, change the text lines
        if self.interacting:
            for event in event_info["events"]:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                    self.talking = True
                    if self.line_index < len(self.lines) - 1:
                        self.line_index += 1
                        self.text_surf = self.lines[self.line_index]

        self.alpha_expansion.update(self.interacting, event_info["dt"])
        self.text_surf.set_alpha(int(self.alpha_expansion.number))

        self.handle_states(player)

    def draw(self, screen: pygame.Surface, camera: Camera, event_info: EventInfo):
        self.animations[self.state].play(
            screen, camera.apply(self.pos), event_info["dt"]
        )
        text_pos = self.text_surf.get_rect(
            midbottom=(self.rect.centerx, self.rect.top - 2)
        ).topleft
        screen.blit(self.text_surf, camera.apply(text_pos))


class QuestGiverNPC(TalkingNPC):
    def __init__(self, assets: dict, obj):
        super().__init__(assets, obj)

        self.item = obj.properties["item"]
        self.text_if_item = obj.properties["text_if_item"]
        self.exclamation = assets["exclamation"]
        self.exclamation_pos = self.exclamation.get_rect(midbottom=(self.rect.centerx, self.rect.top - 2))
        
        self.quest_done = False
        self.check_finished = False
        self.quest_ongoing = False

    def update(self, event_info: EventInfo, player: Player):
        super().update(event_info, player)

        self.quest_done = self.item in player.settings["items_delivered"]
        self.quest_ongoing = self.item in player.settings["inventory"]

        # if the quest was already done
        if self.quest_done and not self.check_finished:
            # we only need to execute this once
            self.check_finished = True
            lines = self.text_if_item.split("\n\n")
            self.render_text_default(lines)

        # if the quest is starting
        elif self.talking and not self.quest_ongoing and not self.quest_done:
            player.settings["inventory"].append(self.item)

    def draw(self, screen: pygame.Surface, camera: Camera, event_info: EventInfo):
        # the exclamation point should be in the background
        if not self.quest_done and not self.quest_ongoing and not self.talking:
            screen.blit(self.exclamation, camera.apply(self.exclamation_pos))
        
        super().draw(screen, camera, event_info)


class QuestReceiverNPC(TalkingNPC):
    def __init__(self, assets: dict, obj):
        super().__init__(assets, obj)

        self.item = obj.properties["item"]
        self.text_if_item = obj.properties["text_if_item"]
        self.check_finished = False

    def update(self, event_info: EventInfo, player: Player):
        super().update(event_info, player)

        self.quest_done = self.item in player.settings["items_delivered"]
        self.quest_ongoing = self.item in player.settings["inventory"]

        # if the quest was already finished
        if not self.talking and self.quest_done and not self.check_finished:
            lines = self.text_if_item.split("\n\n")
            self.render_text_default(lines)
            # we only need to check for this once
            self.check_finished = True

        # if player finished the quest and the text
        # hasn't been rendered already
        if self.talking and self.item in player.settings["inventory"]:
            lines = self.text_if_item.split("\n\n")
            self.render_text(lines)

            player.settings["inventory"].remove(self.item)
            player.settings["items_delivered"].append(self.item)
            player.settings["seashells"] += 1
