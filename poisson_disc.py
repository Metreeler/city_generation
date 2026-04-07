import cv2 as cv
import numpy as np
import numpy.typing as npt

from node import Node
from perlin_noise_2d import noise_layer


def random_number(seed, x, y, z=None):
    if z is None:
        z = x + y + x * y
    a = x * np.cos(x) + y * np.sin(x) + 1 / (1 + np.exp(np.cos(x + y)))
    b = x * np.cos(y) + y * np.sin(y) + 1 / (1 + np.exp(np.sin(x + y)))
    c = x * np.cos(z) + y * np.sin(z) + 1 / (1 + np.exp(np.cos(z)))
    seed_value = int(seed[:min(5, len(seed))], 36)
    d = seed_value * (a + b + c)
    return (((a * b * c * d) % 10477) / 10477)


class PoissonDisc:
    def __init__(self, seed:str, row, col, mask, radii):
        self.nodes:list[Node] = self.create_mesh(seed, row, col, mask, radii)

    def create_mesh(
            self,
            seed:str,
            row:int, 
            col:int, 
            zone_to_cover, 
            radii
        ):

        random_i = np.tile(np.arange(row), (col, 1)).T
        random_j = np.tile(np.arange(col), (row, 1))

        random = random_number(seed, random_i, random_j)
        
        new_node_terrain = random * zone_to_cover
        available = new_node_terrain.copy()
        
        nodes:list[Node] = [
            # Node(0, 0, 5, 100),
            # Node(row, 0, 5, 100),
            # Node(0, col, 5, 100),
            # Node(row, col, 5, 100),
        ]

        for n in nodes:
            cv.circle(available, center=(n.y, n.x), radius=n.radius, color=(0, 0, 0), thickness=-1)


        terrain_opened = np.zeros((row, col))

        while np.max(available) > 0:
            (x_values, y_values) = np.where(new_node_terrain == np.max(new_node_terrain))
            x, y = x_values[0], y_values[0]
            radius = np.uint64(radii[x, y])

            nodes.append(Node(x, y, 5, radius))
            
            cv.circle(available, center=(y_values[0], x_values[0]), radius=radius, color=(0, 0, 0), thickness=-1)

            cv.circle(terrain_opened, center=(y_values[0], x_values[0]), radius=radius + 1, color=(1, 1, 1), thickness=-1)

            new_node_terrain = available * terrain_opened
            if np.max(new_node_terrain) <= 0:
                new_node_terrain = available
        
        return nodes
    
    def draw(self, src, color):
        for node in self.nodes:
            node.draw(src, color)


if __name__=="__main__":
    seed = "abcd"
    row, col = 2000, 2000
    min_radius, max_radius = 20, 100

    radii = min_radius + noise_layer(seed, row, col, 2, 1) * (max_radius - min_radius)
    src = np.zeros((row, col)) + 1

    distribution = PoissonDisc(seed, row, col, src, radii)
    
    poisson_drawn = np.zeros((row, col, 3))

    print('Poisson disc with ', len(distribution.nodes), ' nodes')
    distribution.draw(poisson_drawn, (255, 255, 255))

    cv.imwrite("data/web-display/assets/radii.png", (radii * 255).astype(np.uint8))
    cv.imwrite("data/web-display/assets/out.png", (poisson_drawn).astype(np.uint8))
