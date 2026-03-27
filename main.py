import numpy as np
import cv2 as cv
import random
import string
import json

from perlin_noise_2d import noise_layer
from node import *


if __name__=="__main__":
    # seed = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    seed = "iz1xk046cg"
    
    row, col = 2000, 2000
    city_node_radius = 15
    terrain_node_radius = 50
    
    print(seed)

    terrain = np.zeros((row, col))
    terrain[100:(row - 100), 100:(col -100)] = 1

    city_mask = np.zeros((row, col))
    
    nodes:list[Node] = []

    nodes.append(Node(1000, 1000, 10, 250, main_node=True, part_of_city=True))
    nodes.append(Node(300, 300, 10, 100, main_node=True, part_of_city=True))
    nodes.append(Node(1700, 300, 10, 100, main_node=True, part_of_city=True))
    nodes.append(Node(300, 1700, 10, 100, main_node=True, part_of_city=True))
    nodes.append(Node(1700, 1700, 10, 100, main_node=True, part_of_city=True))

    for node in nodes:
        cv.circle(city_mask, center=(node.y, node.x), radius=node.radius - city_node_radius, color=(1, 1, 1), thickness=-1)
        cv.circle(city_mask, center=(node.y, node.x), radius=city_node_radius, color=(0, 0, 0), thickness=-1)

    nodes = nodes + create_mesh(seed, row, col, city_mask * terrain, city_node_radius, part_of_city=True, save=True)
    
    # City outskirt creation

    city_outskirt_mask = np.zeros((row, col))

    for node in nodes:
        if node.main_node:
            cv.circle(city_outskirt_mask, center=(node.y, node.x), radius=node.radius, color=(1, 1, 1), thickness=1)

    outskirt_nodes = create_mesh(seed, row, col, city_outskirt_mask * terrain, terrain_node_radius, city_outskirt=True)

    closest_node:list[Node|None] = [None] * len(outskirt_nodes)
    min_dist = np.zeros((len(outskirt_nodes))) + terrain_node_radius

    for node in nodes:
        for i in range(len(outskirt_nodes)):
            dist = outskirt_nodes[i].distance_to(node)
            if dist < min_dist[i]:
                min_dist[i] = dist
                closest_node[i] = node
    
    for i in range(len(outskirt_nodes)):
        if closest_node[i] is not None:
            outskirt_nodes[i].add_neighbor(closest_node[i])
            closest_node[i].add_neighbor(outskirt_nodes[i])
    
    nodes = nodes + outskirt_nodes
    
    # Other nodes creation

    terrain_mask = np.zeros((row, col)) + 1

    for node in nodes:
        if node.main_node or not node.part_of_city:
            cv.circle(terrain_mask, center=(node.y, node.x), radius=node.radius, color=(0, 0, 0), thickness=-1)

    nodes = nodes + create_mesh(seed, row, col, terrain_mask * terrain, terrain_node_radius)

    out = np.zeros((row, col, 3))
    out[:, :, 0] = terrain * 255
    out[:, :, 1] = terrain * 255
    out[:, :, 2] = terrain * 255
    
    for i in range(len(nodes) - 1):
        for j in range(i + 1, len(nodes)):
            if nodes[i].part_of_city and nodes[j].part_of_city:
                if(nodes[i].distance_to(nodes[j]) < min(nodes[i].radius, nodes[j].radius) * np.sqrt(2)):
                    nodes[i].add_neighbor(nodes[j])
                    nodes[j].add_neighbor(nodes[i])
            elif not nodes[i].part_of_city and not nodes[j].part_of_city:
                if(nodes[i].distance_to(nodes[j]) < max(nodes[i].radius, nodes[j].radius) * 2):
                    nodes[i].add_neighbor(nodes[j])
                    nodes[j].add_neighbor(nodes[i])
    
    # for i in range(4):
    #     print(a_star(nodes, nodes[i + 1], nodes[0]))

    #     current_node = nodes[0]

    #     while current_node.parent != None:
    #         current_node.draw_path_to_node(out, current_node.parent, (255, 50, 50))
    #         current_node = current_node.parent
        
    #     reset_a_star(nodes)

    for node in nodes:
        node.draw_path_to_neighbors(out, (255, 50, 50))

    for node in nodes:
        if node.main_node:
            node.draw(out, (50, 255, 50))
        else:
            node.draw(out, (255, 50, 50))
    
    coords = []
    for n in nodes:
        coords.append({
            "x":int(n.x),
            "y":int(n.y),
            "radius":int(n.radius)
            })
    
    # print(coords)
    with open("data/nodes.json", 'w', encoding ='utf8') as json_file:
        json.dump({"data":coords}, json_file, ensure_ascii = False)
    

    cv.imwrite("data/web-display/assets/terrain.png", (terrain * 255).astype(np.uint8))
    cv.imwrite("data/web-display/assets/out.png", (out).astype(np.uint8))