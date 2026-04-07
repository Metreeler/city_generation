import numpy as np
import cv2 as cv

from node import Node


class Edge:
    def __init__(self, n1:Node, n2:Node):
        self.n1 = n1
        self.n2 = n2
        self.outer_edge = False

    def __eq__(self, value):
        if not isinstance(value, Edge):
            return False
        return (self.n1 == value.n1 and self.n2 == value.n2) or (self.n1 == value.n2 and self.n2 == value.n1)
    
    def __hash__(self):
        return hash((self.n1, self.n2))
    
    def __str__(self):
        return "n1 : (" + str(self.n1) + "), n2 : (" + str(self.n2) + ")"
    
    # def intersect(self, other):
    #     x1 = self.n1.x
    #     y1 = self.n1.y
    #     x2 = self.n2.x
    #     y2 = self.n2.y
    #     x3 = other.n1.x
    #     y3 = other.n1.y
    #     x4 = other.n2.x
    #     y4 = other.n2.y
        
    #     denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    #     if denominator == 0:
    #         return None
    #     px = (x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - x4 * y3)
    #     py = (x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - x4 * y3)
    #     px = px / denominator
    #     py = py / denominator

    #     return Node(px, py, self.n1.size, self.n1.radius)

    def intersect(self, other) -> Node|None:
        x1 = self.n1.x
        y1 = self.n1.y
        x2 = self.n2.x
        y2 = self.n2.y
        x3 = other.n1.x
        y3 = other.n1.y
        x4 = other.n2.x
        y4 = other.n2.y
        v1 = [x2 - x1, y2 - y1]
        v2 = [x4 - x3, y4 - y3]
        if np.cross(v1, v2):
            u_a = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / ((y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1))
            u_b = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / ((y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1))
            if 0 <= u_a <= 1 and 0 <= u_b <= 1:
                return Node(round(x1 + (x2 - x1) * u_a), round(y1 + (y2 - y1) * u_a), self.n1.size, self.n1.radius)
        return None

    def draw(self, src, color):
        if self.outer_edge:
            cv.line(src, (int(self.n1.y), int(self.n1.x)), (int(self.n2.y), int(self.n2.x)), (0, 125, 255), 5)
        else:
            cv.line(src, (int(self.n1.y), int(self.n1.x)), (int(self.n2.y), int(self.n2.x)), color, 3)
        self.n1.draw(src, color)
        self.n2.draw(src, color)