#!/usr/bin/env python3
"""
Regex Raiders - Learn regex through progressive challenges
"""

import re
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.text import Text
from rich import box

from levels import get_level, get_total_levels

console = Console()


class Game:
    def __init__(self):
        self.current_level = 1
        self.total_score = 0
        self.hints_used = 0

    def show_title(self):
        """Display game title"""
        title = Text("REGEX RAIDERS", style="bold cyan", justify="center")
        subtitle = Text("Master Regular Expressions Through Adventure", style="dim", justify="center")

        console.print()
        console.print(Panel(title, box=box.DOUBLE, border_style="cyan"))
        console.print(subtitle)
        console.print()

    def show_level_intro(self, level):
        """Show level introduction"""
        console.print()
        console.print(f"[bold yellow]Level {level.number}:[/bold yellow] [cyan]{level.title}[/cyan]")
        console.print(f"[dim]Concept: {level.concept}[/dim]")
        console.print()
        console.print(f"[white]{level.description}[/white]")
        console.print()

    def show_strings(self, level, matches=None, false_positives=None, missed_targets=None):
        """Display all strings with color-coded feedback"""
        table = Table(title="Strings in the Chamber", box=box.ROUNDED, show_header=True)
        table.add_column("String", style="white")
        table.add_column("Status", style="white")

        for string in level.strings:
            is_target = string in level.targets

            if matches is None:
                # Before any attempt
                status = "[yellow]TARGET[/yellow]" if is_target else "[dim]decoy[/dim]"
                style = "yellow" if is_target else "dim white"
            else:
                # After attempt
                if string in false_positives:
                    status = "[red]FALSE MATCH![/red]"
                    style = "red"
                elif string in missed_targets:
                    status = "[red]MISSED![/red]"
                    style = "red"
                elif string in matches and is_target:
                    status = "[green]CAPTURED![/green]"
                    style = "green"
                elif is_target:
                    status = "[yellow]target[/yellow]"
                    style = "yellow"
                else:
                    status = "[dim]avoided[/dim]"
                    style = "dim white"

            table.add_row(f"[{style}]{string}[/{style}]", status)

        console.print(table)
        console.print()

    def show_hint(self, level):
        """Show progressive hints"""
        if self.hints_used < len(level.hints):
            hint = level.hints[self.hints_used]
            console.print(Panel(f"[yellow]Hint {self.hints_used + 1}:[/yellow] {hint}",
                              border_style="yellow", box=box.ROUNDED))
            self.hints_used += 1
        else:
            console.print("[dim]No more hints available for this level[/dim]")
        console.print()

    def get_pattern(self):
        """Get regex pattern from user"""
        console.print("[cyan]Enter your regex pattern (or 'hint' for help, 'quit' to exit):[/cyan]")
        pattern = Prompt.ask("[bold green]>>[/bold green]")
        return pattern.strip()

    def validate_pattern(self, level, pattern):
        """Validate the regex pattern against the level"""
        try:
            regex_obj = re.compile(pattern)
        except re.error as e:
            console.print(f"[red]Invalid regex pattern:[/red] {e}")
            console.print()
            return None

        result = level.check_solution(pattern, regex_obj)
        return result

    def show_result(self, level, result, pattern):
        """Show the result of the pattern attempt"""
        if result['correct']:
            console.print()
            console.print(Panel("[bold green]SUCCESS![/bold green] You've captured all the targets!",
                              border_style="green", box=box.DOUBLE))
            console.print(f"[cyan]Your pattern:[/cyan] [bold white]{pattern}[/bold white]")
            console.print(f"[cyan]Score:[/cyan] [bold yellow]{result['score']}[/bold yellow] points")
            console.print()
            self.total_score += result['score']
            return True
        else:
            console.print()
            console.print("[red]Not quite right! Let's see what happened:[/red]")
            console.print()

            if result['false_positives']:
                console.print(f"[red]False matches (should NOT match):[/red] {', '.join(result['false_positives'])}")

            if result['missed_targets']:
                console.print(f"[red]Missed targets (should match):[/red] {', '.join(result['missed_targets'])}")

            console.print()
            self.show_strings(level, result['matches'], result['false_positives'], result['missed_targets'])
            return False

    def play_level(self, level):
        """Play a single level"""
        self.hints_used = 0
        self.show_level_intro(level)
        self.show_strings(level)

        while True:
            pattern = self.get_pattern()

            if pattern.lower() == 'quit':
                return False

            if pattern.lower() == 'hint':
                self.show_hint(level)
                continue

            if not pattern:
                console.print("[red]Please enter a pattern[/red]")
                console.print()
                continue

            result = self.validate_pattern(level, pattern)
            if result is None:
                continue

            success = self.show_result(level, result, pattern)
            if success:
                return True

    def show_victory(self):
        """Show final victory message"""
        console.print()
        console.print(Panel(
            f"[bold green]CONGRATULATIONS![/bold green]\n\n"
            f"You've completed all {get_total_levels()} levels!\n"
            f"Total Score: [bold yellow]{self.total_score}[/bold yellow] points\n\n"
            f"You're now a Regex Raider!",
            border_style="green",
            box=box.DOUBLE
        ))
        console.print()

    def run(self):
        """Main game loop"""
        self.show_title()

        console.print("[dim]Learn regex by solving progressive challenges.[/dim]")
        console.print("[dim]Capture the target strings without matching the decoys![/dim]")
        console.print()

        ready = Prompt.ask("[cyan]Ready to start?[/cyan] (y/n)", default="y")
        if ready.lower() != 'y':
            console.print("[yellow]Maybe next time![/yellow]")
            return

        while self.current_level <= get_total_levels():
            level = get_level(self.current_level)

            success = self.play_level(level)

            if not success:
                console.print("[yellow]Thanks for playing![/yellow]")
                console.print(f"[cyan]Final Score:[/cyan] [bold]{self.total_score}[/bold] points")
                break

            self.current_level += 1

            if self.current_level <= get_total_levels():
                console.print("[green]Press Enter to continue to the next level...[/green]")
                input()

        if self.current_level > get_total_levels():
            self.show_victory()


def main():
    """Entry point"""
    try:
        game = Game()
        game.run()
    except KeyboardInterrupt:
        console.print()
        console.print("[yellow]Game interrupted. Thanks for playing![/yellow]")
        sys.exit(0)


if __name__ == "__main__":
    main()
