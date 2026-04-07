import numpy as np
import cv2 as cv
import json

from node import Node
from edge import Edge
from triangle import Triangle
from polygon import Polygon
from to_html import to_html

class Delauney:
    def __init__(self, row:int, col:int, nodes:list[Node]):
        self.nodes = nodes
        self.triangulation:set[Triangle] = self.triangulate(row, col)
        self.polygons:set[Polygon] = set()
        self.voronoi_nodes:set[Node] = set()
        self.voronoi:set[Edge] = self.delauney_to_voronoi(row, col)
    
    def triangulate(self, row, col):
        super_triangle = self.super_triangle(row, col)
        triangulation = [super_triangle]
        
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
                triangulation.append(Triangle([edge.n1, edge.n2, n]))

        
        for i in range(len(triangulation) - 1):
            for j in range(i + 1, len(triangulation)):
                triangulation[i].merge_triangle_edges(triangulation[j])
        
        outer_triangles:set[Triangle] = set()
        for tri in triangulation:
            for n in super_triangle.nodes:
                if tri.has_node(n):
                    outer_triangles.add(tri)
                    break
        
        for tri in outer_triangles:
            for edge in tri.edges:
                edge.outer_edge = True
            triangulation.remove(tri)

        return triangulation
    
    def draw(self, src, color):
        for tri in self.triangulation:
            tri.draw(src, color)
    
    def draw_voronoi_from_nodes(self, src, color):
        for node in self.voronoi_nodes:
            node.draw(src, color)
            node.draw_path_to_neighbors(src, (100, 100, 100))
    
    def draw_voronoi(self, src, color):
        for edge in self.voronoi:
            edge.draw(src, color)
    
    def draw_polygons(self, src, color):
        for poly in self.polygons:
            poly.draw(src, (np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255)))
    
    def draw_circum_circles(self, src, color):
        for tri in self.triangulation:
            tri.draw_circum_center(src, color)
            

    def super_triangle(self, row, col):
        x_coords = [n.x for n in self.nodes]
        y_coords = [n.y for n in self.nodes]
        return Triangle([
                Node(min(x_coords) - row,min(y_coords) - col, 0, 0),
                Node((max(x_coords) + row) * 2, min(y_coords) - col, 0, 0),
                Node(min(y_coords) - row, (max(x_coords) + col) * 2, 0, 0)
            ])
    
    def delauney_to_voronoi(self, row, col):
        voronoi:set[Edge] = set()
        triangles = self.triangulation.copy()
        polygons:set[Polygon] = set()
        top = Edge(Node(0, 0), Node(0, col))
        left = Edge(Node(0, 0), Node(row, 0))
        bottom = Edge(Node(row, 0), Node(row, col))
        right = Edge(Node(0, col), Node(row, col))
        while len(triangles) > 0:
            tri = triangles.pop()
            for e in tri.edges:
                if e.outer_edge:
                    n1 = tri.circum_circle.center
                    ps = e.n1 - e.n2
                    ps = Node(ps.y, -ps.x, ps.size, ps.radius)
                    middle = e.n1 + e.n2
                    middle.x = middle.x / 2
                    middle.y = middle.y / 2
                    di = middle - next(x for x in tri.nodes if x != e.n1 and x != e.n2)

                    norm = ps.get_norm()
                    if ps.dot_product(di) < 0:
                        ps.x = ps.x * -1 / norm
                        ps.y = ps.y * -1 / norm
                    else:
                        ps.x = ps.x / norm
                        ps.y = ps.y / norm
                    
                    n2 = Node(n1.x + ps.x * 2 * max(row, col), n1.y + ps.y * 2 * max(row, col))
                    edge = Edge(n1, n2)
                    intersections = [edge.intersect(top), edge.intersect(bottom), edge.intersect(right), edge.intersect(left)]
                    intersection = [x for x in intersections if x is not None]
                    
                    if len(intersection) == 1:
                        n2 = intersection[0]

                        # n1.add_neighbor(n2)
                        edge = Edge(n1, n2)
                        poly_1 = Polygon(e.n1, [edge], [e.n2])
                        poly_2 = Polygon(e.n2, [edge], [e.n1])
                        # self.voronoi_nodes.add(n1)
                        # self.voronoi_nodes.add(n2)
                        polygons.add(poly_1)
                        polygons.add(poly_2)
                        voronoi.add(e)
                else:
                    for t in triangles:
                        if e in t.edges:
                            n1 = tri.circum_circle.center
                            n2 = t.circum_circle.center
                            # n1.add_neighbor(n2)
                            edge = Edge(n1, n2)
                            poly_1 = Polygon(e.n1, [edge], [e.n2])
                            poly_2 = Polygon(e.n2, [edge], [e.n1])
                            # self.voronoi_nodes.add(n1)
                            # self.voronoi_nodes.add(n2)
                            polygons.add(poly_1)
                            polygons.add(poly_2)
                            voronoi.add(e)
                            break
        
        polygons_to_save:set[Polygon] = set()
        for poly in polygons:
            new_poly = True
            if poly.edges[0].n1.in_rectangle(0, 0, row, col) or poly.edges[0].n2.in_rectangle(0, 0, row, col):
                for p in polygons_to_save:
                    if poly.center == p.center:
                        p.edges = p.edges + poly.edges
                        p.neighbours = p.neighbours + poly.neighbours
                        new_poly = False
                        break
                    else:
                        pass
                if new_poly:
                    polygons_to_save.add(poly)

        for poly in polygons_to_save:
            poly.order_vertices(row, col)
        
        for poly in polygons_to_save:
            if poly.outer_poly:
                for edge in poly.edges:
                    intersections = [edge.intersect(top), edge.intersect(bottom), edge.intersect(right), edge.intersect(left)]
                    intersection = [x for x in intersections if x is not None]
                    if len(intersection) == 1:
                        if edge.n1.in_rectangle(0, 0, row, col) and not edge.n1 == intersection[0]:
                            edge.n2 = intersection[0]
                            poly.complete = False
                        elif edge.n2.in_rectangle(0, 0, row, col) and not edge.n2 == intersection[0]:
                            edge.n1 = intersection[0]
                            poly.complete = False
                poly.order_vertices(row, col)

        # for poly in polygons_to_save:
        #     poly.order_vertices(row, col)

        for poly in polygons_to_save:
            poly.close_edges()

        for poly in polygons_to_save:
            for edge in poly.edges:
                edge.n1.add_neighbor(edge.n2)
                self.voronoi_nodes.add(edge.n1)
                self.voronoi_nodes.add(edge.n2)


        
        self.polygons = polygons_to_save

        return voronoi


if __name__=="__main__":
    row, col = 500, 1000
    # nodes:list[Node] = []
    
    nodes:list[Node] = [
        Node(400, 400, 5),
        Node(100, 200, 5),
        Node(300, 100, 5),
    ]

    # for i in range(100):
    #     nodes.append(Node(np.random.randint(row / 10, row - (row / 10)), np.random.randint(col / 10, col - (col / 10)), 5, 0))


    # with open("data/nodes.json") as f:
    #     loaded_nodes = json.load(f)

    # for n in loaded_nodes["data"]:
    #     nodes.append(Node(n["x"], n["y"], 5, n["radius"]))

    out = np.zeros((row, col, 3))

    d = Delauney(row, col, nodes)

    d.draw(out, (0, 0, 255))
    d.draw_circum_circles(out, (0, 0, 255))
    
    cv.imwrite("data/web-display/assets/out.png", (out).astype(np.uint8))

    out = np.zeros((row, col, 3))
    
    for tri in d.triangulation:
        for e in tri.edges:
            if e.outer_edge:
                e.draw(out, (255, 255, 255))
    
    cv.imwrite("data/web-display/assets/outer_edges.png", (out).astype(np.uint8))

    
    to_html('data/web-display/assets', 'data/web-display/index.html')