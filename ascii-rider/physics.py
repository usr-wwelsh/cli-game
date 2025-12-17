"""
Physics engine for the rider
"""
import math

class Rider:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vx = 1.0  # Start with forward velocity
        self.vy = 0.0
        self.crashed = False
        self.on_track = False

        # Physics constants
        self.gravity = 0.4  # Reduced gravity to prevent falling through
        self.friction = 0.995  # Very low friction for smooth riding
        self.air_resistance = 0.99
        self.bounce = 0.4
        self.max_speed = 12.0  # Reduced max speed to prevent phasing through track
        self.crash_threshold = 10.0

    def update(self, track, dt=1.0):
        """Update rider position and velocity"""
        if self.crashed:
            return

        # Apply gravity
        self.vy += self.gravity * dt

        # Apply air resistance when not on track
        if not self.on_track:
            self.vx *= self.air_resistance
            self.vy *= self.air_resistance

        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Check collision with track
        self.on_track = False
        collision = self.check_collision(track)

        if collision:
            line_start, line_end, collision_point = collision
            self.on_track = True

            # Calculate line direction (tangent)
            dx = line_end[0] - line_start[0]
            dy = line_end[1] - line_start[1]
            length = math.sqrt(dx*dx + dy*dy)

            if length > 0:
                # Normalize tangent
                tx = dx / length
                ty = dy / length

                # Normal is perpendicular (rotate 90 degrees)
                nx = -ty
                ny = tx

                # Move rider to surface
                self.x = collision_point[0]
                self.y = collision_point[1]

                # Current velocity magnitude
                speed = math.sqrt(self.vx**2 + self.vy**2)

                # Velocity projected onto normal (perpendicular to surface)
                normal_velocity = self.vx * nx + self.vy * ny

                # Check for crash (too much perpendicular velocity)
                if normal_velocity < -self.crash_threshold:
                    self.crashed = True
                    self.vx = 0
                    self.vy = 0
                    return

                # If moving into the surface, redirect along tangent
                if normal_velocity < 0:
                    # Remove normal component and add to tangent
                    self.vx -= normal_velocity * nx * (1 + self.bounce)
                    self.vy -= normal_velocity * ny * (1 + self.bounce)

                # Project velocity onto tangent (along surface)
                tangent_velocity = self.vx * tx + self.vy * ty

                # Keep moving along the surface with friction
                self.vx = tangent_velocity * tx * self.friction
                self.vy = tangent_velocity * ty * self.friction

                # Add gravity component along the slope
                gravity_along_slope = self.gravity * ty
                self.vx += gravity_along_slope * tx * dt
                self.vy += gravity_along_slope * ty * dt

        # Limit max speed
        speed = math.sqrt(self.vx**2 + self.vy**2)
        if speed > self.max_speed:
            self.vx = (self.vx / speed) * self.max_speed
            self.vy = (self.vy / speed) * self.max_speed

        # Check if fallen off screen (out of bounds)
        if self.y > 100 or self.y < -10 or self.x < -10 or self.x > 200:
            self.crashed = True

    def check_collision(self, track):
        """Check if rider collides with any track line"""
        closest_collision = None
        min_dist = 4.0  # Increased collision threshold to prevent falling through

        for line_idx in track.lines:
            p1 = track.points[line_idx[0]]
            p2 = track.points[line_idx[1]]

            # Check if rider is near this line segment
            closest = self.closest_point_on_line(p1, p2)

            if closest:
                dist = math.sqrt((self.x - closest[0])**2 + (self.y - closest[1])**2)

                # Find the closest collision
                if dist < min_dist:
                    min_dist = dist
                    closest_collision = (p1, p2, closest)

        return closest_collision

    def closest_point_on_line(self, p1, p2):
        """Find closest point on line segment to rider"""
        x1, y1 = p1[0], p1[1]
        x2, y2 = p2[0], p2[1]

        dx = x2 - x1
        dy = y2 - y1

        if dx == 0 and dy == 0:
            return p1

        # Parameter t of closest point on line
        t = ((self.x - x1) * dx + (self.y - y1) * dy) / (dx*dx + dy*dy)

        # Clamp t to line segment
        t = max(0, min(1, t))

        # Closest point
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy

        return (closest_x, closest_y)

    def velocity_magnitude(self):
        """Get current speed"""
        return math.sqrt(self.vx**2 + self.vy**2)
