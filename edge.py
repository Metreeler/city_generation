import numpy as np
import cv2 as cv

from node import Node


class Edge:
    def __init__(self, n1:Node, n2:Node):
        self.n1 = n1
        self.n2 = n2

    def __eq__(self, value):
        if not isinstance(value, Edge):
            return False
        return (self.n1 == value.n1 and self.n2 == value.n2) or (self.n1 == value.n2 and self.n2 == value.n1)
    
    def __hash__(self):
        return hash((self.n1, self.n2))
    
    def __str__(self):
        return "n1 : (" + str(self.n1) + "), n2 : (" + str(self.n2) + ")"

    def draw(self, src, color):
        cv.line(src, (int(self.n1.y), int(self.n1.x)), (int(self.n2.y), int(self.n2.x)), color, 1)
        self.n1.draw(src, color)
        self.n2.draw(src, color)