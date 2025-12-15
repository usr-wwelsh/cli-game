#!/usr/bin/env python3
"""
CLI Infrastructure Tycoon - An AWS/Terraform-themed Incremental Game
Enhanced with beautiful visuals and educational challenges!
"""

import time
import random
import os
import json
from typing import Dict, List, NamedTuple, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.layout import Layout
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.live import Live
from rich.align import Align
from rich import box
from datetime import datetime

console = Console()


def load_challenges_from_file(filename: str = "challenges.json") -> List[Dict]:
    """Load challenges from JSON file."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(script_dir, filename)

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('challenges', [])
    except FileNotFoundError:
        console.print(f"[yellow]Warning: {filename} not found. Using default challenges.[/yellow]")
        return []
    except json.JSONDecodeError:
        console.print(f"[red]Error: Invalid JSON in {filename}[/red]")
        return []


class InfrastructureAsset(NamedTuple):
    """Represents an infrastructure asset in the game."""
    name: str
    base_cost: float
    revenue_per_sec: float
    terraform_resource: str
    description: str
    emoji: str
    tier: int  # 1-3, affects unlock requirements


class Challenge(NamedTuple):
    """Represents an educational challenge."""
    name: str
    description: str
    question: str
    options: List[str]
    correct_answer: int
    explanation: str
    asset_affected: Optional[str]
    difficulty: str  # "easy", "medium", "hard"
    category: str  # "security", "performance", "cost", "architecture"


class Achievement(NamedTuple):
    """Represents an achievement."""
    name: str
    description: str
    emoji: str
    condition: str  # Type of condition to check


class GameState:
    """Manages the game's state."""
    def __init__(self):
        self.money = 100.0
        self.total_revenue = 100.0
        self.last_update = time.time()
        self.last_income_update = time.time()  # Track when income was last calculated
        self.challenges = []
        self.challenge_streak = 0
        self.challenges_solved = 0
        self.challenges_failed = 0

        # Achievement tracking
        self.achievements_unlocked = set()
        self.total_assets_purchased = 0
        self.peak_income = 0.0

        # Define infrastructure assets
        self.asset_types = {
            'ec2': InfrastructureAsset(
                name="EC2 Instances",
                base_cost=15.0,
                revenue_per_sec=1.0,
                terraform_resource="aws_instance",
                description="Virtual servers in the cloud",
                emoji="🖥️",
                tier=1
            ),
            's3': InfrastructureAsset(
                name="S3 Storage",
                base_cost=25.0,
                revenue_per_sec=2.0,
                terraform_resource="aws_s3_bucket",
                description="Object storage for static content",
                emoji="🗄️",
                tier=1
            ),
            'lb': InfrastructureAsset(
                name="Load Balancers",
                base_cost=60.0,
                revenue_per_sec=5.0,
                terraform_resource="aws_lb",
                description="Distribute traffic across instances",
                emoji="⚖️",
                tier=2
            ),
            'db': InfrastructureAsset(
                name="RDS Databases",
                base_cost=120.0,
                revenue_per_sec=10.0,
                terraform_resource="aws_db_instance",
                description="Managed relational databases",
                emoji="💾",
                tier=2
            ),
            'lambda': InfrastructureAsset(
                name="Lambda Functions",
                base_cost=250.0,
                revenue_per_sec=25.0,
                terraform_resource="aws_lambda_function",
                description="Serverless computing",
                emoji="⚡",
                tier=3
            ),
            'vpc': InfrastructureAsset(
                name="VPC Networks",
                base_cost=600.0,
                revenue_per_sec=50.0,
                terraform_resource="aws_vpc",
                description="Virtual private clouds",
                emoji="🌐",
                tier=3
            ),
            'cloudfront': InfrastructureAsset(
                name="CloudFront CDN",
                base_cost=350.0,
                revenue_per_sec=35.0,
                terraform_resource="aws_cloudfront_distribution",
                description="Content delivery network",
                emoji="🚀",
                tier=3
            ),
        }

        # Player's owned assets
        self.assets = {asset_id: 0 for asset_id in self.asset_types.keys()}

        # Income tracking
        self.income_per_second = 0.0

        # Health tracking
        self.asset_health = {asset_id: 100.0 for asset_id in self.asset_types.keys()}

        # Challenge timing
        self.last_challenge_time = time.time()

        # Define achievements
        self.all_achievements = [
            Achievement("First Purchase", "Buy your first asset", "🎉", "first_asset"),
            Achievement("Cloud Novice", "Own 5 total assets", "🌱", "total_5"),
            Achievement("Infrastructure Pro", "Own 25 total assets", "💼", "total_25"),
            Achievement("Cloud Architect", "Own 100 total assets", "🏗️", "total_100"),
            Achievement("Quiz Master", "Solve 10 challenges correctly", "🧠", "solve_10"),
            Achievement("Perfect Score", "Get 5 challenges correct in a row", "⭐", "streak_5"),
            Achievement("Money Maker", "Reach $10K income/sec", "💰", "income_10k"),
            Achievement("Cloud Tycoon", "Reach $100K total revenue", "👑", "revenue_100k"),
            Achievement("Diversified", "Own at least one of each asset type", "🎯", "diversified"),
        ]

    def calculate_asset_cost(self, asset_id: str, count: int = 1) -> float:
        """Calculate the cost of purchasing assets."""
        base_cost = self.asset_types[asset_id].base_cost
        total_cost = 0.0
        for i in range(count):
            total_cost += base_cost * (1.15 ** (self.assets[asset_id] + i))
        return total_cost

    def purchase_asset(self, asset_id: str, count: int = 1) -> bool:
        """Attempt to purchase an asset."""
        cost = self.calculate_asset_cost(asset_id, count)
        if self.money >= cost:
            # Apply any pending income at OLD rate before purchase
            current_time = time.time()
            dt = current_time - self.last_income_update
            if dt > 0:
                self.update_money(dt)
                self.last_income_update = current_time

            self.money -= cost
            self.assets[asset_id] += count
            self.total_assets_purchased += count
            if self.asset_health[asset_id] < 50:
                self.asset_health[asset_id] = 100.0
            self.update_income()
            self.check_achievements()
            return True
        return False

    def update_income(self):
        """Recalculate total income per second."""
        self.income_per_second = 0.0
        for asset_id, count in self.assets.items():
            if count > 0:
                revenue = self.asset_types[asset_id].revenue_per_sec
                health_factor = self.asset_health[asset_id] / 100.0
                self.income_per_second += revenue * count * health_factor

        if self.income_per_second > self.peak_income:
            self.peak_income = self.income_per_second
            self.check_achievements()

    def update_money(self, dt: float):
        """Update money based on income."""
        earnings = self.income_per_second * dt
        self.money += earnings
        self.total_revenue += earnings
        self.check_achievements()

    def check_achievements(self):
        """Check and unlock achievements."""
        for achievement in self.all_achievements:
            if achievement.name in self.achievements_unlocked:
                continue

            unlocked = False
            if achievement.condition == "first_asset" and self.total_assets_purchased >= 1:
                unlocked = True
            elif achievement.condition == "total_5" and self.total_assets_purchased >= 5:
                unlocked = True
            elif achievement.condition == "total_25" and self.total_assets_purchased >= 25:
                unlocked = True
            elif achievement.condition == "total_100" and self.total_assets_purchased >= 100:
                unlocked = True
            elif achievement.condition == "solve_10" and self.challenges_solved >= 10:
                unlocked = True
            elif achievement.condition == "streak_5" and self.challenge_streak >= 5:
                unlocked = True
            elif achievement.condition == "income_10k" and self.peak_income >= 10000:
                unlocked = True
            elif achievement.condition == "revenue_100k" and self.total_revenue >= 100000:
                unlocked = True
            elif achievement.condition == "diversified":
                if all(count > 0 for count in self.assets.values()):
                    unlocked = True

            if unlocked:
                self.achievements_unlocked.add(achievement.name)
                console.print(Panel(
                    f"[bold yellow]{achievement.emoji} Achievement Unlocked![/bold yellow]\n"
                    f"[cyan]{achievement.name}[/cyan]\n{achievement.description}",
                    border_style="yellow",
                    box=box.DOUBLE
                ))
                time.sleep(1.5)

    def generate_challenge(self) -> Optional[Challenge]:
        """Generate an educational challenge from JSON file."""
        current_time = time.time()
        if current_time - self.last_challenge_time < 45:
            return None

        if sum(self.assets.values()) == 0:
            return None

        # Probability increases with progress
        if random.random() > 0.15:
            return None

        self.last_challenge_time = current_time

        # Select random owned asset
        owned_assets = [aid for aid, count in self.assets.items() if count > 0]
        if not owned_assets:
            return None

        affected_asset = random.choice(owned_assets)

        # Load challenges from JSON file
        challenges_data = load_challenges_from_file()
        if not challenges_data:
            return None

        # Select random challenge and create Challenge object
        challenge_dict = random.choice(challenges_data)

        return Challenge(
            name=challenge_dict.get('name', 'Unknown Challenge'),
            description=challenge_dict.get('description', ''),
            question=challenge_dict.get('question', ''),
            options=challenge_dict.get('options', []),
            correct_answer=challenge_dict.get('correct_answer', 0),
            explanation=challenge_dict.get('explanation', ''),
            asset_affected=affected_asset,
            difficulty=challenge_dict.get('difficulty', 'medium'),
            category=challenge_dict.get('category', 'general')
        )

    def handle_challenge(self, challenge: Challenge, answer_index: int) -> bool:
        """Handle challenge resolution based on user's answer."""
        correct = (answer_index == challenge.correct_answer)

        if correct:
            self.challenges_solved += 1
            self.challenge_streak += 1
            # Restore health and give reward
            self.asset_health[challenge.asset_affected] = min(100.0,
                self.asset_health[challenge.asset_affected] + 25.0)
            reward = self.income_per_second * 10  # 10 seconds worth of income
            self.money += reward
            self.check_achievements()
            return True
        else:
            self.challenges_failed += 1
            self.challenge_streak = 0
            # Reduce health
            self.asset_health[challenge.asset_affected] *= 0.7
            return False


