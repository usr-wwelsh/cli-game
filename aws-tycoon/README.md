# AWS Infrastructure Tycoon

A beautiful, educational CLI game that teaches AWS and Terraform concepts through gameplay!

## Features

### Visual Enhancements
- **Rich Terminal UI** - Colorful panels, tables, and progress bars
- **Health Bars** - Visual indicators for infrastructure health
- **Color-Coded Stats** - Green for good, yellow for warning, red for critical
- **Beautiful Menus** - Styled panels with emojis and borders
- **Achievement Popups** - Celebratory notifications when unlocking achievements

### Gameplay
- **7 AWS Services** - EC2, S3, Load Balancers, RDS, Lambda, VPC, CloudFront
- **Incremental Progression** - Start small, scale up your cloud empire
- **Health System** - Maintain your infrastructure or face consequences
- **Income Generation** - Earn money passively from your assets

### Educational Challenges
- **45+ Real-World Scenarios** - Based on actual AWS/DevOps practices
- **4 Categories**:
  - 🔒 Security - IAM, encryption, security groups, DDoS protection
  - ⚡ Performance - Auto-scaling, CDN, database optimization
  - 💰 Cost Optimization - Spot instances, reserved instances, savings plans
  - 🏗️ Architecture - High availability, load balancing, disaster recovery
- **3 Difficulty Levels** - Easy, Medium, Hard
- **Detailed Explanations** - Learn from both correct and incorrect answers
- **Streak System** - Build momentum by answering correctly
- **Rewards** - Restore health and earn bonus cash for correct answers

### Achievement System
- 🎉 First Purchase
- 🌱 Cloud Novice (5 assets)
- 💼 Infrastructure Pro (25 assets)
- 🏗️ Cloud Architect (100 assets)
- 🧠 Quiz Master (10 challenges solved)
- ⭐ Perfect Score (5 streak)
- 💰 Money Maker ($10K income/sec)
- 👑 Cloud Tycoon ($100K revenue)
- 🎯 Diversified (own all asset types)

## How to Play

### Installation
```bash
pip install rich
```

### Run the Game
```bash
python main.py
```

### Controls
- **[P]urchase** - Buy new infrastructure assets
- **[C]hallenges** - Answer educational questions
- **[A]chievements** - View your progress
- **[I]nfo** - Learn about Terraform and AWS
- **[Q]uit** - Exit the game

### Strategy Tips
1. Start with EC2 instances and S3 for basic income
2. Answer challenges to restore asset health and earn bonuses
3. Upgrade to higher-tier assets (Lambda, VPC, CloudFront) for better returns
4. Build a streak by answering challenges correctly
5. Aim for the "Diversified" achievement to unlock all asset types

## Adding Your Own Challenges

The game loads challenges from `challenges.json`, making it easy to add hundreds more!

### Challenge Structure
```json
{
  "name": "🔒 Your Challenge Name",
  "description": "Brief description of the scenario",
  "question": "The question to ask the player?",
  "options": [
    "Option 1 (incorrect)",
    "Option 2 (correct)",
    "Option 3 (incorrect)",
    "Option 4 (incorrect)"
  ],
  "correct_answer": 1,
  "explanation": "Why option 2 is correct and what the player should learn",
  "difficulty": "easy",
  "category": "security"
}
```

### Categories
- `security` - Security best practices, IAM, encryption
- `performance` - Optimization, scaling, caching
- `cost` - Cost optimization strategies
- `architecture` - System design, high availability

### Difficulty Levels
- `easy` - Beginner-friendly concepts
- `medium` - Intermediate knowledge required
- `hard` - Advanced topics

### Steps to Add Challenges
1. Open `challenges.json`
2. Add your challenge object to the `challenges` array
3. Make sure `correct_answer` is the index (0-3) of the correct option
4. Save and restart the game!

## Game Balance

- Starting Cash: $100
- Challenge Frequency: Every 45 seconds (15% chance when eligible)
- Health Decay: 0.02% per second per asset
- Correct Answer Reward: +25% health + 10 seconds of income
- Incorrect Answer Penalty: -30% health, streak reset

## Terraform Resources

Each asset corresponds to a real Terraform resource:
- EC2 Instances → `aws_instance`
- S3 Storage → `aws_s3_bucket`
- Load Balancers → `aws_lb`
- RDS Databases → `aws_db_instance`
- Lambda Functions → `aws_lambda_function`
- VPC Networks → `aws_vpc`
- CloudFront CDN → `aws_cloudfront_distribution`

## Learning Resources

The game teaches real AWS concepts! Here are some topics covered:
- Security Groups and least privilege principle
- IAM best practices and MFA
- S3 encryption and bucket policies
- RDS Read Replicas and Multi-AZ
- CloudFront edge locations and CDN
- Auto Scaling for variable traffic
- Spot Instances vs Reserved Instances
- High Availability across Availability Zones
- Load Balancer types (ALB vs NLB)
- Container orchestration with ECS/EKS
- Terraform state management
- DDoS protection with AWS Shield
- CloudWatch vs CloudTrail
- Disaster Recovery (RTO vs RPO)
- And many more!

## Credits

Built with:
- Python 3
- [Rich](https://github.com/Textualize/rich) - Beautiful terminal formatting

## Contributing

Feel free to add more challenges to `challenges.json`! The more educational content, the better!

---

**Have fun building your cloud empire while learning AWS and Terraform! ☁️**
