from dataclasses import dataclass
from typing import TypedDict

import pygame
from pygame import Vector2

import assets
from zone import Zone, ZoneType
from link import Link


class DijkstraTableEntry(TypedDict):
    zone: Zone
    cost: float
    prev: Zone | None


@dataclass
class Drone:
    """Drone that moves between nodes.

    Args:
        name: Name of the drone.
        zone: Starting zone.
    """
    name: str
    zone: Zone

    def __post_init__(self) -> None:
        self.pos = Vector2(0, 0)
        self.speed = Vector2(0, 0)
        self.img = assets.IMG['drone']
        self.alt_img = assets.get_colored('drone', 'black')
        self.rect = self.img.get_rect(center=(self.pos.x, self.pos.y))
        self.lagged = False
        self.path: list[Zone] = []

        self.zone.drone_load += 1

    def move(self, links: list[Link]) -> None:
        """Move to the next zone."""
        if not self.path:
            return
        if self.lagged:
            self.lagged = False
            self.img, self.alt_img = self.alt_img, self.img
            return
        dest = self.path[0]

        # Get and set the link load and capacity.
        link_cap, link_load = 0, 0
        key = "-".join(sorted([self.zone.name, dest.name]))
        for x in links:
            if str(x) == key:
                link_cap, link_load = x.max_link_capacity, x.drone_load
                x.drone_load += 1
                break

        if dest.zonetype != ZoneType.END:
            if dest.drone_load >= dest.max_drones or link_load >= link_cap:
                return
        if dest.zonetype == ZoneType.RESTRICTED:
            self.lagged = True
            self.img, self.alt_img = self.alt_img, self.img
        print(f'{self.name}-{dest.name}', end=' ')
        self.zone.drone_load -= 1
        dest.drone_load += 1
        self.zone = self.path.pop(0)

    def dijkstras(
            self,
            graph: list[Zone],
            goal: Zone,
            traffic: dict[str, int]
            ) -> list[Zone]:
        """Implementation of Dijkstra's algorithm.

        Args:
            graph: List of all zones that make up the network.
            goal: Zone to find a path to.
            traffic: Map of congestion for each node.

        Returns:
            List of zones that make up the path,
            or an empty list if no path could be found."""
        # Make a table with the necessary information for each zone.
        g: dict[str, DijkstraTableEntry] = {
            x.name: {
                'zone': x,
                'cost': float('inf'),
                'prev': None
            }
            for x in graph
        }

        visited = set()
        queue = [self.zone]
        g[self.zone.name]['cost'] = 0

        while queue:
            for z, i in queue[0].neighbors:
                if z.zonetype == ZoneType.BLOCKED:
                    continue
                if z.name not in visited:
                    queue.append(z)

                current = g[queue[0].name]
                neighbor = g[z.name]
                distance = 100 + (100 * traffic[z.name])
                if neighbor['zone'].zonetype == ZoneType.RESTRICTED:
                    distance *= 2
                if neighbor['zone'].zonetype == ZoneType.PRIORITY:
                    distance //= 2
                if current['cost'] + distance < neighbor['cost']:
                    neighbor['cost'] = current['cost'] + distance
                    neighbor['prev'] = current['zone']

            visited.add(queue[0].name)
            queue.pop(0)

        # Collapse the path.
        path: list[Zone] = []
        current = g[goal.name]
        while current['prev']:
            path.append(current['zone'])
            current = g[current['prev'].name]
        path.reverse()

        self.path = path
        return path

    def update(self) -> None:
        "Update this object's visual information."
        self.speed *= 0.75
        wishdir = self.zone.pos - self.pos
        if wishdir.length() > 32:
            self.speed += (self.zone.pos - self.pos).normalize() * 3
        else:
            self.speed *= 0.5
        self.pos += self.speed

    def draw(self, screen: pygame.Surface, offset: Vector2) -> None:
        "Draw this object to `screen` with camera `offset`."
        screen.blit(self.img, self.rect.move(self.pos + offset))
