#!/usr/bin/env python3
"""
Server Strike: Network Wars
A tile-based tower defense CLI game in a post-apocalyptic anarchist network
"""

import json
import os
import random
import time
import math
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

# Import colorama for colored text
try:
    from colorama import init, Fore, Back, Style
    init()
except ImportError:
    print("Warning: colorama not found. Install it with 'pip install colorama'")
    class DummyColor:
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ''
    Fore = Back = Style = DummyColor()

# ============================================================================
# GAME CONSTANTS
# ============================================================================

GRID_WIDTH = 15
GRID_HEIGHT = 10

class TileType(Enum):
    EMPTY = 0
    PATH = 1
    BLOCKED = 2
    SPAWN = 3
    CORE = 4

class EnemyType(Enum):
    BOTNET = "botnet"
    DDOS = "ddos"
    INTRUSION = "intrusion"
    SIPHON = "siphon"
    WORM = "worm"
    ELITE_HACKER = "elite"

class TowerType(Enum):
    FIREWALL = "firewall"
    AI_AGENT = "ai_agent"
    BANDWIDTH_FILTER = "filter"
    QUANTUM_TRAP = "quantum"
    SIGNAL_JAMMER = "jammer"

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class Enemy:
    """Represents an enemy attacking your network"""
    type: EnemyType
    hp: int
    max_hp: int
    speed: float
    position: Tuple[int, int]
    path_index: int
    reward: int
    damage: int  # Damage to core if it reaches
    faction: str = "Rogue Swarm"

    def move(self, path: List[Tuple[int, int]]) -> bool:
        """Move along path, return True if reached end"""
        if self.path_index >= len(path) - 1:
            return True
        self.path_index += 1
        self.position = path[self.path_index]
        return False

@dataclass
class Tower:
    """Represents a defensive tower"""
    type: TowerType
    position: Tuple[int, int]
    level: int = 1
    range: float = 2.5
    damage: int = 10
    attack_speed: float = 1.0
    last_attack: float = 0
    cost: Dict[str, int] = field(default_factory=dict)

    def can_attack(self, current_time: float) -> bool:
        """Check if tower can attack based on attack speed"""
        return current_time - self.last_attack >= (1.0 / self.attack_speed)

    def in_range(self, enemy_pos: Tuple[int, int]) -> bool:
        """Check if enemy is in tower range"""
        dx = self.position[0] - enemy_pos[0]
        dy = self.position[1] - enemy_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        return distance <= self.range

@dataclass
class Faction:
    """Represents a faction in the anarchist network"""
    name: str
    ai_personality: str
    relationship: int  # -100 to 100
    trades_available: List[Dict[str, Any]] = field(default_factory=list)
    hostile: bool = False
    color: str = Fore.WHITE

# ============================================================================
# GAME STATE
# ============================================================================

