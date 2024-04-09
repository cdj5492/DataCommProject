from network.network_grid import NetworkGrid
from network.sim.file import init_routingcubes_from_file
from network.sim.recipe import Recipe
from routing_algorithms.template import Template as AlgoTemplate
from robot_algorithm.template import Template as RoboTemplate


def print_grid(grid:NetworkGrid):
    cubes = grid.get_all_nodes()
    for cube in cubes:
        print(cube)
    if (len(cubes) == 0):
        print("[empty grid]")
    print()


def main():
    cubes = init_routingcubes_from_file(r"data\networks\net1.txt")

    recipe = Recipe.from_file(r"data\recipes\net1_1.txt")
    print(recipe)

    # Workaround for bug in robot algorithm template
    robo_alg = RoboTemplate()
    robo_alg.step = lambda foo : None

    # Init NetworkGrid
    grid = NetworkGrid(AlgoTemplate(), robo_alg)
    for cube in cubes:
        x, y, z = cube.position
        grid.add_node(x, y, z, cube)
    print_grid(grid)

    while recipe.is_running():
        recipe.execute_next(grid)
        grid.step()
        print_grid(grid)


if __name__ == "__main__":
    main()
