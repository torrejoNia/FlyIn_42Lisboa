from dataclasses import dataclass

import pygame
from pygame import Vector2

from zone import Zone


@dataclass
class Link:
    """Links two zones together.

    Args:
        hubs: Tuple of two zones to link.
        max_link_capacity: How many drones can move on this link per turn.
    """
    hubs: tuple[Zone, Zone]
    max_link_capacity: int = 1

    def __post_init__(self) -> None:
        self.hubs[0].neighbors.append((self.hubs[1], self.max_link_capacity))
        self.hubs[1].neighbors.append((self.hubs[0], self.max_link_capacity))
        self.drone_load = 0

        self.start = self.hubs[0].pos
        self.end = self.hubs[1].pos
        self.thickness = min(6 * self.max_link_capacity, 48)

    def __str__(self) -> str:
        return "-".join(sorted([self.hubs[0].name, self.hubs[1].name]))

    def draw(self, screen: pygame.Surface, offset: Vector2) -> None:
        "Draw this object to `screen` with camera `offset`."
        pygame.draw.line(
            screen,
            (0, 0, 0),
            self.start + offset,
            self.end + offset,
            self.thickness + 6,
        )
        pygame.draw.line(
            screen,
            (255, 255, 255),
            self.start + offset,
            self.end + offset,
            self.thickness,
        )
