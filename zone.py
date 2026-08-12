from enum import Enum, auto
from dataclasses import dataclass, field

import pygame
from pygame import Vector2

import assets


class ZoneType(Enum):
    NORMAL = auto()      # Normal path.
    BLOCKED = auto()     # Inaccessible.
    RESTRICTED = auto()  # 2-turn movement.
    PRIORITY = auto()    # 1-turn, preferred if possible.
    START = auto()       # Start.
    END = auto()         # End.


@dataclass
class Zone:
    """Node in a network of zones that can be traversed by drones.

    Args:
        name: Name of the zone.
        x: Horizontal position.
        y: Vertical position.
        zonetype: Should be one of `ZoneType` enum. Specifies extra rules.
        color: Colors the image of the zone.
        max_drones: How many drones can occupy this zone at a time.
        neighbors: What zones is this zone connected to.
    """
    name: str
    x: int
    y: int
    zonetype: ZoneType = ZoneType.NORMAL
    color: str = 'white'
    max_drones: int = 1
    neighbors: list[tuple['Zone', int]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.drone_load = 0
        self.pos = Vector2(self.x * 128, self.y * 128)
        self.hovered = False

        self.img = assets.get_colored(
            f'zone_{self.zonetype.name.lower()}', self.color)
        self.rect = self.img.get_rect(center=self.pos)

        # Creating the zone's name label.
        self.nametext = pygame.font.Font.render(
            assets.FONT_BIG,
            f'{self.name}',
            True,
            (255, 255, 255),
            (0, 0, 0)
        )
        self.nametext_rect = self.nametext.get_rect(center=(800, 1100))

        # Creating the max_drones label.
        self.label = assets.IMG['label']
        self.label_rect = self.label.get_rect(
            left=self.pos.x - 64,
            top=self.pos.y - 32,
        )
        self.labeltext = pygame.font.Font.render(
            assets.FONT,
            f'{self.max_drones:>2}',
            True,
            (255, 255, 255)
        )
        self.labeltext_rect = self.labeltext.get_rect(
            left=self.pos.x + 16,
            top=self.pos.y + 19,
        )

    def draw(self, screen: pygame.Surface, offset: Vector2) -> None:
        "Draw this object to `screen` with camera `offset`."
        screen.blit(self.img, self.rect.move(offset))
        if self.max_drones != 1:
            screen.blit(self.label, self.label_rect.move(offset))
            screen.blit(
                self.labeltext,
                self.labeltext_rect.move(offset),
                (0, 0, 128, 21)
            )