def format_number(num: float) -> str:
    """Format large numbers with suffixes."""
    if num >= 1e12:
        return f"${num/1e12:.2f}T"
    elif num >= 1e9:
        return f"${num/1e9:.2f}B"
    elif num >= 1e6:
        return f"${num/1e6:.2f}M"
    elif num >= 1e3:
        return f"${num/1e3:.2f}K"
    else:
        return f"${num:.2f}"


def get_health_color(health: float) -> str:
    """Get color based on health percentage."""
    if health >= 80:
        return "green"
    elif health >= 50:
        return "yellow"
    elif health >= 25:
        return "orange"
    else:
        return "red"


def get_health_bar(health: float, width: int = 10) -> str:
    """Create a visual health bar."""
    filled = int((health / 100) * width)
    bar = "█" * filled + "░" * (width - filled)
    color = get_health_color(health)
    return f"[{color}]{bar}[/{color}]"


def display_dashboard(game_state: GameState):
    """Display beautiful dashboard with all game info."""
    console.clear()

    # Header
    header = Panel(
        Align.center(
            Text("☁️  AWS INFRASTRUCTURE TYCOON  ☁️", style="bold cyan", justify="center")
        ),
        border_style="bright_blue",
        box=box.DOUBLE
    )
    console.print(header)

    # Stats Panel
    stats_table = Table.grid(padding=(0, 2))
    stats_table.add_column(style="cyan", justify="right")
    stats_table.add_column(style="green bold", justify="left")

    stats_table.add_row("💰 Cash:", format_number(game_state.money))
    stats_table.add_row("📈 Income/sec:", f"[bold green]{format_number(game_state.income_per_second)}/sec[/bold green]")
    stats_table.add_row("💎 Total Revenue:", format_number(game_state.total_revenue))
    stats_table.add_row("🎯 Challenges Solved:", f"[green]{game_state.challenges_solved}[/green] 🔥 Streak: {game_state.challenge_streak}")
    stats_table.add_row("🏆 Achievements:", f"{len(game_state.achievements_unlocked)}/{len(game_state.all_achievements)}")

    stats_panel = Panel(stats_table, title="[bold]📊 Statistics[/bold]", border_style="green")
    console.print(stats_panel)

    # Assets Panel
    assets_table = Table(box=box.ROUNDED, border_style="blue")
    assets_table.add_column("Asset", style="cyan", no_wrap=True)
    assets_table.add_column("Qty", justify="center", style="yellow")
    assets_table.add_column("Health", justify="center")
    assets_table.add_column("Income", justify="right", style="green")
    assets_table.add_column("Terraform", style="dim")

    for asset_id, count in game_state.assets.items():
        if count > 0:
            asset = game_state.asset_types[asset_id]
            health = game_state.asset_health[asset_id]
            income = asset.revenue_per_sec * count * (health / 100)

            assets_table.add_row(
                f"{asset.emoji} {asset.name}",
                str(count),
                get_health_bar(health, 8) + f" {health:.0f}%",
                format_number(income) + "/s",
                f"[dim]{asset.terraform_resource}[/dim]"
            )

    if sum(game_state.assets.values()) > 0:
        assets_panel = Panel(assets_table, title="[bold]🖥️  Your Infrastructure[/bold]", border_style="blue")
        console.print(assets_panel)
    else:
        console.print(Panel(
            "[yellow]No infrastructure deployed yet. Start building your cloud empire![/yellow]",
            title="[bold]🖥️  Your Infrastructure[/bold]",
            border_style="blue"
        ))

    # Active Challenges
    if game_state.challenges:
        challenge_text = f"[bold red]⚠️  {len(game_state.challenges)} Active Challenge(s) - Address them in the Challenges menu![/bold red]"
        console.print(Panel(challenge_text, border_style="red"))

    # Menu
    menu_text = Text()
    menu_text.append("\n Commands: ", style="bold white")
    menu_text.append("[P]", style="bold cyan")
    menu_text.append("urchase  ", style="white")
    menu_text.append("[C]", style="bold cyan")
    menu_text.append("hallenges  ", style="white")
    menu_text.append("[A]", style="bold cyan")
    menu_text.append("chievements  ", style="white")
    menu_text.append("[I]", style="bold cyan")
    menu_text.append("nfo  ", style="white")
    menu_text.append("[Q]", style="bold cyan")
    menu_text.append("uit", style="white")

    console.print(Panel(menu_text, border_style="white"))


