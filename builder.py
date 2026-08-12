from typing import Any

from drone import Drone
from zone import Zone
from link import Link


def build(
        data: dict[str, Any]
        ) -> tuple[list[Drone], Zone, Zone, dict[str, Zone], list[Link]]:
    """Returns a tuple containing all necessary objects for the map.
    Objects are as follows:
    1. `drones`
    2. `start_hub`
    3. `end_hub`
    4. `zones`
    5. `links`
    """
    start = Zone(**data['start_hub'])
    end = Zone(**data['end_hub'])

    hubs: dict[str, Zone] = {x['name']: Zone(**x) for x in data['hubs']}
    hubs.update({start.name: start, end.name: end})

    drones = [Drone(f'D{i + 1}', start) for i in range(data['nb_drones'])]

    links: list[Link] = []
    for link in data['links']:
        links.append(Link(
            (hubs[link['hubs'][0]], hubs[link['hubs'][1]]),
            link.get('max_link_capacity', 1)
        ))

    return (
        drones,
        start,
        end,
        hubs,
        links
    )
