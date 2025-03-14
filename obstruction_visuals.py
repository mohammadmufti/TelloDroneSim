import random
from obstructions import (CylindricalObstruction, RectangularObstruction,
                         PyramidalObstruction, SphereObstruction, CompositeObstruction)

"""This method is used to create visual obstructions for the simulation"""
def create_obstructions():
    obstructions = []
    obstructions.append(CylindricalObstruction((100, -700, 0), 20, 150, color=(0.6, 0.7, 0.6)))
    obstructions.append(RectangularObstruction((-200, 100, 0), (40, 40, 30), color=(0.5, 0.5, 0.5), rotation=45))
    obstructions.append(RectangularObstruction((400, -700, 0), (100, 100, 100), color=(0.5, 0.5, 0.5)))
    obstructions.append(create_basic_house_1((-500, 200, 0)))
    obstructions.append(create_basic_tree_1((0, -700, 0)))

    # Generate random trees near y=1000
    num_trees = 20  # Adjust as desired
    for _ in range(num_trees):
        x = random.uniform(-1000, 1000)  # Random x within 2000x2000 grid
        y = random.uniform(600, 1000)  # y between 800 and 1000 (900 ± 100)
        z = 0  # Ground level
        trunk_height = random.uniform(100, 400)  # Random height between 300 and 700
        trunk_radius = random.uniform(10, 20)  # Slightly varied trunk width
        canopy_radius = random.uniform(40, 75)  # Varied canopy size
        tree = create_basic_tree_1((x, y, z), trunk_radius, trunk_height, canopy_radius)
        obstructions.append(tree)

    return obstructions

def create_basic_house_1(position, color=(0.5, 0.5, 0.5)):
    building = CompositeObstruction(position, color)
    building.add_component(RectangularObstruction, (0, 0, 0), (500, 500, 300), color=(0.7, 0.7, 0.7))
    building.add_component(PyramidalObstruction, (0, 0, 300), (500, 500), 150, color=(0.2, 0.2, 0.7))
    building.add_component(SphereObstruction, (0, 0, 450), 20, color=(1.0, 0.8, 0.0))
    pillar_positions = [(-240, -240, 0), (240, -240, 0), (-240, 240, 0), (240, 240, 0)]
    for pos in pillar_positions:
        building.add_component(CylindricalObstruction, pos, 10, 300, color=(0.6, 0.6, 0.6))
    return building

def create_basic_tree_1(position, trunk_radius=10, trunk_height=200, canopy_radius=75, color=(0.5, 0.5, 0.5)):
    tree = CompositeObstruction(position, color)  # Base color, though components override it
    tree.add_component(CylindricalObstruction, (0, 0, 0), trunk_radius, trunk_height, color=(0.6, 0.3, 0.0))  # Brown trunk
    tree.add_component(SphereObstruction, (0, 0, trunk_height), canopy_radius, color=(0.0, 0.6, 0.0))  # Green canopy
    return tree