def display_purchase_menu(game_state: GameState):
    """Display purchase menu with beautiful formatting."""
    while True:
        console.clear()

        header = Panel(
            Align.center("🛒  PURCHASE INFRASTRUCTURE  🛒"),
            style="bold yellow",
            border_style="yellow",
            box=box.DOUBLE
        )
        console.print(header)

        console.print(f"\n[bold green]💰 Available Cash: {format_number(game_state.money)}[/bold green]\n")

        # Create assets table
        table = Table(box=box.ROUNDED, border_style="yellow", show_header=True)
        table.add_column("#", style="cyan", justify="center")
        table.add_column("Asset", style="cyan bold")
        table.add_column("Cost", justify="right", style="yellow")
        table.add_column("Income", justify="right", style="green")
        table.add_column("Owned", justify="center", style="blue")
        table.add_column("Tier", justify="center")

        for i, (asset_id, asset) in enumerate(game_state.asset_types.items(), 1):
            cost = game_state.calculate_asset_cost(asset_id, 1)
            affordable = "✓" if game_state.money >= cost else "✗"
            affordable_color = "green" if game_state.money >= cost else "red"

            tier_stars = "⭐" * asset.tier

            table.add_row(
                str(i),
                f"{asset.emoji} {asset.name}",
                f"[{affordable_color}]{format_number(cost)}[/{affordable_color}] {affordable}",
                f"{format_number(asset.revenue_per_sec)}/s",
                str(game_state.assets[asset_id]),
                tier_stars
            )

        console.print(table)

        console.print("\n[dim]Tip: Higher tier assets are more powerful but cost more![/dim]")
        choice = Prompt.ask(
            "\n[bold cyan]Enter asset number to purchase, or 'b' to go back[/bold cyan]",
            default="b"
        )

        if choice.lower() == 'b':
            break

        if choice.isdigit():
            idx = int(choice) - 1
            asset_ids = list(game_state.asset_types.keys())

            if 0 <= idx < len(asset_ids):
                asset_id = asset_ids[idx]
                asset = game_state.asset_types[asset_id]

                # Show detailed info
                cost = game_state.calculate_asset_cost(asset_id, 1)
                console.print(f"\n[bold]{asset.emoji} {asset.name}[/bold]")
                console.print(f"[dim]{asset.description}[/dim]")
                console.print(f"[yellow]Cost: {format_number(cost)}[/yellow]")
                console.print(f"[green]Income: {format_number(asset.revenue_per_sec)}/s[/green]")
                console.print(f"[blue]Terraform: {asset.terraform_resource}[/blue]")

                max_affordable = calculate_max_affordable(game_state, asset_id)
                console.print(f"\n[dim]You can afford up to {max_affordable} unit(s)[/dim]")

                qty = Prompt.ask(f"[cyan]How many to purchase?[/cyan]", default="1")

                if qty.isdigit() and int(qty) > 0:
                    quantity = int(qty)
                    total_cost = sum(
                        game_state.asset_types[asset_id].base_cost * (1.15 ** (game_state.assets[asset_id] + i))
                        for i in range(quantity)
                    )

                    if game_state.money >= total_cost:
                        game_state.money -= total_cost
                        game_state.assets[asset_id] += quantity
                        game_state.total_assets_purchased += quantity
                        game_state.update_income()
                        game_state.check_achievements()

                        console.print(f"\n[bold green]✓ Purchased {quantity}x {asset.name} for {format_number(total_cost)}![/bold green]")
                        time.sleep(1.5)
                    else:
                        console.print(f"\n[bold red]✗ Insufficient funds! Need {format_number(total_cost)}[/bold red]")
                        time.sleep(1.5)


