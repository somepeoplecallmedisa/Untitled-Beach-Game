import enum


class GameStates(enum.Enum):
    GAME = enum.auto()
    MENU = enum.auto()


class EntityStates(enum.Enum):
    IDLE = "idle"
    WALK = "walk"
    JUMP = "jump"
    TALK = "talk"
