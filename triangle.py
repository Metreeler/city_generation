import numpy as np
import cv2 as cv

from node import Node
from edge import Edge
from circum_circle import CircumCircle

class Triangle:
    def __init__(self, nodes:list[Node]):
        assert len(nodes) == 3
        self.nodes = nodes
        self.edges:list[Edge] = [
            Edge(nodes[0], nodes[1]),
            Edge(nodes[1], nodes[2]),
            Edge(nodes[2], nodes[0])
        ]
        self.circum_circle = CircumCircle(nodes)
    
    def has_edge(self, edge:Edge):
        return sum([edge == e for e in self.edges]) > 0
    
    def has_node(self, node:Node):
        return sum([node == n for n in self.nodes]) > 0
    
    def draw(self, src, color):
        for edge in self.edges:
            edge.draw(src, color)
    
    def merge_triangle_edges(self, triangle):
        merged = False
        for i in range(len(self.edges)):
            for j in range(len(triangle.edges)):
                if(self.edges[i] == triangle.edges[j]):
                    self.edges[i] = triangle.edges[j]
                    merged = True
                    break
            if merged: break
    
    def draw_circum_center(self, src, color):
        self.circum_circle.draw(src, color)

if __name__=="__main__":
    t1 = Triangle([
        Node(600, 600, 5),
        Node(800, 600, 5),
        Node(600, 800, 5),
    ])
    t2 = Triangle([
        Node(900, 900, 5),
        Node(600, 800, 5),
        Node(800, 600, 5),
    ])

    print("before")
    t1.merge_triangle_edges(t2)

    for e in t2.edges:
        e.outer_edge = True
    
    for e in t1.edges:
        if e.outer_edge:
            print(str(e))
    
    print("after")
    
    for e in t1.edges:
        if e.outer_edge:
            print(str(e))
    
    

