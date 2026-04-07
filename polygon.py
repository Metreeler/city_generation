import cv2 as cv
import numpy as np

from node import Node
from edge import Edge


class Polygon:
    def __init__(self, center:Node, edges:list[Edge], neighbors:list[Node]):
        self.center:Node = center
        self.edges:list[Edge] = edges
        self.vertices:list[Node] = []
        self.neighbours:list[Node] = neighbors
        self.complete:bool = False
        self.outer_poly:bool = False
    
    def draw(self, src, color):
        vertices = []

        for n in self.vertices:
            vertices.append((n.y, n.x))

        # if not self.complete:
        #     vertices = np.array(vertices, dtype=np.int32)
        #     cv.drawContours(src, [vertices], 0, color, -1)
        if self.outer_poly and self.complete:
            vertices = np.array(vertices, dtype=np.int32)
            cv.drawContours(src, [vertices], 0, (0, 0, np.random.randint(100, 255)), -1)
        elif self.complete:
            vertices = np.array(vertices, dtype=np.int32)
            cv.drawContours(src, [vertices], 0, color, -1)
        elif len(vertices) > 2:
            vertices = np.array(vertices, dtype=np.int32)
            cv.drawContours(src, [vertices], 0, (np.random.randint(100, 255), 0, 0), -1)
        else:
            vertices.append((self.center.y, self.center.x))
            vertices = np.array(vertices, dtype=np.int32)
            cv.drawContours(src, [vertices], 0, (np.random.randint(255), np.random.randint(255), np.random.randint(255)), -1)
            cv.circle(src, center=(self.center.y, self.center.x), radius=10, color=(100, 100, 100), thickness=-1)
        
        self.center.draw(src, (255, 255, 255))

    def order_vertices(self, row, col):
        outer_nodes:list[Node] = [self.edges[0].n1]

        has_neighbor = True
        while len(self.edges) + 1 > len(outer_nodes) and has_neighbor:
            has_neighbor = False
            for e in self.edges:
                if e.n1 == outer_nodes[-1] and e.n2 not in outer_nodes:
                    outer_nodes.append(e.n2)
                    has_neighbor = True
                elif e.n2 == outer_nodes[-1] and e.n1 not in outer_nodes:
                    outer_nodes.append(e.n1)
                    has_neighbor = True
                elif e.n1 == outer_nodes[0] and e.n2 not in outer_nodes:
                    outer_nodes.insert(0, e.n2)
                    has_neighbor = True
                elif e.n2 == outer_nodes[0] and e.n1 not in outer_nodes:
                    outer_nodes.insert(0, e.n1)
                    has_neighbor = True
        
        for node in outer_nodes:
            if not node.in_rectangle(0, 0, row, col):
                self.outer_poly = True
                break
        
        coords: list[Node] = []
        for e in self.edges:
            coords.append(e.n1)
            coords.append(e.n2)
        
        if len(coords) > 2:
            self.complete = True
            for n in coords:
                if coords.count(n) != 2:
                    self.complete = False
                    break
        
        self.vertices = outer_nodes
    
    def close_edges(self):
        if not self.complete:
            coords: list[Node] = []
            for edge in self.edges:
                coords.append(edge.n1)
                coords.append(edge.n2)

            unique_coords:list[Node] = []
            for n in coords:
                if coords.count(n) != 2:
                    unique_coords.append(n)

            if len(unique_coords) == 2:
                n1 = unique_coords[0]
                n2 = unique_coords[1]
                if n1.x == n2.x or n1.y == n2.y:
                    self.edges.append(Edge(unique_coords[0], unique_coords[1]))
                    self.complete = True

                
    
    def __str__(self):
        out = "Center : " + str(self.center)
        for e in self.edges:
            out += "\n - " + str(e)
        return out


if __name__=="__main__":
    row, col = 2000, 2000
    
    out = np.zeros((row, col, 3))

    n1 = Node(100, 1000, 0, 0)
    n2 = Node(1000, 100, 0, 0)
    n3 = Node(1000, 1000, 0, 0)
    n4 = Node(500, 1250, 0, 0)

    poly = Polygon(Node(10, 10, 0, 0), [Edge(n1, n2), Edge(n2, n3), Edge(n4, n3), Edge(n4, n1)], [])

    poly.draw(out, (np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255)))

    cv.imwrite("data/web-display/assets/out.png", (out).astype(np.uint8))