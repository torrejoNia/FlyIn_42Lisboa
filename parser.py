from pathlib import Path
from typing import Any, TypedDict

from lark import Lark, Transformer

from zone import Zone, ZoneType
from link import Link


class TransformedTree(TypedDict):
    nb_drones: int | None
    start_hub: dict[str, Any] | None
    end_hub: dict[str, Any] | None
    hubs: list[Zone]
    links: list[Link]


class ParsingError(Exception):
    pass


class TreeToMap(Transformer[Any, TransformedTree]):
    "Transforms a `ParseTree` into a dictionary used to build a Fly-In graph."
    @staticmethod
    def __validate_unique(name: str, registry: set[str]) -> None:
        if name in registry:
            raise ParsingError(f'"{name}" is duplicated.')
        registry.add(name)

    def VALIDZONE(self, token: Any) -> ZoneType:
        return ZoneType[str(token).upper()]

    def ALPHA(self, token: Any) -> str:
        return str(token)

    def ALNUM(self, token: Any) -> str:
        return str(token)

    def INT(self, token: Any) -> int:
        return int(token)

    def ABOVE_ZERO(self, token: Any) -> int:
        return int(token)

    def meta_zone(self, items: Any) -> dict[str, Any]:
        return {"zonetype": items[0]}

    def meta_color(self, items: Any) -> dict[str, Any]:
        return {"color": items[0]}

    def meta_max(self, items: Any) -> dict[str, Any]:
        return {"max_drones": items[0]}

    def meta_link(self, items: Any) -> dict[str, Any]:
        return {"max_link_capacity": items[0]}

    def start_hub(self, items: Any) -> tuple[str, dict[str, Any]]:
        name, x, y, *meta = items
        metadata = {k: v for d in meta for k, v in d.items()}
        if 'zonetype' not in metadata:
            metadata['zonetype'] = ZoneType.START
        return ("start_hub", {"name": name, "x": x, "y": y} | metadata)

    def end_hub(self, items: Any) -> tuple[str, dict[str, Any]]:
        name, x, y, *meta = items
        metadata = {k: v for d in meta for k, v in d.items()}
        if 'zonetype' not in metadata:
            metadata['zonetype'] = ZoneType.END
        return ("end_hub", {"name": name, "x": x, "y": y} | metadata)

    def any_hub(self, items: Any) -> tuple[str, dict[str, Any]]:
        name, x, y, *meta = items
        metadata = {k: v for d in meta for k, v in d.items()}
        return ("hub", {"name": name, "x": x, "y": y} | metadata)

    def connection(self, items: Any) -> tuple[str, dict[str, Any]]:
        a, b, *meta = items
        metadata = meta[0] if meta else {}
        return ("link", {'hubs': (a, b)} | metadata)

    def nb_drones(self, items: Any) -> tuple[str, Any]:
        return ("nb_drones", items[0])

    def start(self, items: Any) -> TransformedTree:
        result: TransformedTree = {
            "nb_drones": None,
            "start_hub": None,
            "end_hub": None,
            "hubs": [],
            "links": []
        }
        registry: set[str] = set()
        for item in items:
            match item[0]:
                case "nb_drones":
                    result["nb_drones"] = item[1]

                case "start_hub":
                    if result['start_hub'] is not None:
                        raise ParsingError('"start_hub" key is duplicated.')
                    self.__validate_unique(item[1]['name'], registry)
                    result["start_hub"] = item[1]

                case "end_hub":
                    if result['end_hub'] is not None:
                        raise ParsingError('"end_hub" key is duplicated.')
                    self.__validate_unique(item[1]['name'], registry)
                    result["end_hub"] = item[1]

                case "hub":
                    self.__validate_unique(item[1]['name'], registry)
                    result["hubs"].append(item[1])

                case "link":
                    self.__validate_unique(
                        '-'.join(sorted(item[1]['hubs'])), registry)
                    result["links"].append(item[1])
        return result


def parse(filename: Path) -> dict[str, Any]:
    """Parse map data from a file.

    Args:
        filename: Path to read from.

    Returns:
        Dictionary containing data to be used for building the map.
        All hubs are given as dictionaries, and can be unpacked
        to build the hub objects (`Zone(**hub)`).

        Links/connections are tuples of `(from, to, capacity)`.
        - `nb_drones` - Number of drones.
        - `start_hub` - Starting hub.
        - `end_hub` - End hub.
        - `hubs` - List of hubs, excluding start and end hubs.
        - `links` - List of links.

    Raises:
        LarkError: When the input map file contains Lark parser errors.
        ParsingError: When the input map file contains miscellaneous errors.
    """

    grammar = r"""
start: nb_drones hub* connection*

?hub: start_hub
    | end_hub
    | any_hub

nb_drones: "nb_drones:" ABOVE_ZERO
start_hub: "start_hub:" ALNUM INT INT _hub_metadata?
end_hub: "end_hub:" ALNUM INT INT _hub_metadata?
any_hub: "hub:" ALNUM INT INT _hub_metadata?
connection: "connection:" ALNUM "-" ALNUM _link_metadata?

_hub_metadata: "[" meta_hub+ "]"
_link_metadata: "[" meta_link "]"

?meta_hub: meta_zone
         | meta_color
         | meta_max

meta_zone: "zone" "=" VALIDZONE
meta_color: "color" "=" ALPHA
meta_max: "max_drones" "=" ABOVE_ZERO
meta_link: "max_link_capacity" "=" ABOVE_ZERO

VALIDZONE: "normal" | "blocked" | "restricted" | "priority"

ALNUM: /[a-zA-Z_][a-zA-Z0-9_]*/
ALPHA: /[a-zA-Z_]+/
INT: /-?\d+/
ABOVE_ZERO: /[1-9][0-9]*/

COMMENT: /#[^\n]*/

%import common.WS
%ignore WS
%ignore COMMENT
    """

    map_parser = Lark(grammar, parser='lalr', transformer=TreeToMap())
    with filename.open("r", encoding="utf-8") as file:
        tree = map_parser.parse(file.read())
        assert isinstance(tree, dict)

        # Checking that critical data is supplied.
        missing = {x for x in tree if tree[x] is None}
        if missing:
            raise ParsingError(f'Critical map data is missing: {missing}.')

        # Checking that links connect to valid hubs.
        all_hubs = [x['name'] for x in tree['hubs']] \
            + [tree['start_hub']['name'], tree['end_hub']['name']]
        for link in tree['links']:
            if link['hubs'][0] not in all_hubs \
                    or link['hubs'][1] not in all_hubs:
                raise ParsingError(
                    f'Link "{"-".join(link['hubs'])}"'
                    ' connects to an invalid hub.')

        return tree
