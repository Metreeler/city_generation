from node import Node
import numpy as np
import cv2 as cv

class CircumCircle:
    def __init__(self, nodes:list[Node]):
        assert len(nodes) == 3

        self.radius:float = self.caclulate_radius(nodes[0], nodes[1], nodes[2])
        self.center:Node = self.calculate_center(nodes[0], nodes[1], nodes[2])
    
    def caclulate_radius(self, A:Node, B:Node, C:Node):
        a = A.distance_to(B)
        b = B.distance_to(C)
        c = A.distance_to(C)
        p = (a + b + c) / 2
        return a * b * c / (4 * np.sqrt(p * (p - a) * (p - b) * (p - c)))
    
    def calculate_center(self, A:Node, B:Node, C:Node):
        det = A.x * (B.y - C.y) - B.x * (A.y - C.y) + C.x * (A.y - B.y)
        a_squared = A.x ** 2 + A.y ** 2
        b_squared = B.x ** 2 + B.y ** 2
        c_squared = C.x ** 2 + C.y ** 2
        det_x = a_squared * (B.y - C.y) - b_squared * (A.y - C.y) + c_squared * (A.y - B.y)
        det_y = a_squared * (B.x - C.x) - b_squared * (A.x - C.x) + c_squared * (A.x - B.x)
        return Node(det_x / (2 * det), - det_y / (2 * det), 5, 0)
    
    def contains_node(self, node:Node):
        return node.distance_to(self.center) < self.radius

    def draw(self, src, color):
        cv.circle(src, (int(self.center.y), int(self.center.x)), int(self.radius), color)