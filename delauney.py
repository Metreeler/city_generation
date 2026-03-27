import numpy as np
import cv2 as cv
import json

from node import Node
from edge import Edge
from triangle import Triangle
from polygon import Polygon

class Delauney:
    def __init__(self, nodes:list[Node]):
        self.nodes = nodes
        self.triangulation = self.triangulate()
        self.polygons:set[Polygon] = set()
        self.voronoi:set[Edge] = self.delauney_to_voronoi()
        self.voronoi_nodes:set[Node] = set()
    
    def triangulate(self):
        super_triangle = self.super_triangle()
        triangulation = set([super_triangle])
        
        for n in self.nodes:
            bad_triangles:set[Triangle] = set()
            polygon:set[Edge] = set()

            for tri in triangulation:
                if tri.circum_circle.contains_node(n):
                    bad_triangles.add(tri)
            
            all_edges:list[Edge] = []
            for tri in bad_triangles:
                all_edges = all_edges + tri.edges
            
            unique_edges = set(all_edges)
            for edge in unique_edges:
                if all_edges.count(edge) == 1:
                    polygon.add(edge)
            
            for tri in bad_triangles:
                triangulation.remove(tri)
            
            for edge in polygon:
                triangulation.add(Triangle([edge.n1, edge.n2, n]))
        
        outer_triangles:set[Triangle] = set()
        for tri in triangulation:
            for n in super_triangle.nodes:
                if tri.has_node(n):
                    outer_triangles.add(tri)
                    break
        
        for tri in outer_triangles:
            triangulation.remove(tri)

        return triangulation
    
    def draw(self, src, color):
        for tri in self.triangulation:
            tri.draw(src, color)
    
    def draw_voronoi(self, src, color):
        for edge in self.voronoi:
            edge.draw(src, color)
    
    def draw_polygons(self, src, color):
        for poly in self.polygons:
            poly.draw(src, (np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255)))
            

    def super_triangle(self):
        x_coords = [n.x for n in self.nodes]
        y_coords = [n.y for n in self.nodes]
        return Triangle([
                Node(min(x_coords) - 1,min(y_coords) - 1, 0, 0),
                Node((max(x_coords) + 1) * 2, min(y_coords) - 1, 0, 0),
                Node(min(y_coords) - 1, (max(x_coords) + 1) * 2, 0, 0)
            ])
    
    def delauney_to_voronoi(self):
        voronoi:set[Edge] = set()
        triangles = self.triangulation.copy()
        polygons:set[Polygon] = set()

        while len(triangles) > 0:
            tri = triangles.pop()
            for e in tri.edges:
                for t in triangles:
                    if e in t.edges and tri.circum_circle.center.x > 0:
                        poly_1 = Polygon(e.n1, [Edge(tri.circum_circle.center, t.circum_circle.center)], [e.n2])
                        poly_2 = Polygon(e.n2, [Edge(tri.circum_circle.center, t.circum_circle.center)], [e.n1])
                        polygons.add(poly_1)
                        polygons.add(poly_2)
                        voronoi.add(Edge(tri.circum_circle.center, t.circum_circle.center))
                        break
        
        polygons_to_save:set[Polygon] = set()
        for poly in polygons:
            new_poly = True
            for p in polygons_to_save:
                if poly.center == p.center:
                    p.edges = p.edges + poly.edges
                    p.neighbours = p.neighbours + poly.neighbours
                    new_poly = False
                    break
            if new_poly:
                polygons_to_save.add(poly)

        # while len(polygons) > 0:
        #     poly = polygons.pop()
        #     for p in polygons:
        #         if ()
        
        self.polygons = polygons_to_save
        print(len(polygons))

        return voronoi


if __name__=="__main__":
    row, col = 2000, 2000
    nodes:list[Node] = []

    for i in range(100):
        nodes.append(Node(np.random.randint(row / 10, row - (row / 10)), np.random.randint(col / 10, col - (col / 10)), 5, 0))


    # with open("data/nodes.json") as f:
    #     loaded_nodes = json.load(f)

    # for n in loaded_nodes["data"]:
    #     nodes.append(Node(n["x"], n["y"], 5, n["radius"]))

    out = np.zeros((row, col, 3))

    d = Delauney(nodes)

    d.draw_polygons(out, (0, 0, 255))
    d.draw_voronoi(out, (0, 0, 255))
    d.draw(out, (0, 255, 0))
    
    cv.imwrite("data/web-display/assets/out.png", (out).astype(np.uint8))
    # d = Delauney([Node(10, 10, 0, 0)])