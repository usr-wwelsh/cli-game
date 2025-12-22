# Regex Raiders

Learn regular expressions through progressive challenges. Capture target strings while avoiding decoys!

## Features

- 10 progressive levels teaching regex concepts from basics to real-world patterns
- Color-coded visual feedback showing matches, misses, and false positives
- Scoring system that rewards efficient patterns
- Progressive hint system for each level
- Clean terminal UI using Rich library

## Concepts Covered

1. Literal matching
2. Anchors (^, $)
3. Wildcard (.)
4. Character classes ([...])
5. Digit shorthand (\d)
6. Quantifiers (+, *, {n,m})
7. Optional characters (?)
8. Email matching (real-world)
9. Word boundaries (\b)
10. IP address matching (real-world)

## Installation

```bash
pip install -r requirements.txt
```

## How to Play

```bash
python main.py
```

### Gameplay

Each level presents you with:
- A collection of strings
- Some are TARGETS (marked in yellow) - you must match these
- Others are DECOYS - you must NOT match these

Your goal: Write a regex pattern that matches ALL targets and NO decoys.

### Commands

- Enter your regex pattern to test it
- Type `hint` to get progressive hints for the level
- Type `quit` to exit the game

### Scoring

- Shorter patterns score higher (encourages learning efficient regex)
- Base score: 1000 points
- Penalty: -5 points per character
- Wrong answers: 0 points (try again!)

### Tips

- Start simple - you can always add complexity
- Use the hint system if you're stuck
- Pay attention to what matches and what doesn't after each attempt
- The game teaches progressively - each level builds on previous concepts

## Example Level

```
Level 1: Literal Match
Match the word 'treasure' exactly

Strings:
- treasure        [TARGET]
- treasure chest  [TARGET]
- pleasure        [decoy]
- gold            [decoy]

Solution: treasure
```

## Learning Path

The game is designed to teach regex in a natural progression:
- Start with exact text matching
- Learn special characters and wildcards
- Master quantifiers for repetition
- Apply concepts to real-world patterns (emails, IPs)

Have fun raiding!
