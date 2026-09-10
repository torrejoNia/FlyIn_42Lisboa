import argparse
import sys
from pathlib import Path

from lark import LarkError

from assets import Assets
from builder import Builder
from drone import Drone
from formatting import D, H, R, X, Y
from link import Link
from parser import ParsingError, Parser
from render import Renderer
from zone import Zone


class FlyInApp:
    def __init__(self) -> None:
        self.turncount = 0
        self.capacity_info = False
        self.parser = Parser()
        self.builder = Builder()
        self.renderer = Renderer()

    def print_capacity_info(
            self, zones: dict[str, Zone], links: list[Link]) -> None:
        "Print the current occupancy of all zones and links."
        print(f'{D}Capacity information:{X}')
        for zone in zones.values():
            print(
                f'Zone {zone.name}: '
                f'{zone.drone_load}/{zone.max_drones} drones'
            )
        for link in links:
            print(
                f'Connection {link}: '
                f'{link.drone_load}/{link.max_link_capacity} capacity used'
            )
        print()

    def execute_turn(
            self,
            goal: Zone,
            drones: list[Drone],
            links: list[Link],
            zones: dict[str, Zone] | None = None) -> None:
        "Allow all drones to make a move towards the goal."
        if all(drone.zone is goal for drone in drones):
            return
        self.turncount += 1
        for link in links:
            link.drone_load = 0
        for drone in drones:
            if drone.zone is goal:
                continue
            drone.move(links)
        if self.capacity_info and zones is not None:
            self.print_capacity_info(zones, links)
        print()

    def list_maps(self, directory: Path, index: int = 0) -> list[Path]:
        "Print all maps in a directory, recursively."
        result = []
        print(f'\n{H}{directory}/{X}')
        for file in directory.iterdir():
            if not file.is_dir() and file.suffix == '.txt':
                result += [file]
                print(
                    f'{index:>4}.', str(file)
                    .removeprefix(str(directory) + '/')
                    .removesuffix('.txt'))
                index += 1
        for file in directory.iterdir():
            if file.is_dir():
                recursive_result = self.list_maps(file, index)
                index += len(recursive_result)
                result += recursive_result
        return result

    def parse_args(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser(
            description='FlyIn drone routing simulation.',
        )
        parser.add_argument(
            '--capacity-info',
            action='store_true',
            help=(
                'Display zone and connection capacity usage '
                'after every turn.'
            ),
        )
        parser.add_argument(
            'map',
            nargs='?',
            help=(
                'Optional path to a map file. '
                'If omitted, an interactive menu is shown.'
            ),
        )
        return parser.parse_args()

    def run(self) -> None:
        args = self.parse_args()
        self.capacity_info = args.capacity_info

        if args.map is not None:
            data = Path(args.map)
        else:
            print(
                f'{D}No map argument given, '
                'defaulting to interactive mode.'
                f'{X}'
            )

            try:
                maps = []
                path_maps = Path('maps')
                if path_maps.exists():
                    maps += self.list_maps(path_maps)
                maps += self.list_maps(Path('testmaps'), len(maps))
            except OSError as e:
                print(
                    f'{R}An error occurred while displaying map names.{X}',
                    file=sys.stderr
                )
                print(f'{R}Error: {e}{X}', file=sys.stderr)
                sys.exit(1)

            map_index = int(input('Input index of map to load: ' + H))
            if 0 <= map_index < len(maps):
                data = Path(maps[map_index])
            else:
                print(
                    f'{R}Error: input must be an integer'
                    f' between 0 and {len(maps) - 1}.{X}',
                    file=sys.stderr
                )
                sys.exit(1)
            print(X)

        try:
            Assets.load_assets(Path('assets'))
            drones, _start, end, zones, links = self.builder.build(
                self.parser.parse(data)
            )
        except (ParsingError, LarkError, OSError) as e:
            print(f'{R}Error: {e}{X}', file=sys.stderr)
            sys.exit(1)

        traffic = {x: 0 for x in zones}
        for drone in drones:
            for zone in drone.dijkstras(list(zones.values()), end, traffic):
                traffic[zone.name] += 1
        if any(not drone.path for drone in drones):
            print(
                f'{Y}Warning: Drones could not find a path to the exit.{X}',
                file=sys.stderr
            )

        self.renderer.run(drones, end, zones, links, self.execute_turn)
        print(f'{D}Turn count: {self.turncount}{X}')


if __name__ == '__main__':
    try:
        FlyInApp().run()
    except KeyboardInterrupt:
        print()
