import numpy as np
import cv2 as cv
import random
import string
import json

from perlin_noise_2d import noise_layer
from node import *
from poisson_disc import PoissonDisc
from delauney import Delauney
from to_html import to_html
from utils import reset_files


if __name__=="__main__":
    # seed = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    seed = '1kqojd176t'
    print("Seed :", seed)

    folder = 'data/web-display/assets'
    reset_files(folder)

    row, col = 800, 500
    min_radius, max_radius = 100, 101

    radii = min_radius + noise_layer(seed, row, col, 2, 1) * (max_radius - min_radius)
    src = np.zeros((row, col)) + 1
    # src[int(row / 10):int(row - row / 10), int(col / 10):int(col - col / 10)] = 1

    distribution = PoissonDisc(seed, row, col, src, radii)
    
    poisson_drawn = np.zeros((row, col, 3))

    print('Poisson disc with ', len(distribution.nodes), ' nodes')
    distribution.draw(poisson_drawn, (255, 255, 255))

    cv.imwrite("data/web-display/assets/radii.png", ((radii - min_radius) / (max_radius - min_radius) * 255).astype(np.uint8))
    cv.imwrite("data/web-display/assets/poisson_drawn.png", (poisson_drawn).astype(np.uint8))

    delauney = Delauney(row, col, distribution.nodes)

    # nodes:list[Node] = [
    #     Node(400, 400, 5),
    #     Node(100, 200, 5),
    #     Node(300, 100, 5),
    #     Node(200, 350, 5),
    # ]

    # delauney = Delauney(row, col, nodes)
    
    delauney_drawn = np.zeros((row, col, 3))
    
    delauney.draw_voronoi_from_nodes(delauney_drawn, (0, 0, 255))
    
    cv.imwrite("data/web-display/assets/delauney_drawn.png", (delauney_drawn).astype(np.uint8))
    
    delauney_triangles_drawn = np.zeros((row, col, 3))
    
    delauney.draw(delauney_triangles_drawn, (0, 0, 255))
    
    cv.imwrite("data/web-display/assets/delauney_triangles_drawn.png", (delauney_triangles_drawn).astype(np.uint8))
    
    voronoi_drawn = np.zeros((row, col, 3))
    
    delauney.draw_voronoi(voronoi_drawn, (0, 0, 255))
    
    cv.imwrite("data/web-display/assets/voronoi_drawn.png", (voronoi_drawn).astype(np.uint8))
    
    polygons_drawn = np.zeros((row, col, 3))
    
    delauney.draw_polygons(polygons_drawn, (0, 0, 255))
    
    cv.imwrite("data/web-display/assets/polygons_drawn.png", (polygons_drawn).astype(np.uint8))
    
    out = np.zeros((row, col, 3))
    
    delauney.draw(out, (0, 0, 255))
    delauney.draw_voronoi_from_nodes(out, (0, 0, 255))
    
    cv.imwrite("data/web-display/assets/out.png", (out).astype(np.uint8))

    to_html(folder, 'data/web-display/index.html')
