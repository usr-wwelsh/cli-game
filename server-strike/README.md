# Server Strike: Network Wars

## Overview
Server Strike is a tile-based tower defense CLI game set in 2087, after the collapse of the Internet. As a Network Defender with an integrated AI companion, you must defend your node against waves of attacks from hostile anarchist factions fighting for control of the fragmented network.

## Gameplay

### Tower Defense Combat
- **Tile-Based Map**: A grid battlefield with paths enemies follow from spawn to your core
- **Tower Placement**: Build defensive structures (Firewalls, AI Agents, Bandwidth Filters, etc.) on empty tiles
- **Wave-Based Combat**: Defend against progressively harder waves of enemies
- **Real-Time Animation**: Watch enemies move along paths and towers attack in real-time
- **Resource Management**: Balance credits, power, bandwidth, and processing to build and upgrade defenses

### Between Waves
- **Faction Diplomacy**: Trade resources with other anarchist nodes
- **Reputation System**: Build relationships that affect trade prices and faction behavior
- **Strategic Planning**: Decide where to place new towers and which to upgrade
- **Resource Trading**: Exchange resources with different factions based on their personalities

### The Factions
Each faction is run by an advanced AI with unique personality and trade behavior:

- **Archivist Collective** (Neutral, Friendly)
  - Knowledge-obsessed, trades data for resources
  - Offers processing power and information trades

- **Red Market Syndicate** (Neutral)
  - Anarcho-capitalist traders
  - Expensive but reliable resource packages

- **Darknet Commune** (Friendly)
  - Idealistic hackers
  - Better deals if you have good reputation

- **Rogue Swarm** (Hostile)
  - Hostile hivemind AI
  - Primary source of attacks

- **Corporate Remnant** (Hostile)
  - Old-world tech corporations
  - Trying to regain control of the network

### Your AI Companion: NEXUS
- Provides tactical analysis and warnings during combat
- Autonomous personality that comments on gameplay
- Guides you through waves and alerts you to threats

## Tower Types

1. **Firewall** (50 credits, 10 power)
   - Basic defense with moderate damage and range
   - Good all-around starter tower

2. **AI Agent** (100 credits, 30 processing)
   - Autonomous AI defense
   - High damage but slower attacks

3. **Bandwidth Filter** (70 credits, 20 bandwidth)
   - Fast attack speed, lower damage
   - Excellent against swarms of weak enemies

4. **Quantum Trap** (150 credits, 50 processing, 20 power)
   - Devastating damage but very slow
   - Best for high-HP enemies

5. **Signal Jammer** (80 credits, 25 power)
   - Excellent range, moderate damage
   - Good for covering large areas

### Tower Upgrades
- Upgrade any tower to increase damage, range, and attack speed
- Each level costs more but provides significant stat boosts
- Strategic upgrading vs. building new towers is key

## Enemy Types

- **Botnet Drone** (b) - Basic enemy, moderate HP and speed
- **DDoS Packet** (d) - Fast but weak, comes in swarms
- **Network Worm** (w) - Quick and evasive
- **Resource Siphon** (s) - Moderate threat, steals resources
- **Intrusion Attempt** (i) - Slow but high HP
- **Elite Hacker** (E) - Boss enemy, very high HP and damage

Enemies get stronger with each wave!

## Commands

### Build Mode
- `build <tower_num> <x> <y>` - Place a tower at coordinates (x, y)
- `upgrade <x> <y>` - Upgrade tower at position
- `info <x> <y>` - Show detailed tower information
- `trade` - Enter faction diplomacy/trading
- `start` - Begin the wave
- `quit` - Exit game

### Trading Mode
- `talk <faction_num>` - Initiate trade with a faction
- `<trade_num>` - Accept a trade offer
- `back` - Return to build mode

## How to Play

1. **Install dependencies**:
   ```bash
   pip install colorama
   ```

2. **Run the game**:
   ```bash
   python main.py
   ```

3. **Game Flow**:
   - Build Phase: Place towers and trade with factions
   - Combat Phase: Watch your defenses fight automatically
   - Rewards: Earn credits and resources for surviving
   - Repeat until wave 20 or core destruction

## Strategy Tips

### Early Game (Waves 1-5)
- Place Firewalls near the path early on
- Focus on covering the most path tiles with tower range
- Don't overspend - save some credits for emergrades

### Mid Game (Waves 6-12)
- Start upgrading your best-positioned towers
- Use faction trading to balance resources
- Place AI Agents at chokepoints for maximum damage
- Build relationship with Darknet Commune for better trades

### Late Game (Waves 13-20)
- Upgrade key towers to level 3+
- Use Quantum Traps for high-HP enemies
- Maintain good resource reserves for emergency builds
- Trade strategically between waves

### Tower Placement
- Place towers on tiles adjacent to the path for maximum coverage
- Use long-range towers (Signal Jammers) to cover multiple path sections
- Create "kill zones" where multiple tower ranges overlap
- Don't forget to defend near your core!

### Resource Management
- Credits are your primary currency - earn them by killing enemies
- Power, Bandwidth, and Processing are needed for specific towers
- Trade excess resources with factions for what you need
- Different factions offer different exchange rates

## Win/Lose Conditions

**Victory**: Survive 20 waves and secure the anarchist network

**Defeat**: Core HP reaches 0 (enemies breach your defenses)

## Map Legend

- `[ ]` - Empty tile (can build here)
- `[·]` - Path tile (enemies walk here)
- `[#]` - Blocked terrain
- `[S]` - Spawn point (enemies appear here)
- `[C]` - Core (your base - defend this!)
- `F1`, `A2`, etc. - Towers (letter = type, number = level)
- `b`, `d`, `i`, etc. - Enemies (colored, moving along path)

## The Lore

In 2087, the global Internet collapsed in what became known as the "Great Fragmentation." Anarchist nodes emerged from the ruins, each controlled by advanced agentic AIs. These independent nodes form a loose network - the last digital infrastructure of humanity.

You control one such node, protected by NEXUS, your integrated AI companion. Hostile factions like the Rogue Swarm and Corporate Remnant constantly attack, trying to seize control or destroy competition. Meanwhile, neutral and friendly factions offer trade and alliances - for a price.

Survival depends on your tactical skill, resource management, and diplomatic savvy. The anarchist network is brutal, but it's all that remains.

Can you defend your node and bring order to the chaos?

---

## Technical Details

- Written in Python 3.6+
- Uses `colorama` for cross-platform colored terminal output
- Tile-based combat simulation with real-time rendering
- Dynamic wave generation scales with difficulty
- Procedural path generation for replayability

Enjoy defending the anarchist net, Commander.
