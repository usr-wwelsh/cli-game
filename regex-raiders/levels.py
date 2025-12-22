"""Level definitions for Regex Raiders"""

class Level:
    def __init__(self, number, title, description, strings, targets, hints, concept):
        self.number = number
        self.title = title
        self.description = description
        self.strings = strings  # All strings in the level
        self.targets = targets  # Strings that should match
        self.hints = hints  # Progressive hints
        self.concept = concept  # What regex concept this teaches

    def check_solution(self, pattern, regex_obj):
        """Check if the pattern correctly matches targets and nothing else"""
        matches = []
        false_positives = []
        missed_targets = []

        for string in self.strings:
            match = regex_obj.search(string)
            if match:
                matches.append(string)
                if string not in self.targets:
                    false_positives.append(string)

        for target in self.targets:
            if target not in matches:
                missed_targets.append(target)

        is_correct = len(false_positives) == 0 and len(missed_targets) == 0

        return {
            'correct': is_correct,
            'matches': matches,
            'false_positives': false_positives,
            'missed_targets': missed_targets,
            'score': self.calculate_score(pattern, is_correct)
        }

    def calculate_score(self, pattern, is_correct):
        """Score based on correctness and pattern efficiency"""
        if not is_correct:
            return 0
        # Shorter patterns get higher scores (encourage efficiency)
        base_score = 1000
        length_penalty = len(pattern) * 5
        return max(base_score - length_penalty, 100)


# Level definitions
LEVELS = [
    Level(
        number=1,
        title="Literal Match",
        description="Match the word 'treasure' exactly",
        strings=[
            "treasure",
            "TREASURE",
            "treasure chest",
            "hidden treasure",
            "pleasure",
            "measure",
            "gold",
        ],
        targets=["treasure", "treasure chest", "hidden treasure"],
        hints=[
            "Just type the word literally",
            "Regex can match substrings - 'treasure' will match any string containing it"
        ],
        concept="Literal matching"
    ),

    Level(
        number=2,
        title="Start and End",
        description="Match lines that START with 'gold'",
        strings=[
            "gold coins",
            "gold",
            "pure gold bar",
            "not gold",
            "goldfish",
        ],
        targets=["gold coins", "gold", "goldfish"],
        hints=[
            "Use ^ to match the start of a string",
            "Pattern: ^gold"
        ],
        concept="Anchors: ^ and $"
    ),

    Level(
        number=3,
        title="Any Character",
        description="Match 'c.t' pattern (cat, cot, cut, but not coat)",
        strings=[
            "cat",
            "cot",
            "cut",
            "coat",
            "c t",
            "cart",
            "cast",
        ],
        targets=["cat", "cot", "cut", "c t"],
        hints=[
            "Use . to match any single character",
            "Pattern: c.t will match c + any char + t"
        ],
        concept="Wildcard: ."
    ),

    Level(
        number=4,
        title="Character Classes",
        description="Match only lowercase vowels (a, e, i, o, u)",
        strings=[
            "a", "e", "i", "o", "u",
            "A", "E", "I", "O", "U",
            "b", "x", "y",
        ],
        targets=["a", "e", "i", "o", "u"],
        hints=[
            "Use square brackets to define a character class",
            "Pattern: [aeiou]"
        ],
        concept="Character classes: [...]"
    ),

    Level(
        number=5,
        title="Digit Hunt",
        description="Match strings containing any digit",
        strings=[
            "room101",
            "level99",
            "nodigits",
            "test",
            "5",
            "code",
            "h4x0r",
        ],
        targets=["room101", "level99", "5", "h4x0r"],
        hints=[
            "Use \\d to match any digit",
            "\\d is shorthand for [0-9]"
        ],
        concept="Shorthand: \\d for digits"
    ),

    Level(
        number=6,
        title="Repetition",
        description="Match strings with 2 or more consecutive 'o' characters",
        strings=[
            "book",
            "food",
            "good",
            "door",
            "one",
            "cool",
            "oooo",
        ],
        targets=["book", "food", "good", "door", "cool", "oooo"],
        hints=[
            "Use + to match one or more",
            "Use {n,} to match n or more",
            "Pattern: o{2,} or oo+"
        ],
        concept="Quantifiers: +, *, {n,m}"
    ),

    Level(
        number=7,
        title="Optional Characters",
        description="Match 'color' and 'colour' (American and British spelling)",
        strings=[
            "color",
            "colour",
            "colored",
            "coloured",
            "colors",
            "discolor",
        ],
        targets=["color", "colour", "colored", "coloured", "colors", "discolor"],
        hints=[
            "Use ? to make a character optional",
            "Pattern: colou?r makes the 'u' optional"
        ],
        concept="Optional: ?"
    ),

    Level(
        number=8,
        title="Email Extraction",
        description="Match valid simple email addresses",
        strings=[
            "user@example.com",
            "admin@site.org",
            "invalid@",
            "@invalid.com",
            "no-at-sign.com",
            "test.user@domain.co.uk",
        ],
        targets=["user@example.com", "admin@site.org", "test.user@domain.co.uk"],
        hints=[
            "Pattern: text + @ + text + . + text",
            "Use \\w+ for word characters",
            "Pattern: \\w+@\\w+\\.\\w+"
        ],
        concept="Real-world: Email matching"
    ),

    Level(
        number=9,
        title="Word Boundaries",
        description="Match the word 'cat' but not in 'category' or 'concat'",
        strings=[
            "cat",
            "the cat sat",
            "category",
            "concat",
            "cats",
            "cat.",
        ],
        targets=["cat", "the cat sat", "cat."],
        hints=[
            "Use \\b for word boundary",
            "Pattern: \\bcat\\b",
            "Word boundary ensures it's a complete word"
        ],
        concept="Word boundaries: \\b"
    ),

    Level(
        number=10,
        title="IP Address Hunt",
        description="Match valid IPv4 addresses (simple version)",
        strings=[
            "192.168.1.1",
            "10.0.0.1",
            "255.255.255.255",
            "999.999.999.999",
            "192.168",
            "not.an.ip.address",
        ],
        targets=["192.168.1.1", "10.0.0.1", "255.255.255.255"],
        hints=[
            "Pattern: digit(s) + . + digit(s) + . + digit(s) + . + digit(s)",
            "Use \\d+ for one or more digits",
            "Pattern: \\d+\\.\\d+\\.\\d+\\.\\d+",
            "Note: This accepts 999.999... but it's a good start!"
        ],
        concept="Real-world: IP addresses"
    ),
]


def get_level(level_number):
    """Get level by number"""
    if 1 <= level_number <= len(LEVELS):
        return LEVELS[level_number - 1]
    return None


def get_total_levels():
    """Get total number of levels"""
    return len(LEVELS)
