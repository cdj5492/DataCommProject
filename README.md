# Routing Algorithm Viewer

## Running the Viewer

### Help

To get the help message, run `python app.py -h`.

### Available routing algorithms

- Source Routing: `rp`
- Bellman-Ford: `bmf`
- Random Walk: `rw`
- Spanning Tree: `mst`

### Example Running Simulation with Source Routing

`python3 app.py rp -n data/networks/demo3.txt -r data/recipes/demo3_3.txt --s 12`


## Adding new Features

### Implementing a New Routing Algorithm

1. Subclass `routing_algorithms.routing_algorithm.RoutingAlgorithm` and `robot_algorithm.robot_algorithm.RobotAlgorithm` to implement the new routing algorithm. (See `routing_algorithms.template.py` and `routing_algorithms.bellmanford.py` for examples.)
2. Import your `RoutingAlgorithm` and `RobotAlgorithm` classes to `app.support.py` and create and entry for them in `ROUTING_ALGOS`. The string name you give the algorithm will be used to select that algorithm on the CLI.

### Creating a New Node Color Configuration

1. Follow the guidelines and examples in `gui.color_conf.py` for creating a new configuration using the classes in `gui.utils.py`.
2. Import your color configuration (an instance of a `ColorConf` subclass or `ColorConfGroup`) to `app.support.py` and create and entry for it in `NODE_COLOR_CONFS`. The string name you give the color mode will be used to select it on the CLI and GUI.
