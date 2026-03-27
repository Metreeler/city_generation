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
    
    def draw(self, src, color):
        self.order_vertices()

        vertices = []

        for n in self.vertices:
            vertices.append((n.y, n.x))

        vertices = np.array(vertices, dtype=np.int32)
        if self.complete:
            cv.drawContours(src, [vertices], 0, color, -1)

            for n in self.neighbours:
                cv.line(src, (self.center.y, self.center.x), (n.y, n.x), (100, 100, 100), 5)
        elif vertices.shape[0] > 2:
            cv.drawContours(src, [vertices], 0, (255, 255, 255), -1)

        self.center.draw(src, (0, 0, 0))

    def order_vertices(self) -> list[Node]:
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
        
        coords: list[Node] = []
        for e in self.edges:
            coords.append(e.n1)
            coords.append(e.n2)
            
        self.complete = True
        for n in coords:
            if coords.count(n) != 2:
                self.complete = False
                break
        
        self.vertices = outer_nodes


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