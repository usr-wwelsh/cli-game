"""
ASCII renderer for track and rider
"""
import curses
import math

class Renderer:
    def __init__(self, stdscr):
        self.stdscr = stdscr

        # Initialize colors
        curses.start_color()

        # Try to use default colors (transparent background)
        try:
            curses.use_default_colors()
            bg = -1
        except:
            bg = curses.COLOR_BLACK

        curses.init_pair(1, curses.COLOR_CYAN, bg)      # Track lines
        curses.init_pair(2, curses.COLOR_GREEN, bg)     # Track points
        curses.init_pair(3, curses.COLOR_YELLOW, bg)    # Slow rider
        curses.init_pair(4, curses.COLOR_RED, bg)       # Fast rider / crashed
        curses.init_pair(5, curses.COLOR_MAGENTA, bg)   # Cursor
        curses.init_pair(6, curses.COLOR_BLUE, bg)      # Menu
        curses.init_pair(7, curses.COLOR_WHITE, bg)     # Default

        self.COLOR_TRACK = curses.color_pair(1)
        self.COLOR_POINTS = curses.color_pair(2)
        self.COLOR_RIDER_SLOW = curses.color_pair(3)
        self.COLOR_RIDER_FAST = curses.color_pair(4)
        self.COLOR_CURSOR = curses.color_pair(5)
        self.COLOR_MENU = curses.color_pair(6)
        self.COLOR_DEFAULT = curses.color_pair(7)

    def draw_track(self, track):
        """Draw all track lines"""
        for line_idx in track.lines:
            p1 = track.points[line_idx[0]]
            p2 = track.points[line_idx[1]]
            self.draw_line(p1[0], p1[1], p2[0], p2[1], '=', self.COLOR_TRACK)

        # Draw points
        for point in track.points:
            self.safe_addstr(int(point[1]), int(point[0]), 'o', self.COLOR_POINTS | curses.A_BOLD)

    def draw_line(self, x1, y1, x2, y2, char='=', color=None):
        """Draw a line between two points using Bresenham's algorithm"""
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

        dx = abs(x2 - x1)
        dy = abs(y2 - y1)

        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1

        err = dx - dy

        while True:
            if color:
                self.safe_addstr(y1, x1, char, color | curses.A_BOLD)
            else:
                self.safe_addstr(y1, x1, char)

            if x1 == x2 and y1 == y2:
                break

            e2 = 2 * err

            if e2 > -dy:
                err -= dy
                x1 += sx

            if e2 < dx:
                err += dx
                y1 += sy

    def draw_rider(self, rider):
        """Draw the rider (stick figure on a sled)"""
        x, y = int(rider.x), int(rider.y)

        if rider.crashed:
            # Crashed animation - red and flashing
            self.safe_addstr(y, x, 'X', self.COLOR_RIDER_FAST | curses.A_BOLD | curses.A_REVERSE)
        else:
            # Simple rider character
            # Calculate angle based on velocity for cooler effect
            angle = math.atan2(rider.vy, rider.vx)

            if abs(angle) < 0.5:  # Mostly horizontal
                rider_char = 'o>'
            elif angle > 1.0:  # Going down
                rider_char = 'o\\'
            elif angle < -1.0:  # Going up
                rider_char = 'o/'
            else:
                rider_char = 'o-'

            # Color based on speed - yellow when slow, red when fast
            speed = rider.velocity_magnitude()
            if speed > 8.0:
                color = self.COLOR_RIDER_FAST | curses.A_BOLD
            elif speed > 5.0:
                color = self.COLOR_RIDER_SLOW | curses.A_BOLD
            else:
                color = self.COLOR_RIDER_SLOW

            self.safe_addstr(y, x, rider_char, color)

    def draw_cursor(self, x, y):
        """Draw the editor cursor"""
        self.safe_addstr(y, x, '+', self.COLOR_CURSOR | curses.A_BOLD | curses.A_REVERSE)

    def safe_addstr(self, y, x, text, *args):
        """Safely add string to screen (handles out of bounds)"""
        height, width = self.stdscr.getmaxyx()

        if 0 <= y < height - 1 and 0 <= x < width - len(str(text)):
            try:
                self.stdscr.addstr(y, x, text, *args)
            except curses.error:
                pass
