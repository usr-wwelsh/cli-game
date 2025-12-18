#!/usr/bin/env python3
"""
Terminal Line Rider - Draw tracks and watch physics in action!
"""
import curses
import json
import os
import time
from pathlib import Path
from physics import Rider
from track import Track
from renderer import Renderer

class Game:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.track = Track()
        self.rider = None
        self.renderer = Renderer(stdscr)
        self.mode = 'menu'  # menu, editor, playing, load_menu
        self.running = True
        self.maps_dir = Path(__file__).parent / 'maps'
        self.maps_dir.mkdir(exist_ok=True)

        # Editor state
        self.editor_x = 40
        self.editor_y = 10
        self.paused = False

        # Status message
        self.status_message = ""
        self.status_message_time = 0

        curses.curs_set(0)
        curses.use_default_colors()
        self.stdscr.nodelay(1)
        self.stdscr.timeout(16)  # ~60 FPS

    def run(self):
        """Main game loop"""
        while self.running:
            self.stdscr.clear()

            if self.mode == 'menu':
                self.menu_screen()
            elif self.mode == 'load_menu':
                self.load_menu_screen()
            elif self.mode == 'editor':
                self.editor_screen()
            elif self.mode == 'playing':
                self.playing_screen()

            self.stdscr.refresh()

            key = self.stdscr.getch()
            self.handle_input(key)

    def menu_screen(self):
        """Main menu"""
        height, width = self.stdscr.getmaxyx()

        title = [
            "╔══════════════════════════════════════╗",
            "║     TERMINAL LINE RIDER CLI          ║",
            "╚══════════════════════════════════════╝",
        ]

        for i, line in enumerate(title):
            self.stdscr.addstr(2 + i, width // 2 - len(line) // 2, line,
                             self.renderer.COLOR_MENU | curses.A_BOLD)

        menu_items = [
            "1. New Track (Editor)",
            "2. Load Track",
            "3. Play Default: Beginner Hill",
            "4. Play Default: Death Drop",
            "5. Play Default: Loop-de-Loop",
            "",
            "Q. Quit"
        ]

        for i, item in enumerate(menu_items):
            if item.startswith("3.") or item.startswith("4.") or item.startswith("5."):
                # Highlight default maps in cyan
                self.stdscr.addstr(8 + i, width // 2 - len(item) // 2, item,
                                 self.renderer.COLOR_TRACK)
            elif item.startswith("Q."):
                # Quit in red
                self.stdscr.addstr(8 + i, width // 2 - len(item) // 2, item,
                                 self.renderer.COLOR_RIDER_FAST)
            elif item:
                # Other items in yellow
                self.stdscr.addstr(8 + i, width // 2 - len(item) // 2, item,
                                 self.renderer.COLOR_RIDER_SLOW)

    def load_menu_screen(self):
        """Track selection menu"""
        height, width = self.stdscr.getmaxyx()

        title = "╔═══ SELECT TRACK TO LOAD ═══╗"
        self.stdscr.addstr(2, width // 2 - len(title) // 2, title,
                         self.renderer.COLOR_MENU | curses.A_BOLD)

        tracks = sorted(list(self.maps_dir.glob('*.json')), key=lambda p: p.stat().st_mtime, reverse=True)

        if not tracks:
            msg = "No saved tracks found!"
            self.stdscr.addstr(6, width // 2 - len(msg) // 2, msg,
                             self.renderer.COLOR_RIDER_FAST)
            msg2 = "Press M to return to menu"
            self.stdscr.addstr(8, width // 2 - len(msg2) // 2, msg2,
                             self.renderer.COLOR_POINTS)
        else:
            for i, track_path in enumerate(tracks[:9]):  # Show up to 9 tracks
                # Get file info
                track_name = track_path.stem
                mod_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(track_path.stat().st_mtime))

                # Load track data to show info
                try:
                    with open(track_path, 'r') as f:
                        data = json.load(f)
                    point_count = len(data.get('points', []))
                    line_count = len(data.get('lines', []))
                    info = f"{i+1}. {track_name} - {point_count} points, {line_count} lines - {mod_time}"
                except:
                    info = f"{i+1}. {track_name} - {mod_time}"

                self.stdscr.addstr(6 + i, 2, info[:width-3],
                                 self.renderer.COLOR_RIDER_SLOW)

            instructions = "Press 1-9 to load a track | M: back to menu"
            self.stdscr.addstr(height - 2, width // 2 - len(instructions) // 2, instructions,
                             self.renderer.COLOR_POINTS)

    def editor_screen(self):
        """Track editor"""
        height, width = self.stdscr.getmaxyx()

        # Instructions
        instructions = "EDITOR | WASD: move cursor | SPACE: place/connect point | R: reset rider | P: play | Ctrl+S: save | M: menu"
        self.stdscr.addstr(0, 0, instructions[:width-1], self.renderer.COLOR_POINTS)

        # Render track
        self.renderer.draw_track(self.track)
        self.renderer.draw_cursor(self.editor_x, self.editor_y)

        if self.rider:
            self.renderer.draw_rider(self.rider)

        # Show status message if active (for 2 seconds)
        if self.status_message and time.time() - self.status_message_time < 2.0:
            self.stdscr.addstr(height - 1, 0, self.status_message[:width-1],
                             self.renderer.COLOR_RIDER_SLOW | curses.A_BOLD)

    def playing_screen(self):
        """Playing mode with physics"""
        height, width = self.stdscr.getmaxyx()

        instructions = "PLAYING | R: reset | E: back to editor | M: menu | SPACE: pause"
        self.stdscr.addstr(0, 0, instructions[:width-1], self.renderer.COLOR_DEFAULT)

        # Update physics
        if not self.paused and self.rider and not self.rider.crashed:
            self.rider.update(self.track)

        # Render
        self.renderer.draw_track(self.track)
        if self.rider:
            self.renderer.draw_rider(self.rider)

            # Show stats with color based on speed
            speed = self.rider.velocity_magnitude()
            stats = f"Speed: {speed:.1f} | Pos: ({self.rider.x:.1f}, {self.rider.y:.1f})"

            if self.rider.crashed:
                stats += " | CRASHED!"
                self.stdscr.addstr(1, 0, stats, self.renderer.COLOR_RIDER_FAST | curses.A_BOLD | curses.A_REVERSE)
            elif speed > 8.0:
                self.stdscr.addstr(1, 0, stats, self.renderer.COLOR_RIDER_FAST | curses.A_BOLD)
            elif speed > 5.0:
                self.stdscr.addstr(1, 0, stats, self.renderer.COLOR_RIDER_SLOW | curses.A_BOLD)
            else:
                self.stdscr.addstr(1, 0, stats, self.renderer.COLOR_POINTS)

    def handle_input(self, key):
        """Handle keyboard input based on mode"""
        if key == ord('q') or key == ord('Q'):
            if self.mode == 'menu':
                self.running = False

        if self.mode == 'menu':
            if key == ord('1'):
                self.mode = 'editor'
                self.track = Track()
                self.rider = None
                self.editor_x = 40
                self.editor_y = 10
            elif key == ord('2'):
                self.load_track_menu()
            elif key == ord('3'):
                self.load_default_map('beginner_hill')
            elif key == ord('4'):
                self.load_default_map('death_drop')
            elif key == ord('5'):
                self.load_default_map('loop_de_loop')

        elif self.mode == 'load_menu':
            if key == ord('m') or key == ord('M'):
                self.mode = 'menu'
            elif ord('1') <= key <= ord('9'):
                # Load the selected track
                track_index = key - ord('1')
                tracks = sorted(list(self.maps_dir.glob('*.json')),
                              key=lambda p: p.stat().st_mtime, reverse=True)
                if track_index < len(tracks):
                    self.load_track(tracks[track_index])

        elif self.mode == 'editor':
            if key == ord('w'): self.editor_y = max(2, self.editor_y - 1)
            elif key == ord('s'): self.editor_y = min(self.stdscr.getmaxyx()[0] - 2, self.editor_y + 1)
            elif key == ord('a'): self.editor_x = max(0, self.editor_x - 2)
            elif key == ord('d'): self.editor_x = min(self.stdscr.getmaxyx()[1] - 2, self.editor_x + 2)
            elif key == ord(' '):
                self.track.add_point(self.editor_x, self.editor_y)
            elif key == ord('r'):
                start = self.track.get_start_position()
                if start:
                    self.rider = Rider(start[0], start[1])
            elif key == ord('p'):
                if self.track.lines:
                    start = self.track.get_start_position()
                    if start:
                        self.rider = Rider(start[0], start[1])
                        self.mode = 'playing'
                        self.paused = False
            elif key == 19:  # Ctrl+S
                self.save_track()
            elif key == ord('m'):
                self.mode = 'menu'

        elif self.mode == 'playing':
            if key == ord(' '):
                self.paused = not self.paused
            elif key == ord('r'):
                start = self.track.get_start_position()
                if start:
                    self.rider = Rider(start[0], start[1])
            elif key == ord('e'):
                self.mode = 'editor'
            elif key == ord('m'):
                self.mode = 'menu'

    def save_track(self):
        """Save current track to file"""
        try:
            # Find the highest existing track number
            existing_tracks = list(self.maps_dir.glob('track *.json'))
            track_numbers = []
            for track_path in existing_tracks:
                try:
                    # Extract number from "track N.json"
                    num = int(track_path.stem.replace('track ', ''))
                    track_numbers.append(num)
                except ValueError:
                    continue

            # Get next track number
            next_num = max(track_numbers, default=0) + 1
            filename = f"track {next_num}.json"
            filepath = self.maps_dir / filename

            data = {
                'points': self.track.points,
                'lines': self.track.lines
            }

            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)

            self.status_message = f"✓ Saved: {filename}"
            self.status_message_time = time.time()
        except Exception as e:
            self.status_message = f"✗ Save failed: {str(e)}"
            self.status_message_time = time.time()

    def load_track_menu(self):
        """Switch to track selection menu"""
        self.mode = 'load_menu'

    def load_track(self, filepath):
        """Load track from file"""
        with open(filepath, 'r') as f:
            data = json.load(f)

        self.track = Track()
        self.track.points = data.get('points', [])
        self.track.lines = data.get('lines', [])

        start = self.track.get_start_position()
        if start:
            self.rider = Rider(start[0], start[1])

        self.mode = 'playing'
        self.paused = False

    def load_default_map(self, map_name):
        """Load a default map"""
        default_maps = {
            'beginner_hill': {
                'points': [[10, 20], [30, 20], [50, 25], [70, 25], [90, 30]],
                'lines': [[0, 1], [1, 2], [2, 3], [3, 4]]
            },
            'death_drop': {
                'points': [[10, 10], [30, 10], [32, 30], [50, 30], [70, 35]],
                'lines': [[0, 1], [1, 2], [2, 3], [3, 4]]
            },
            'loop_de_loop': {
                'points': [
                    [10, 10], [20, 10], [25, 15], [30, 20], [35, 25],
                    [40, 28], [45, 28], [50, 25], [55, 20], [60, 15],
                    [65, 10], [80, 10]
                ],
                'lines': [[i, i+1] for i in range(11)]
            }
        }

        if map_name in default_maps:
            data = default_maps[map_name]
            self.track = Track()
            self.track.points = data['points']
            self.track.lines = data['lines']

            start = self.track.get_start_position()
            if start:
                self.rider = Rider(start[0], start[1])

            self.mode = 'playing'
            self.paused = False

def main(stdscr):
    game = Game(stdscr)
    game.run()

if __name__ == '__main__':
    curses.wrapper(main)