class GameState:
    """Manages all game state"""

    def __init__(self):
        self.grid: List[List[TileType]] = []
        self.path: List[Tuple[int, int]] = []
        self.towers: List[Tower] = []
        self.enemies: List[Enemy] = []
        self.resources = {"power": 150, "bandwidth": 150, "processing": 150}
        self.core_hp = 100
        self.max_core_hp = 100
        self.wave_number = 0
        self.credits = 100  # Currency for buying towers
        self.in_combat = False
        self.game_time = 0.0

        # Faction system
        self.factions = self._initialize_factions()

        # AI Companion
        self.ai_name = "NEXUS"
        self.ai_personality = "analytical"
        self.ai_rapport = 50

        # Initialize map
        self._generate_map()

    def _initialize_factions(self) -> Dict[str, Faction]:
        """Initialize all factions"""
        return {
            "archivist": Faction(
                name="Archivist Collective",
                ai_personality="Knowledge-obsessed, trades data for resources",
                relationship=20,
                color=Fore.CYAN
            ),
            "redmarket": Faction(
                name="Red Market Syndicate",
                ai_personality="Profit-driven, expensive but reliable",
                relationship=0,
                color=Fore.RED
            ),
            "commune": Faction(
                name="Darknet Commune",
                ai_personality="Idealistic, helps allies generously",
                relationship=30,
                color=Fore.GREEN
            ),
            "swarm": Faction(
                name="Rogue Swarm",
                ai_personality="Hostile hivemind AI, pure aggression",
                relationship=-80,
                hostile=True,
                color=Fore.MAGENTA
            ),
            "corporate": Faction(
                name="Corporate Remnant",
                ai_personality="Old-world corps seeking control",
                relationship=-40,
                hostile=True,
                color=Fore.YELLOW
            )
        }

    def _generate_map(self):
        """Generate the game map with paths"""
        # Initialize empty grid
        self.grid = [[TileType.EMPTY for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

        # Create a winding path from left to right
        # Start on left side
        start_y = GRID_HEIGHT // 2
        current_pos = (0, start_y)
        self.path = [current_pos]

        # Mark spawn point
        self.grid[start_y][0] = TileType.SPAWN

        # Generate path that winds to the right side
        x, y = current_pos
        while x < GRID_WIDTH - 1:
            # Randomly choose to go right, up, or down
            choices = [(x + 1, y)]  # Always can go right
            if y > 0:
                choices.append((x, y - 1))  # Can go up
            if y < GRID_HEIGHT - 1:
                choices.append((x, y + 1))  # Can go down

            # Prefer going right
            if random.random() < 0.6:
                next_pos = (x + 1, y)
            else:
                next_pos = random.choice(choices)

            x, y = next_pos
            if next_pos not in self.path:
                self.path.append(next_pos)
                self.grid[y][x] = TileType.PATH

        # Mark core (endpoint)
        end_x, end_y = self.path[-1]
        self.grid[end_y][end_x] = TileType.CORE

        # Add some blocked terrain randomly
        for _ in range(15):
            bx, by = random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)
            if self.grid[by][bx] == TileType.EMPTY:
                self.grid[by][bx] = TileType.BLOCKED

# ============================================================================
# TOWER DEFINITIONS
# ============================================================================

TOWER_SPECS = {
    TowerType.FIREWALL: {
        "name": "Firewall",
        "cost": {"credits": 50, "power": 10},
        "damage": 15,
        "range": 2.5,
        "attack_speed": 1.0,
        "description": "Basic defense, moderate damage and range",
        "symbol": "F",
        "color": Fore.BLUE
    },
    TowerType.AI_AGENT: {
        "name": "AI Agent",
        "cost": {"credits": 100, "processing": 30},
        "damage": 25,
        "range": 3.0,
        "attack_speed": 0.8,
        "description": "Autonomous AI, high damage, slower attacks",
        "symbol": "A",
        "color": Fore.CYAN
    },
    TowerType.BANDWIDTH_FILTER: {
        "name": "Bandwidth Filter",
        "cost": {"credits": 70, "bandwidth": 20},
        "damage": 8,
        "range": 2.0,
        "attack_speed": 2.5,
        "description": "Fast attacks, lower damage, good against swarms",
        "symbol": "B",
        "color": Fore.GREEN
    },
    TowerType.QUANTUM_TRAP: {
        "name": "Quantum Trap",
        "cost": {"credits": 150, "processing": 50, "power": 20},
        "damage": 50,
        "range": 2.0,
        "attack_speed": 0.3,
        "description": "Devastating damage but very slow",
        "symbol": "Q",
        "color": Fore.MAGENTA
    },
    TowerType.SIGNAL_JAMMER: {
        "name": "Signal Jammer",
        "cost": {"credits": 80, "power": 25},
        "damage": 12,
        "range": 4.0,
        "attack_speed": 1.2,
        "description": "Excellent range, moderate damage",
        "symbol": "J",
        "color": Fore.YELLOW
    }
}

# ============================================================================
# ENEMY DEFINITIONS
# ============================================================================

ENEMY_SPECS = {
    EnemyType.BOTNET: {
        "name": "Botnet Drone",
        "hp": 30,
        "speed": 1.0,
        "reward": 10,
        "damage": 5,
        "symbol": "b",
        "color": Fore.RED
    },
    EnemyType.DDOS: {
        "name": "DDoS Packet",
        "hp": 15,
        "speed": 2.0,
        "reward": 8,
        "damage": 3,
        "symbol": "d",
        "color": Fore.YELLOW
    },
    EnemyType.INTRUSION: {
        "name": "Intrusion Attempt",
        "hp": 50,
        "speed": 0.7,
        "reward": 20,
        "damage": 10,
        "symbol": "i",
        "color": Fore.MAGENTA
    },
    EnemyType.SIPHON: {
        "name": "Resource Siphon",
        "hp": 40,
        "speed": 0.8,
        "reward": 15,
        "damage": 8,
        "symbol": "s",
        "color": Fore.CYAN
    },
    EnemyType.WORM: {
        "name": "Network Worm",
        "hp": 20,
        "speed": 1.5,
        "reward": 12,
        "damage": 4,
        "symbol": "w",
        "color": Fore.GREEN
    },
    EnemyType.ELITE_HACKER: {
        "name": "Elite Hacker",
        "hp": 100,
        "speed": 0.5,
        "reward": 50,
        "damage": 20,
        "symbol": "E",
        "color": Fore.RED + Style.BRIGHT
    }
}

# ============================================================================
# RENDERING
# ============================================================================

def clear_screen():
    """Clear terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def render_map(state: GameState, show_ranges: bool = False, selected_pos: Optional[Tuple[int, int]] = None):
    """Render the game map"""
    print(f"\n{Fore.CYAN}╔{'═' * (GRID_WIDTH * 4 + 1)}╗{Style.RESET_ALL}")

    for y in range(GRID_HEIGHT):
        print(f"{Fore.CYAN}║{Style.RESET_ALL} ", end="")
        for x in range(GRID_WIDTH):
            tile = state.grid[y][x]
            pos = (x, y)

            # Check if there's an enemy here
            enemy_here = None
            for enemy in state.enemies:
                if enemy.position == pos:
                    enemy_here = enemy
                    break

            # Check if there's a tower here
            tower_here = None
            for tower in state.towers:
                if tower.position == pos:
                    tower_here = tower
                    break

            # Determine what to display
            if enemy_here:
                spec = ENEMY_SPECS[enemy_here.type]
                print(f"{spec['color']}{spec['symbol']:^3}{Style.RESET_ALL}", end=" ")
            elif tower_here:
                spec = TOWER_SPECS[tower_here.type]
                symbol = f"{spec['symbol']}{tower_here.level}"
                print(f"{spec['color']}{symbol:^3}{Style.RESET_ALL}", end=" ")
            elif selected_pos == pos:
                print(f"{Fore.WHITE}{Back.BLUE}[ ]{Style.RESET_ALL}", end=" ")
            elif show_ranges and selected_pos and tower_here is None:
                # Show range indicator if a tower is selected
                for tower in state.towers:
                    if tower.position == selected_pos and tower.in_range(pos):
                        print(f"{Fore.BLUE}···{Style.RESET_ALL}", end=" ")
                        break
                else:
                    print(_get_tile_symbol(tile), end=" ")
            else:
                print(_get_tile_symbol(tile), end=" ")

        print(f"{Fore.CYAN}║{Style.RESET_ALL}")

    print(f"{Fore.CYAN}╚{'═' * (GRID_WIDTH * 4 + 1)}╝{Style.RESET_ALL}")

def _get_tile_symbol(tile: TileType) -> str:
    """Get the symbol for a tile type"""
    symbols = {
        TileType.EMPTY: f"{Fore.WHITE}[ ]{Style.RESET_ALL}",
        TileType.PATH: f"{Fore.YELLOW}[·]{Style.RESET_ALL}",
        TileType.BLOCKED: f"{Fore.WHITE}[#]{Style.RESET_ALL}",
        TileType.SPAWN: f"{Fore.RED}[S]{Style.RESET_ALL}",
        TileType.CORE: f"{Fore.GREEN}[C]{Style.RESET_ALL}"
    }
    return symbols.get(tile, "[ ]")

def render_hud(state: GameState):
    """Render the game HUD"""
    print(f"\n{Fore.YELLOW}╔════════════════ STATUS ════════════════╗{Style.RESET_ALL}")

    # Core HP bar
    hp_percent = state.core_hp / state.max_core_hp
    hp_color = Fore.GREEN if hp_percent > 0.6 else Fore.YELLOW if hp_percent > 0.3 else Fore.RED
    hp_bar = "█" * int(hp_percent * 20)
    print(f"Core HP: {hp_color}{hp_bar:20}{Style.RESET_ALL} {state.core_hp}/{state.max_core_hp}")

    # Resources
    print(f"\nCredits: {Fore.YELLOW}{state.credits}{Style.RESET_ALL}")
    print(f"Power: {Fore.CYAN}{state.resources['power']}{Style.RESET_ALL} | ", end="")
    print(f"Bandwidth: {Fore.GREEN}{state.resources['bandwidth']}{Style.RESET_ALL} | ", end="")
    print(f"Processing: {Fore.MAGENTA}{state.resources['processing']}{Style.RESET_ALL}")

    # Wave info
    print(f"\nWave: {Fore.RED}{state.wave_number}{Style.RESET_ALL}")
    print(f"Enemies: {Fore.RED}{len(state.enemies)}{Style.RESET_ALL}")
    print(f"Towers: {Fore.BLUE}{len(state.towers)}{Style.RESET_ALL}")

    print(f"{Fore.YELLOW}╚════════════════════════════════════════╝{Style.RESET_ALL}")

def print_ai_message(state: GameState, message: str):
    """Print a message from the AI companion"""
    print(f"\n{Fore.CYAN}[{state.ai_name}]:{Style.RESET_ALL} {message}")

def print_ascii_logo():
    """Print game logo"""
    logo = f"""{Fore.CYAN}
   ███████╗███████╗██████╗ ██╗   ██╗███████╗██████╗
   ██╔════╝██╔════╝██╔══██╗██║   ██║██╔════╝██╔══██╗
   ███████╗█████╗  ██████╔╝██║   ██║█████╗  ██████╔╝
   ╚════██║██╔══╝  ██╔══██╗╚██╗ ██╔╝██╔══╝  ██╔══██╗
   ███████║███████╗██║  ██║ ╚████╔╝ ███████╗██║  ██║
   ╚══════╝╚══════╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝

   ███████╗████████╗██████╗ ██╗██╗  ██╗███████╗
   ██╔════╝╚══██╔══╝██╔══██╗██║██║ ██╔╝██╔════╝
   ███████╗   ██║   ██████╔╝██║█████╔╝ █████╗
   ╚════██║   ██║   ██╔══██╗██║██╔═██╗ ██╔══╝
   ███████║   ██║   ██║  ██║██║██║  ██╗███████╗
   ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚══════╝
{Style.RESET_ALL}
        {Fore.YELLOW}NETWORK WARS - DEFEND THE ANARCHIST NET{Style.RESET_ALL}
"""
    print(logo)

# ============================================================================
# WAVE GENERATION
# ============================================================================

def generate_wave(state: GameState) -> List[Enemy]:
    """Generate enemies for the current wave"""
    wave_num = state.wave_number
    enemies = []

    # Determine wave composition based on wave number
    if wave_num <= 3:
        # Early waves: mostly weak enemies
        for _ in range(5 + wave_num * 2):
            enemy_type = random.choice([EnemyType.BOTNET, EnemyType.DDOS])
            enemies.append(_create_enemy(enemy_type, state))
    elif wave_num <= 7:
        # Mid waves: mixed composition
        for _ in range(8 + wave_num):
            enemy_type = random.choice([EnemyType.BOTNET, EnemyType.DDOS, EnemyType.WORM, EnemyType.SIPHON])
            enemies.append(_create_enemy(enemy_type, state))
    elif wave_num <= 12:
        # Late waves: harder enemies
        for _ in range(10 + wave_num):
            enemy_type = random.choice([EnemyType.INTRUSION, EnemyType.SIPHON, EnemyType.WORM])
            enemies.append(_create_enemy(enemy_type, state))
        # Add an elite
        if wave_num % 3 == 0:
            enemies.append(_create_enemy(EnemyType.ELITE_HACKER, state))
    else:
        # Boss waves
        for _ in range(15):
            enemy_type = random.choice(list(EnemyType))
            enemies.append(_create_enemy(enemy_type, state))
        for _ in range(wave_num // 5):
            enemies.append(_create_enemy(EnemyType.ELITE_HACKER, state))

    return enemies

def _create_enemy(enemy_type: EnemyType, state: GameState) -> Enemy:
    """Create an enemy of the specified type"""
    spec = ENEMY_SPECS[enemy_type]

    # Scale HP with wave number
    hp_multiplier = 1 + (state.wave_number * 0.15)
    hp = int(spec["hp"] * hp_multiplier)

    return Enemy(
        type=enemy_type,
        hp=hp,
        max_hp=hp,
        speed=spec["speed"],
        position=state.path[0],
        path_index=0,
        reward=spec["reward"],
        damage=spec["damage"]
    )

# ============================================================================
# COMBAT SIMULATION
# ============================================================================

def simulate_combat_tick(state: GameState) -> bool:
    """Simulate one tick of combat. Returns True if wave is complete."""
    state.game_time += 0.1

    # Move enemies
    enemies_to_remove = []
    for enemy in state.enemies:
        # Move based on speed (slower enemies move less frequently)
        if random.random() < enemy.speed * 0.3:
            reached_core = enemy.move(state.path)
            if reached_core:
                state.core_hp -= enemy.damage
                enemies_to_remove.append(enemy)
                print_ai_message(state, f"{Fore.RED}Warning! Enemy reached core! -{enemy.damage} HP{Style.RESET_ALL}")

    # Remove enemies that reached core
    for enemy in enemies_to_remove:
        state.enemies.remove(enemy)

    # Towers attack
    for tower in state.towers:
        if tower.can_attack(state.game_time):
            # Find enemies in range
            targets = [e for e in state.enemies if tower.in_range(e.position)]
            if targets:
                # Attack first enemy in range
                target = targets[0]
                target.hp -= tower.damage
                tower.last_attack = state.game_time

                # Remove dead enemies
                if target.hp <= 0:
                    state.enemies.remove(target)
                    state.credits += target.reward

    # Check if wave complete
    return len(state.enemies) == 0

# ============================================================================
# BUILD MODE
# ============================================================================

def build_mode(state: GameState):
    """Enter build mode to place towers"""
    clear_screen()
    print_ascii_logo()
    print(f"\n{Fore.YELLOW}BUILD MODE{Style.RESET_ALL}")
    print("Place your defenses before the next wave!\n")

    render_map(state)
    render_hud(state)

    print(f"\n{Fore.CYAN}Available Towers:{Style.RESET_ALL}")
    for i, (tower_type, spec) in enumerate(TOWER_SPECS.items(), 1):
        cost_str = ", ".join([f"{v} {k}" for k, v in spec['cost'].items()])
        print(f"{i}. {spec['color']}{spec['name']}{Style.RESET_ALL} - {cost_str}")
        print(f"   {spec['description']}")
        print(f"   Damage: {spec['damage']} | Range: {spec['range']} | Speed: {spec['attack_speed']}/s")

    print(f"\n{Fore.YELLOW}Commands:{Style.RESET_ALL}")
    print("build <tower_num> <x> <y> - Place a tower")
    print("upgrade <x> <y> - Upgrade a tower")
    print("info <x> <y> - Show tower info")
    print("trade - Visit faction trading")
    print("start - Start the wave")
    print("quit - Exit game")

    while True:
        cmd = input(f"\n{Fore.MAGENTA}>{Style.RESET_ALL} ").strip().lower().split()

        if not cmd:
            continue

        if cmd[0] == "start":
            return True
        elif cmd[0] == "quit":
            return False
        elif cmd[0] == "trade":
            faction_trade(state)
            build_mode(state)
            return True
        elif cmd[0] == "build" and len(cmd) == 4:
            try:
                tower_num = int(cmd[1])
                x, y = int(cmd[2]), int(cmd[3])
                place_tower(state, tower_num, x, y)

                # Refresh display
                clear_screen()
                print_ascii_logo()
                render_map(state)
                render_hud(state)
            except ValueError:
                print(f"{Fore.RED}Invalid coordinates{Style.RESET_ALL}")
        elif cmd[0] == "upgrade" and len(cmd) == 3:
            try:
                x, y = int(cmd[1]), int(cmd[2])
                upgrade_tower(state, x, y)

                clear_screen()
                print_ascii_logo()
                render_map(state)
                render_hud(state)
            except ValueError:
                print(f"{Fore.RED}Invalid coordinates{Style.RESET_ALL}")
        elif cmd[0] == "info" and len(cmd) == 3:
            try:
                x, y = int(cmd[1]), int(cmd[2])
                show_tower_info(state, x, y)
            except ValueError:
                print(f"{Fore.RED}Invalid coordinates{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Unknown command{Style.RESET_ALL}")

def place_tower(state: GameState, tower_num: int, x: int, y: int):
    """Place a tower at the specified position"""
    # Validate tower number
    tower_types = list(TOWER_SPECS.keys())
    if tower_num < 1 or tower_num > len(tower_types):
        print(f"{Fore.RED}Invalid tower type{Style.RESET_ALL}")
        return

    tower_type = tower_types[tower_num - 1]
    spec = TOWER_SPECS[tower_type]

    # Check position is valid
    if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
        print(f"{Fore.RED}Position out of bounds{Style.RESET_ALL}")
        return

    # Check tile is empty
    if state.grid[y][x] != TileType.EMPTY:
        print(f"{Fore.RED}Can't build here - tile is not empty{Style.RESET_ALL}")
        return

    # Check if tower already exists here
    for tower in state.towers:
        if tower.position == (x, y):
            print(f"{Fore.RED}Tower already exists here{Style.RESET_ALL}")
            return

    # Check resources
    if state.credits < spec['cost'].get('credits', 0):
        print(f"{Fore.RED}Not enough credits{Style.RESET_ALL}")
        return

    for resource, amount in spec['cost'].items():
        if resource != 'credits' and state.resources.get(resource, 0) < amount:
            print(f"{Fore.RED}Not enough {resource}{Style.RESET_ALL}")
            return

    # Deduct resources
    state.credits -= spec['cost'].get('credits', 0)
    for resource, amount in spec['cost'].items():
        if resource != 'credits':
            state.resources[resource] -= amount

    # Create tower
    tower = Tower(
        type=tower_type,
        position=(x, y),
        level=1,
        range=spec['range'],
        damage=spec['damage'],
        attack_speed=spec['attack_speed'],
        cost=spec['cost']
    )
    state.towers.append(tower)

    print(f"{Fore.GREEN}Placed {spec['name']} at ({x}, {y}){Style.RESET_ALL}")

def upgrade_tower(state: GameState, x: int, y: int):
    """Upgrade a tower"""
    tower = None
    for t in state.towers:
        if t.position == (x, y):
            tower = t
            break

    if not tower:
        print(f"{Fore.RED}No tower at this position{Style.RESET_ALL}")
        return

    # Calculate upgrade cost (50% of base cost per level)
    upgrade_cost = int(50 * tower.level * 0.5)

    if state.credits < upgrade_cost:
        print(f"{Fore.RED}Not enough credits. Need {upgrade_cost}{Style.RESET_ALL}")
        return

    # Upgrade tower
    state.credits -= upgrade_cost
    tower.level += 1
    tower.damage = int(tower.damage * 1.3)
    tower.range += 0.3
    tower.attack_speed *= 1.1

    print(f"{Fore.GREEN}Upgraded tower to level {tower.level}!{Style.RESET_ALL}")
    print(f"New stats - Damage: {tower.damage}, Range: {tower.range:.1f}, Speed: {tower.attack_speed:.1f}/s")

def show_tower_info(state: GameState, x: int, y: int):
    """Show information about a tower"""
    tower = None
    for t in state.towers:
        if t.position == (x, y):
            tower = t
            break

    if not tower:
        print(f"{Fore.RED}No tower at this position{Style.RESET_ALL}")
        return

    spec = TOWER_SPECS[tower.type]
    print(f"\n{spec['color']}{spec['name']} (Level {tower.level}){Style.RESET_ALL}")
    print(f"Position: ({x}, {y})")
    print(f"Damage: {tower.damage}")
    print(f"Range: {tower.range:.1f}")
    print(f"Attack Speed: {tower.attack_speed:.1f}/s")

# ============================================================================
# FACTION TRADING
# ============================================================================

def faction_trade(state: GameState):
    """Enter faction trading interface"""
    clear_screen()
    print_ascii_logo()
    print(f"\n{Fore.YELLOW}FACTION DIPLOMACY{Style.RESET_ALL}")
    print("Trade resources and build relationships with other nodes\n")

    print(f"{Fore.CYAN}Your Resources:{Style.RESET_ALL}")
    print(f"Credits: {state.credits}")
    for res, amount in state.resources.items():
        print(f"{res.capitalize()}: {amount}")

    print(f"\n{Fore.CYAN}Factions:{Style.RESET_ALL}")
    for i, (fid, faction) in enumerate(state.factions.items(), 1):
        rel_color = Fore.GREEN if faction.relationship > 30 else Fore.YELLOW if faction.relationship > -30 else Fore.RED
        hostility = " [HOSTILE]" if faction.hostile else ""
        print(f"{i}. {faction.color}{faction.name}{Style.RESET_ALL} - Relationship: {rel_color}{faction.relationship}/100{Style.RESET_ALL}{hostility}")
        print(f"   AI: {faction.ai_personality}")

    print(f"\n{Fore.YELLOW}Commands:{Style.RESET_ALL}")
    print("talk <faction_num> - Initiate trade with faction")
    print("back - Return to build mode")

    while True:
        cmd = input(f"\n{Fore.MAGENTA}>{Style.RESET_ALL} ").strip().lower().split()

        if not cmd:
            continue

        if cmd[0] == "back":
            return
        elif cmd[0] == "talk" and len(cmd) == 2:
            try:
                faction_num = int(cmd[1])
                faction_ids = list(state.factions.keys())
                if 1 <= faction_num <= len(faction_ids):
                    faction = state.factions[faction_ids[faction_num - 1]]
                    faction_interaction(state, faction)
                    return
                else:
                    print(f"{Fore.RED}Invalid faction number{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Invalid input{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Unknown command{Style.RESET_ALL}")

def faction_interaction(state: GameState, faction: Faction):
    """Interact with a specific faction"""
    clear_screen()
    print(f"\n{faction.color}=== {faction.name.upper()} ==={Style.RESET_ALL}")
    print(f"AI Personality: {faction.ai_personality}")
    print(f"Relationship: {faction.relationship}/100")

    if faction.hostile and faction.relationship < -50:
        print(f"\n{Fore.RED}[AI]: We have nothing to discuss. Prepare for attack.{Style.RESET_ALL}")
        faction.relationship -= 5
        time.sleep(2)
        return

    # Generate trade offers based on faction and relationship
    print(f"\n{Fore.CYAN}Available Trades:{Style.RESET_ALL}")

    # Generate some random trades
    trades = []
    if faction.name == "Archivist Collective":
        trades = [
            {"give": {"credits": 30}, "receive": {"processing": 40}, "description": "Trade credits for processing power"},
            {"give": {"bandwidth": 30}, "receive": {"credits": 40}, "description": "Trade bandwidth for credits"}
        ]
    elif faction.name == "Red Market Syndicate":
        trades = [
            {"give": {"credits": 50}, "receive": {"power": 60}, "description": "Buy power"},
            {"give": {"credits": 80}, "receive": {"processing": 50, "bandwidth": 50}, "description": "Buy resource package"}
        ]
    elif faction.name == "Darknet Commune":
        # Better deals if good relationship
        multiplier = 1.5 if faction.relationship > 50 else 1.0
        trades = [
            {"give": {"credits": int(20 / multiplier)}, "receive": {"power": 40}, "description": "Community trade - power"},
            {"give": {"credits": int(25 / multiplier)}, "receive": {"bandwidth": 50}, "description": "Community trade - bandwidth"}
        ]
    else:
        trades = [
            {"give": {"credits": 40}, "receive": {"power": 40}, "description": "Standard trade"},
        ]

    for i, trade in enumerate(trades, 1):
        give_str = ", ".join([f"{v} {k}" for k, v in trade["give"].items()])
        receive_str = ", ".join([f"{v} {k}" for k, v in trade["receive"].items()])
        print(f"{i}. {trade['description']}")
        print(f"   Give: {Fore.RED}{give_str}{Style.RESET_ALL} -> Receive: {Fore.GREEN}{receive_str}{Style.RESET_ALL}")

    print("\nEnter trade number to accept, or 'back' to return")

    cmd = input(f"\n{Fore.MAGENTA}>{Style.RESET_ALL} ").strip().lower()

    if cmd == "back":
        return

    try:
        trade_num = int(cmd)
        if 1 <= trade_num <= len(trades):
            trade = trades[trade_num - 1]

            # Check if player can afford
            can_afford = True
            for resource, amount in trade["give"].items():
                if resource == "credits":
                    if state.credits < amount:
                        can_afford = False
                        break
                elif state.resources.get(resource, 0) < amount:
                    can_afford = False
                    break

            if not can_afford:
                print(f"{Fore.RED}You can't afford this trade{Style.RESET_ALL}")
                time.sleep(1.5)
                return

            # Execute trade
            for resource, amount in trade["give"].items():
                if resource == "credits":
                    state.credits -= amount
                else:
                    state.resources[resource] -= amount

            for resource, amount in trade["receive"].items():
                if resource == "credits":
                    state.credits += amount
                else:
                    state.resources[resource] += amount

            faction.relationship += 5
            print(f"{Fore.GREEN}Trade complete! Relationship improved.{Style.RESET_ALL}")
            time.sleep(1.5)
    except ValueError:
        print(f"{Fore.RED}Invalid input{Style.RESET_ALL}")
        time.sleep(1)

# ============================================================================
# MAIN GAME LOOP
# ============================================================================

def main():
    """Main game function"""
    clear_screen()
    print_ascii_logo()

    print(f"\n{Fore.CYAN}Year 2087. The Internet has collapsed.{Style.RESET_ALL}")
    print("Anarchist nodes fight for control of the fragmented network.")
    print("You must defend your node against hostile factions.")
    print("\nYour AI companion will guide you.\n")

    input("Press Enter to begin...")

    state = GameState()

    # AI introduction
    clear_screen()
    print_ai_message(state, f"Systems online. I am {state.ai_name}, your integrated AI companion.")
    print_ai_message(state, "I will assist in network defense and provide tactical analysis.")
    print_ai_message(state, "Hostile factions detected. Prepare for incoming attacks.")
    time.sleep(3)

    # Main game loop
    game_running = True

    while game_running and state.core_hp > 0:
        state.wave_number += 1

        # Build phase
        print_ai_message(state, f"Wave {state.wave_number} approaching. Deploy defenses.")
        time.sleep(1)

        if not build_mode(state):
            # Player quit
            break

        # Generate wave
        state.enemies = generate_wave(state)
        state.in_combat = True

        print_ai_message(state, f"{Fore.RED}Wave {state.wave_number} incoming! {len(state.enemies)} hostiles detected!{Style.RESET_ALL}")
        time.sleep(2)

        # Combat phase
        while state.enemies and state.core_hp > 0:
            clear_screen()
            print_ascii_logo()
            print(f"\n{Fore.RED}WAVE {state.wave_number} IN PROGRESS{Style.RESET_ALL}\n")

            render_map(state)
            render_hud(state)

            # Simulate combat tick
            wave_complete = simulate_combat_tick(state)

            if wave_complete:
                break

            time.sleep(0.15)  # Animation speed

        state.in_combat = False

        # Check if player lost
        if state.core_hp <= 0:
            clear_screen()
            print(f"\n{Fore.RED}{'='*50}")
            print("CORE DESTROYED")
            print(f"{'='*50}{Style.RESET_ALL}\n")
            print(f"Your node has fallen to wave {state.wave_number}")
            print(f"The network fragmentspread further into darkness...")
            print_ai_message(state, "Critical failure. Systems offline. This was... inevitable.")
            break

        # Wave complete
        clear_screen()
        print(f"\n{Fore.GREEN}{'='*50}")
        print(f"WAVE {state.wave_number} COMPLETE")
        print(f"{'='*50}{Style.RESET_ALL}\n")
        print_ai_message(state, f"Wave neutralized. Well executed.")

        # Rewards
        wave_bonus = 50 + (state.wave_number * 10)
        state.credits += wave_bonus
        print(f"\n{Fore.YELLOW}+{wave_bonus} credits{Style.RESET_ALL}")

        # Resource regeneration
        for resource in state.resources:
            regen = random.randint(10, 20)
            state.resources[resource] += regen
            print(f"{Fore.GREEN}+{regen} {resource}{Style.RESET_ALL}")

        time.sleep(3)

        # Check win condition
        if state.wave_number >= 20:
            clear_screen()
            print(f"\n{Fore.GREEN}{'='*50}")
            print("VICTORY!")
            print(f"{'='*50}{Style.RESET_ALL}\n")
            print(f"You have defended your node through {state.wave_number} waves!")
            print("Your network stands strong in the anarchist web.")
            print_ai_message(state, "Exceptional performance. The node is secure... for now.")
            break

    print(f"\n{Fore.CYAN}Thanks for playing Server Strike: Network Wars!{Style.RESET_ALL}\n")

if __name__ == "__main__":
    main()
