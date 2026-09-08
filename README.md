*This project has been created as part of the 42 curriculum by esnavarr*

# FlyIn

This project is a simulation of autonomous drones traversing a graph of connected hubs. Each drone starts from a designated start node and must reach a common goal while respecting node and link capacities, movement rules, and congestion effects. The program combines pathfinding, conflict avoidance, and a live visual representation in a single pygame-based application.

The central challenge is not only to find a valid route, but to do it efficiently in a multi-agent system. Drones must avoid collisions and bottlenecks while still advancing toward the destination. The simulation therefore mixes graph traversal with traffic-aware planning and real-time animation.

## Description

FlyIn models a multi-agent pathfinding problem inspired by MAPF-style coordination. A map is expressed as a set of hubs and links, where each hub can have special behaviors (blocked, restricted, priority, or normal), and each link can have a maximum allowed lane capacity.

A run proceeds as follows:

- a map is parsed from a text file
- hubs and links are converted into runtime objects
- drones are created at the start hub
- each drone computes a route toward the exit
- turns are executed one by one, with movement rules enforced
- the visual interface shows both the graph and the drones moving through it

The program is designed for both educational exploration and debugging: the visual layer makes congestion and movement rules easy to understand, while the terminal output shows each drone move as it occurs.

## Features

- Graph-based map definition using text input files
- Multi-drone pathfinding and movement coordination
- Node capacities and link capacities
- Special zone types:
  - normal
  - blocked
  - restricted
  - priority
- Traffic-aware path planning to reduce conflicts
- Interactive pygame visualization
- Autoplay mode for continuous simulation
- Mouse controls for stepping turns and panning the camera

## Instructions

### Requirements

- Python 3.13+
- uv (recommended)
- pygame
- lark
- webcolors

### Install and run

From the FlyIn project directory:

```bash
uv sync
make run
```

You can also launch it directly:

```bash
uv run .
```

If you want to open a specific map without the interactive menu, pass it as a command-line argument:

```bash
uv run . testmaps/basic.txt
```

### Controls

- Left mouse button: execute one turn
- Right mouse button: pan the camera
- Space bar: toggle autoplay
- Escape or window close: quit the simulation

### Available maps

The application automatically scans the `maps` and `testmaps` directories for `.txt` map files, prints them in a numbered list, and lets the user choose one.

## Resources

### Classic references and background

- MAPF overview: https://en.wikipedia.org/wiki/Multi-agent_pathfinding
- Dijkstra’s algorithm explanation: https://www.w3schools.com/dsa/dsa_algo_graphs_dijkstra.php
- Pygame documentation: https://www.pygame.org/docs/
- Cooperative pathfinding and conflict-focused planning ideas: https://arongranberg.com/2015/06/cooperative-pathfinding-experiments/
- Conflict-based search video: https://www.youtube.com/watch?v=FnrZyL6965o

### AI usage

AI assistance was used primarily as a planning and debugging aid during the project:

- brainstorming the overall architecture of the simulation
- helping verify the correctness of the graph and movement rules
- suggesting ways to structure the traffic-aware pathfinding logic
- reviewing the clarity and readability of the implementation
- prepare technical documentation

The AI was not used as a substitute for the project’s core reasoning; it was used to support design decisions, debugging, and prepare the documentation.

## Algorithm and implementation strategy

The project follows a graph-based approach using a weighted network of zones and links.

### 1. Parsing the map

Map files are read using a Lark grammar in `parser.py`. A valid map can include:

- number of drones
- start hub
- end hub
- intermediate hubs
- connections between hubs
- optional metadata such as zone type, color, and capacity

The parser validates:

- required map data exists
- hub names are unique
- links connect to valid hubs
- special metadata is well-formed

### 2. Building the simulation state

The `build()` function in `builder.py` creates:

- `Zone` objects for every hub
- `Link` objects for every connection
- `Drone` objects placed on the start position

Each `Link` registers itself with both connected zones, so each zone knows which neighbors it can reach.

### 3. Pathfinding with Dijkstra and traffic cost

Each drone computes a route using a Dijkstra-like shortest-path search. The algorithm is not applied blindly: it also accounts for congestion in the network.

The key idea is a traffic heuristic:

- drones are processed in priority order
- earlier drones make their path choices first
- those choices increase the cost of the affected zones for later drones

This means lower-priority drones will naturally prefer routes that are less crowded or more suitable.

The cost model is adjusted based on zone type:

- restricted zones have a higher movement cost
- priority zones have a lower cost
- blocked zones are skipped entirely

This makes the routing more realistic and reduces accidental collisions in dense traffic.

### 4. Movement rules and turn execution

The main simulation loop triggers a turn with `execute_turn()`. During a turn:

- each active drone attempts to move to the next node in its planned path
- the destination node is checked for capacity limits
- the link is checked for maximum simultaneous traffic
- restricted zones may delay the drone for an extra turn
- if the drone reaches the goal, it stops moving further

This ensures the simulation behaves like a controlled multi-agent transit system rather than a simple independent path animation.

## Visual representation and user experience

The visual layer is built with pygame, and it plays an important role in both debugging and presentation.

### What the visual representation adds

- distinguishes different zone types with color and appearance
- shows link capacities visually through stroke thickness
- overlays route labels and hub names
- animates drone movement smoothly between zones
- supports panning for exploring large maps
- allows autoplay for continuous observation
- makes congestion and blocked routes easier to understand at a glance

The interface also includes on-screen instructions so the user can immediately understand the controls without reading source code.

This visual feedback matters because the underlying logic is combinatorial: seeing the pathing decisions in motion makes the behavior far easier to reason about than reading only the terminal logs.

## Example input and expected output

### Example map file

```text
nb_drones: 1

start_hub: start 0 0 [color=black]
hub: a1 1 0
end_hub: end 2 0 [color=black]

connection: start-a1
connection: a1-end
```

This defines a very simple route where one drone starts at `start`, moves to `a1`, and then reaches `end`.

### What happens at runtime

When the map is loaded, the drone calculates a path and the simulation begins. If the player clicks the left mouse button to execute a turn, the terminal prints a move such as:

```text
D1-a1
```

After the next turn:

```text
D1-a1 D1-end
```

The visual window will show the drone moving along the path from the start node to the terminal node, with the end state being a drone located on the goal hub.

## Project structure

The main files are:

- `__main__.py`: program entry point and main event loop
- `parser.py`: grammar and map parsing logic
- `builder.py`: object construction from parsed map data
- `zone.py`: graph node definition and zone behavior
- `link.py`: connection definition and visual rendering
- `drone.py`: movement, pathfinding, and state management
- `assets.py`: asset loading and image coloring utilities
- `testmaps/`: example map inputs for validation and debugging

## Summary

FlyIn is a small but complete simulation of multi-agent graph navigation. It combines parsing, pathfinding, collision avoidance, congestion management, and interactive pygame visualization into a project that is both practical to run and instructive to study. The design emphasizes clarity of logic, understandable visual feedback, and a flexible input format that makes map experimentation easy.
