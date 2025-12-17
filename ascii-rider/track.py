"""
Track/Map management
"""

class Track:
    def __init__(self):
        self.points = []  # List of [x, y] coordinates
        self.lines = []   # List of [point_index1, point_index2]
        self.last_point = None

    def add_point(self, x, y):
        """Add a point and connect to previous if exists"""
        point = [x, y]

        # Check if point already exists nearby
        for i, p in enumerate(self.points):
            if abs(p[0] - x) < 2 and abs(p[1] - y) < 2:
                # Point already exists, just connect to it
                if self.last_point is not None and self.last_point != i:
                    self.lines.append([self.last_point, i])
                self.last_point = i
                return

        # Add new point
        point_idx = len(self.points)
        self.points.append(point)

        # Connect to previous point
        if self.last_point is not None:
            self.lines.append([self.last_point, point_idx])

        self.last_point = point_idx

    def get_start_position(self):
        """Get the starting position for the rider (first point)"""
        if self.points:
            return self.points[0]
        return None

    def clear(self):
        """Clear all points and lines"""
        self.points = []
        self.lines = []
        self.last_point = None