def calculate_max_affordable(game_state: GameState, asset_id: str) -> int:
    """Calculate maximum affordable quantity."""
    money = game_state.money
    count = 0
    current_count = game_state.assets[asset_id]

    while True:
        cost = game_state.asset_types[asset_id].base_cost * (1.15 ** (current_count + count))
        if money >= cost:
            money -= cost
            count += 1
        else:
            break

    return count


def display_challenge_menu(game_state: GameState):
    """Display and handle challenges."""
    # Generate new challenge if needed
    if not game_state.challenges:
        new_challenge = game_state.generate_challenge()
        if new_challenge:
            game_state.challenges.append(new_challenge)

    if not game_state.challenges:
        console.clear()
        console.print(Panel(
            "[green]✓ No active challenges! Your infrastructure is running smoothly.\n"
            "Challenges will appear as your infrastructure grows.[/green]",
            title="[bold]🎯 Challenges[/bold]",
            border_style="green"
        ))
        Prompt.ask("\nPress Enter to continue", default="")
        return

    challenge = game_state.challenges[0]

    console.clear()

    # Challenge header
    difficulty_colors = {"easy": "green", "medium": "yellow", "hard": "red"}
    category_emojis = {
        "security": "🔒",
        "performance": "⚡",
        "cost": "💰",
        "architecture": "🏗️"
    }

    header = Panel(
        Align.center(
            f"[bold]{category_emojis.get(challenge.category, '🎯')} {challenge.name}[/bold]\n"
            f"[{difficulty_colors[challenge.difficulty]}]Difficulty: {challenge.difficulty.upper()}[/{difficulty_colors[challenge.difficulty]}] | "
            f"Category: {challenge.category.title()}"
        ),
        border_style=difficulty_colors[challenge.difficulty],
        box=box.DOUBLE
    )
    console.print(header)

    # Challenge description
    console.print(Panel(
        f"[yellow]{challenge.description}[/yellow]\n\n"
        f"[white]Affected Asset: {game_state.asset_types[challenge.asset_affected].emoji} "
        f"{game_state.asset_types[challenge.asset_affected].name}[/white]",
        title="[bold]📋 Situation[/bold]",
        border_style="yellow"
    ))

    # Question
    console.print(f"\n[bold cyan]❓ {challenge.question}[/bold cyan]\n")

    # Options
    for i, option in enumerate(challenge.options):
        console.print(f"  [{i+1}] {option}")

    # Streak indicator
    if game_state.challenge_streak > 0:
        console.print(f"\n[bold green]🔥 Current Streak: {game_state.challenge_streak}[/bold green]")

    answer = Prompt.ask(
        "\n[bold]Select your answer (1-4) or 'b' to skip[/bold]",
        choices=["1", "2", "3", "4", "b"],
        default="b"
    )

    if answer == 'b':
        return

    answer_idx = int(answer) - 1
    correct = game_state.handle_challenge(challenge, answer_idx)

    # Show result
    console.clear()
    if correct:
        reward = game_state.income_per_second * 10
        result_panel = Panel(
            f"[bold green]✓ CORRECT![/bold green]\n\n"
            f"[white]{challenge.explanation}[/white]\n\n"
            f"[yellow]Rewards:[/yellow]\n"
            f"  • Asset health restored: +25%\n"
            f"  • Bonus cash: {format_number(reward)}\n"
            f"  • Streak: 🔥 {game_state.challenge_streak}",
            title="[bold green]🎉 Success![/bold green]",
            border_style="green",
            box=box.DOUBLE
        )
        console.print(result_panel)
    else:
        result_panel = Panel(
            f"[bold red]✗ INCORRECT[/bold red]\n\n"
            f"[white]{challenge.explanation}[/white]\n\n"
            f"[yellow]Consequences:[/yellow]\n"
            f"  • Asset health reduced: -30%\n"
            f"  • Streak reset: {game_state.challenge_streak} → 0",
            title="[bold red]❌ Failed[/bold red]",
            border_style="red",
            box=box.DOUBLE
        )
        console.print(result_panel)

    game_state.challenges.remove(challenge)
    game_state.update_income()

    Prompt.ask("\nPress Enter to continue", default="")


