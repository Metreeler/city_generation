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
            Edge(nodes[0], nodes[2]),
            Edge(nodes[1], nodes[2])
        ]
        self.circum_circle = CircumCircle(nodes)
    
    def has_edge(self, edge:Edge):
        return sum([edge == e for e in self.edges]) > 0
    
    def has_node(self, node:Node):
        return sum([node == n for n in self.nodes]) > 0
    
    def draw(self, src, color):
        for edge in self.edges:
            edge.draw(src, color)
