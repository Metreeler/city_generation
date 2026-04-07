import numpy as np
import cv2 as cv
import random
import string
import json

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

def normalize_array(arr, low, high):
    if np.max(arr) > np.min(arr):
        return (high - low) * (arr - np.min(arr)) / (np.max(arr) - np.min(arr)) + low
    return arr


class Node:
    def __init__(self, x, y, size=0, radius=0, main_node=False, part_of_city=False, city_outskirt=False):
        self.x:float = x
        self.y:float = y
        self.size:int = size
        self.radius:int = radius
        self.neighbors:set[Node] = set()
        self.main_node:bool = main_node
        self.city_outskirt:bool = city_outskirt
        self.part_of_city:bool = part_of_city

        # A STAR
        self.f:float = np.inf
        self.g:float = np.inf
        self.h:float = 0
        self.parent:Node|None = None
    
    def __eq__(self, value):
        return self.x == value.x and self.y == value.y
    
    def __gt__(self, other):
        return self.x + self.y > other.x + other.y
    
    def __lt__(self, other):
        return self.x + self.y < other.x + other.y
    
    def __sub__(self, other):
        return Node(self.x - other.x, self.y - other.y, self.size, self.radius)
    
    def __add__(self, other):
        return Node(self.x + other.x, self.y + other.y, self.size, self.radius)
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def __str__(self):
        return str(self.x) + ", " + str(self.y)
    
    def dot_product(self, other):
        return self.x * other.x + self.y * other.y
    
    def get_norm(self):
        return np.sqrt(self.x ** 2 + self.y ** 2)
    
    def in_rectangle(self, x1, y1, x2, y2):
        return x1 <= self.x <= x2 and y1 <= self.y <= y2
    
    def draw(self, src, color):
        cv.circle(src, center=(int(self.y), int(self.x)), radius = self.size, color=color, thickness=-1)
    
    def draw_radius(self, src, color):
        cv.circle(src, center=(self.y, self.x), radius = self.radius, color=color, thickness=2)

    def draw_path_to_neighbors(self, src, color):
        for neighbor in self.neighbors:
            self.draw_path_to_node(src, neighbor, color)

    def draw_path_to_node(self, src, node, color):
        cv.line(src, (int(self.y), int(self.x)), (int(node.y), int(node.x)), color, 2)
    
    def distance_to(self, node):
        return np.sqrt((self.x - node.x) ** 2 + (self.y - node.y) ** 2)
    
    def constrain_in_area(self, row, col):
        if row >= self.x >= 0 and col >= self.y >= 0:
            return self
        x = min(max(self.x, 0), row)
        y = min(max(self.y, 0), col)
        return Node(x, y, self.size, self.radius, self.main_node, self.part_of_city, self.city_outskirt)
    
    def add_neighbor(self, node):
        self.neighbors.add(node)
        node.neighbors.add(self)


def a_star(nodes: list[Node], starting_node:Node, ending_node:Node):
    for node in nodes:
        node.h = node.distance_to(ending_node)
    
    open_list = [starting_node]
    closed_list = []

    while len(open_list) > 0:
        open_list.sort(key=lambda node: node.f)
        current_node = open_list.pop(0)

        if current_node is ending_node:
            return True

        closed_list.append(current_node)

        for n in current_node.neighbors:
            if n not in closed_list:
                if n not in open_list:
                    open_list.append(n)
                    n.parent = current_node
                    n.g = current_node.g + 1
                    n.f = n.g + n.h
                elif n.g > current_node.g + 1:
                    n.parent = current_node
                    n.g = current_node.g + 1
                    n.f = n.g + n.h
    return False


def reset_a_star(nodes):
    for node in nodes:
        node.f = np.inf
        node.g = np.inf
        node.h = 0
        node.parent = None

def create_mesh(
        seed,
        row, 
        col, 
        zone_to_cover, 
        min_radius, 
        main_node=False, 
        part_of_city=False, 
        city_outskirt=False, 
        save=False
    ):
    random_i = np.tile(np.arange(row), (col, 1))
    random_j = np.tile(np.arange(col), (row, 1)).T

    random = random_number(seed, random_i, random_j)

    new_node_terrain = random * zone_to_cover
    available = new_node_terrain.copy()
    
    nodes:list[Node] = []
    
    maxNode = 1000

    if save:
        cv.imwrite("data/web-display/assets/start_terrain.png", (new_node_terrain * 255).astype(np.uint8))
        cv.imwrite("data/web-display/assets/zone_to_cover.png", (zone_to_cover * 255).astype(np.uint8))

    terrain_opened = np.zeros((row, col))

    while maxNode > 0 and np.max(available) > 0:
        (x_values, y_values) = np.where(new_node_terrain == np.max(new_node_terrain))
        x, y = x_values[0], y_values[0]
        radius = min_radius

        nodes.append(Node(x, y, 5, radius, main_node, part_of_city, city_outskirt))
        
        cv.circle(available, center=(y_values[0], x_values[0]), radius=radius, color=(0, 0, 0), thickness=-1)

        cv.circle(terrain_opened, center=(y_values[0], x_values[0]), radius=radius + 1, color=(1, 1, 1), thickness=-1)

        new_node_terrain = available * terrain_opened
        if np.max(new_node_terrain) <= 0:
            new_node_terrain = available

        maxNode -= 1
    print(len(nodes))
    
    if save :
        
        cv.imwrite("data/web-display/assets/new_node_terrain.png", (new_node_terrain * 255).astype(np.uint8))
        cv.imwrite("data/web-display/assets/available.png", (available * 255).astype(np.uint8))
        cv.imwrite("data/web-display/assets/terrain_opened.png", (terrain_opened * 255).astype(np.uint8))
    
    return nodes


if __name__=="__main__":
    
    row, col = 2000, 2000
    nodes:list[Node] = []

    out = np.zeros((row, col, 3))

    with open("data/nodes.json") as f:
        loaded_nodes = json.load(f)

    for n in loaded_nodes["data"]:
        nodes.append(Node(n["x"], n["y"], 5, n["radius"]))

    for node in nodes:
        if node.main_node:
            node.draw(out, (50, 255, 50))
        else:
            node.draw(out, (255, 50, 50))

    cv.imwrite("data/web-display/assets/out.png", (out).astype(np.uint8))