def display_achievements(game_state: GameState):
    """Display achievements."""
    console.clear()

    header = Panel(
        Align.center("🏆  ACHIEVEMENTS  🏆"),
        style="bold yellow",
        border_style="yellow",
        box=box.DOUBLE
    )
    console.print(header)

    table = Table(box=box.ROUNDED, border_style="yellow")
    table.add_column("Status", justify="center", style="bold")
    table.add_column("Achievement", style="cyan")
    table.add_column("Description", style="white")

    for achievement in game_state.all_achievements:
        unlocked = achievement.name in game_state.achievements_unlocked
        status = f"[green]✓ {achievement.emoji}[/green]" if unlocked else "[dim]🔒[/dim]"
        name_style = "bold green" if unlocked else "dim"

        table.add_row(
            status,
            f"[{name_style}]{achievement.name}[/{name_style}]",
            achievement.description
        )

    console.print(table)

    progress = len(game_state.achievements_unlocked) / len(game_state.all_achievements) * 100
    console.print(f"\n[bold]Progress: {len(game_state.achievements_unlocked)}/{len(game_state.all_achievements)} ({progress:.1f}%)[/bold]")

    Prompt.ask("\nPress Enter to continue", default="")


def display_info(game_state: GameState):
    """Display educational info about Terraform and AWS."""
    console.clear()

    header = Panel(
        Align.center("📚  TERRAFORM & AWS GUIDE  📚"),
        style="bold blue",
        border_style="blue",
        box=box.DOUBLE
    )
    console.print(header)

    # Terraform intro
    terraform_panel = Panel(
        "[bold]What is Terraform?[/bold]\n\n"
        "Terraform is an Infrastructure as Code (IaC) tool that lets you define and provision "
        "infrastructure using declarative configuration files.\n\n"
        "[yellow]Key Benefits:[/yellow]\n"
        "  • [green]Version Control[/green] - Track infrastructure changes in Git\n"
        "  • [green]Reproducibility[/green] - Deploy identical environments\n"
        "  • [green]Automation[/green] - Reduce manual work and errors\n"
        "  • [green]Collaboration[/green] - Team-based infrastructure management\n"
        "  • [green]Multi-Cloud[/green] - Works with AWS, Azure, GCP, and more",
        title="[bold]🔧 Terraform Overview[/bold]",
        border_style="blue"
    )
    console.print(terraform_panel)

    # Assets table
    assets_table = Table(box=box.ROUNDED, border_style="cyan", title="AWS Services & Terraform Resources")
    assets_table.add_column("Service", style="cyan bold")
    assets_table.add_column("Terraform Resource", style="yellow")
    assets_table.add_column("Description", style="white")

    for asset in game_state.asset_types.values():
        assets_table.add_row(
            f"{asset.emoji} {asset.name}",
            asset.terraform_resource,
            asset.description
        )

    console.print("\n")
    console.print(assets_table)

    # Tips
    tips_panel = Panel(
        "[bold yellow]💡 Pro Tips:[/bold yellow]\n\n"
        "1. Always use remote state (S3 + DynamoDB) for team collaboration\n"
        "2. Use modules to create reusable infrastructure components\n"
        "3. Never commit secrets to version control - use AWS Secrets Manager\n"
        "4. Use terraform plan before apply to preview changes\n"
        "5. Tag all resources for better cost tracking and organization\n"
        "6. Implement proper IAM roles with least privilege principle",
        border_style="yellow"
    )
    console.print("\n")
    console.print(tips_panel)

    Prompt.ask("\nPress Enter to continue", default="")


