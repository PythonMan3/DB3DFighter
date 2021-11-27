import sys
import math

class BoundBox:
    def __init__(self):
        self.reset()
        
    def is_empty(self):
        return self.bound[0] == sys.float_info.max
        
    def reset(self):
        self.bound = [
            sys.float_info.max, sys.float_info.max, sys.float_info.max,     # min X, Y, Z coordinates
            -sys.float_info.max, -sys.float_info.max, -sys.float_info.max]  # max X, Y, Z coordinates
        self.bound_points = [
            [sys.float_info.max, sys.float_info.max, sys.float_info.max],     # min X point
            [sys.float_info.max, sys.float_info.max, sys.float_info.max],     # min Y point
            [sys.float_info.max, sys.float_info.max, sys.float_info.max],     # min Z point
            [-sys.float_info.max, -sys.float_info.max, -sys.float_info.max],  # max X point
            [-sys.float_info.max, -sys.float_info.max, -sys.float_info.max],  # max Y point
            [-sys.float_info.max, -sys.float_info.max, -sys.float_info.max]]  # max Z point
        
    def set_range(self, range_):
        if not isinstance(range_, (tuple, list)) or len(range_) != 6:
            raise ValueError
        self.bound = range_
        
    def get_range(self):
        return self.bound
        
    def add_point(self, xyz):
        for i in range(3):
            # check min X, Y, Z
            if self.bound[i] > xyz[i]:
                self.bound[i] = xyz[i]
                self.bound_points[i] = xyz
            # check max X, Y, Z
            if self.bound[i + 3] < xyz[i]:
                self.bound[i + 3] = xyz[i]
                self.bound_points[i + 3] = xyz
        
    def get_corner_points(self):
        points = [None] * 8
        points[0] = (self.bound[0], self.bound[1], self.bound[2])
        points[1] = (self.bound[0], self.bound[1], self.bound[5])
        points[2] = (self.bound[0], self.bound[4], self.bound[2])
        points[3] = (self.bound[0], self.bound[4], self.bound[5])
        points[4] = (self.bound[3], self.bound[1], self.bound[2])
        points[5] = (self.bound[3], self.bound[1], self.bound[5])
        points[6] = (self.bound[3], self.bound[4], self.bound[2])
        points[7] = (self.bound[3], self.bound[4], self.bound[5])
        return points
        
    def get_center(self):
        if self.is_empty():
            return [0.0, 0.0, 0.0]
        else:
            center = [0.0] * 3
            center[0] = (self.bound[0] + self.bound[3]) / 2.0
            center[1] = (self.bound[1] + self.bound[4]) / 2.0
            center[2] = (self.bound[2] + self.bound[5]) / 2.0
            return center
        
    def get_sphere(self):
        center = self.get_center()
        radius = -sys.float_info.max
        bound_points = [self.bound[0:3], self.bound[3:6]]
        if self.bound_points[0][0] != sys.float_info.max:
            bound_points = self.bound_points
        for point in bound_points:
            dist = math.sqrt(
                (point[0] - center[0]) * (point[0] - center[0]) + \
                (point[1] - center[1]) * (point[1] - center[1]) + \
                (point[2] - center[2]) * (point[2] - center[2]) )
            radius = max(radius, dist)
        return center, radius