def main():
    """Main game loop."""
    game_state = GameState()

    # Welcome screen
    console.clear()
    welcome = Panel(
        Align.center(
            "[bold cyan]Welcome to[/bold cyan]\n\n"
            "[bold yellow]☁️  AWS INFRASTRUCTURE TYCOON  ☁️[/bold yellow]\n\n"
            "[white]Build your cloud empire while learning AWS and Terraform!\n\n"
            "Features:\n"
            "  🖥️  Deploy real AWS services\n"
            "  📚  Learn through educational challenges\n"
            "  🏆  Unlock achievements\n"
            "  🎯  Test your DevOps knowledge\n\n"
            "Press Enter to begin your journey...[/white]"
        ),
        border_style="bright_blue",
        box=box.DOUBLE,
        padding=(1, 2)
    )
    console.print(welcome)
    Prompt.ask("", default="")

    last_time = time.time()
    last_display_update = time.time()

    try:
        while True:
            current_time = time.time()
            dt = current_time - game_state.last_income_update
            game_state.last_income_update = current_time

            # Update game state
            game_state.update_money(dt)

            # Gradual health decrease
            for asset_id in game_state.asset_health:
                if game_state.assets[asset_id] > 0:
                    decay = 0.02 * dt  # Slower decay
                    game_state.asset_health[asset_id] = max(20.0, game_state.asset_health[asset_id] - decay)

            game_state.update_income()

            # Try to generate challenge
            if not game_state.challenges:
                new_challenge = game_state.generate_challenge()
                if new_challenge:
                    game_state.challenges.append(new_challenge)

            # Update display every 2 seconds or when needed
            if current_time - last_display_update >= 2.0:
                display_dashboard(game_state)
                last_display_update = current_time
            else:
                display_dashboard(game_state)

            # Get command
            command = Prompt.ask(
                "[bold cyan]>>[/bold cyan]",
                choices=["p", "c", "a", "i", "q"],
                default="",
                show_choices=False
            ).lower()

            if command in ['q', 'quit']:
                if Confirm.ask("[yellow]Are you sure you want to quit?[/yellow]"):
                    break
            elif command == 'p':
                display_purchase_menu(game_state)
            elif command == 'c':
                display_challenge_menu(game_state)
            elif command == 'a':
                display_achievements(game_state)
            elif command == 'i':
                display_info(game_state)

            last_display_update = 0  # Force display update after menu

    except KeyboardInterrupt:
        pass

    # End screen
    console.clear()
    end_panel = Panel(
        Align.center(
            f"[bold yellow]Thanks for playing![/bold yellow]\n\n"
            f"[cyan]Final Stats:[/cyan]\n"
            f"  💰 Total Revenue: {format_number(game_state.total_revenue)}\n"
            f"  📈 Peak Income: {format_number(game_state.peak_income)}/s\n"
            f"  🎯 Challenges Solved: {game_state.challenges_solved}\n"
            f"  🏆 Achievements: {len(game_state.achievements_unlocked)}/{len(game_state.all_achievements)}\n"
            f"  🏗️  Total Assets: {game_state.total_assets_purchased}\n\n"
            f"[green]Keep learning AWS and Terraform! ☁️[/green]"
        ),
        border_style="bright_blue",
        box=box.DOUBLE,
        padding=(1, 2)
    )
    console.print(end_panel)


if __name__ == "__main__":
    main()
