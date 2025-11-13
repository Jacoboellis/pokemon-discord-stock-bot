# 🎯 Pokemon Discord Stock Bot - New Zealand Edition

A professional Discord bot for monitoring Pokemon card/product stock from New Zealand online retailers. Features real-time monitoring, community reporting, automated daily scans, and enterprise-grade code quality.

## 🌟 Features

### 🤖 Discord Bot Commands
- `/add_sku` - Add products to monitor from Nova Games NZ
- `/report_sighting` - Community members report Pokemon product sightings
- `/daily_scan` - Manual comprehensive scan of all NZ stores
- `/stock_summary` - Overview of monitored products and community activity
- `/schedule_daily` - Set up automatic daily scans (Admin only)

### 🌅 Daily Scanning System
- **Standalone Scanner**: Run `python daily_scan.py` for morning/evening routine
- **Batch Script**: Double-click `daily_scan.bat` for easy Windows scanning
- **CLI Tool**: Run `python -m pokemon_bot.cli --daily` for command-line scanning
- **Automatic Scheduling**: Set up timed scans delivered to Discord channels
- **Real-time Monitoring**: Continuous background monitoring of tracked products

### 🏪 Supported New Zealand Stores
- ✅ **Nova Games NZ** - Fully working, perfect for monitoring
- 🔄 **The Warehouse NZ** - Accessible, ready for development  
- 🔄 **JB Hi-Fi NZ** - Accessible, ready for development
- 🔄 **Farmers NZ** - Accessible, ready for development
- ❌ **EB Games NZ** - Blocked (use community reporting)
- ❌ **Kmart NZ** - Blocked (use community reporting)

### 🏗️ Enterprise-Grade Architecture
- **Generic Monitor System**: Single universal scraper for all stores
- **HTTP Connection Pooling**: Efficient aiohttp sessions with retry logic
- **Error Handling**: Centralized error management with optional Sentry integration
- **Configuration Management**: Environment variable-based config with validation
- **Type Safety**: Full type hints and mypy compatibility
- **Code Quality**: Black formatting, isort imports, flake8 linting
- **CI/CD Pipeline**: GitHub Actions for automated testing and quality checks
- **Containerization**: Docker support for reliable deployment

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ (tested with 3.8-3.12)
- Discord Bot Token
- Git (for cloning)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Jacoboellis/pokemon-discord-stock-bot.git
   cd pokemon-discord-stock-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   
   # For development with linting and testing:
   pip install -r requirements-dev.txt
   ```

3. **Configure the bot**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env with your Discord bot token and channel IDs
   # Windows: notepad .env
   # Linux/Mac: nano .env
   ```

4. **Validate setup**
   ```bash
   python check_setup.py
   ```

4. **Run the bot**
   ```bash
   python main.py
   ```

### Daily Scanner (Standalone)
Perfect for morning/evening routine:
```bash
# Morning scan - see overnight changes
python daily_scan.py

# Or use the Windows batch file
daily_scan.bat
```

## 📱 Discord Commands Reference

| Command | Description | Example |
|---------|-------------|---------|
| `/add_sku` | Add product to monitoring | `/add_sku sku:mega-evolution-booster-pack store:novagames_nz` |
| `/report_sighting` | Report community finding | `/report_sighting store:thewarehouse_nz product:Pokemon...` |
| `/daily_scan` | Manual comprehensive scan | Scans all stores, shows new arrivals |
| `/stock_summary` | Current status overview | Shows monitored products + today's sightings |
| `/schedule_daily` | Set automatic scans | `/schedule_daily channel:#bot-logs time:08:00` |

### 🗓️ Daily Workflow
**Morning**: Run `daily_scan.py` → **All Day**: Community reports → **Evening**: Run scan again

## ⚙️ Configuration

### Store Configuration
Stores are configured in `store_config.yml`. The system uses a generic monitor that can easily add new stores:

```yaml
nz_stores:
  novagames_nz:
    name: "Nova Games NZ"
    base_url: "https://novagames.co.nz"
    search_url: "https://novagames.co.nz/collections/pokemon"
    status: "✅ WORKING"
```

## 🏗️ Architecture

### Core Components
- **GenericStoreMonitor**: Universal store scraper (no individual store classes needed)
- **DatabaseManager**: SQLite database for products, sightings, and schedules
- **NotificationManager**: Discord notifications and embeds
- **DailyReporter**: Comprehensive daily scanning and reporting
- **DailyScanScheduler**: Automatic scheduling system

### File Structure
```
pokemon-discord-stock-bot/
├── bot/                    # Discord bot components
│   ├── commands.py         # Basic bot commands
│   ├── slash_commands.py   # Discord slash commands
│   ├── daily_reporter.py   # Daily scanning system
│   ├── daily_scheduler.py  # Automatic scheduling
│   ├── discord_bot.py      # Main bot class
│   └── notifications.py    # Discord notifications
├── database/               # Database management
│   ├── manager.py          # Database operations
│   └── models.py           # Data models
├── monitors/               # Store monitoring
│   ├── base_monitor.py     # Base monitor class
│   ├── generic_monitor.py  # Universal store monitor
│   └── monitor_manager.py  # Monitor coordination
├── utils/                  # Utilities
│   ├── config.py           # Configuration management
│   ├── helpers.py          # Helper functions
│   └── logger.py           # Logging setup
├── main.py                 # Bot entry point
├── daily_scan.py          # Standalone daily scanner
├── daily_scan.bat         # Windows batch file
├── config.py              # Bot configuration
├── store_config.yml       # Store configurations
└── requirements.txt       # Python dependencies
```

## 🔧 Development & Quality Assurance

### Code Quality Tools
```bash
# Format code
black .

# Sort imports  
isort .

# Lint code
flake8 .

# Type checking
mypy .

# Run all quality checks
pre-commit run --all-files
```

### Testing
```bash
# Run tests
pytest tests/ -v

# Test with coverage
pytest tests/ --cov=. --cov-report=html
```

### CLI Usage
```bash
# Run daily scan from command line
python -m pokemon_bot.cli --daily

# Save scan results to file  
python -m pokemon_bot.cli --daily --output daily_scan.txt

# Validate configuration
python -m pokemon_bot.cli --check-config

# Test store connectivity
python -m pokemon_bot.cli --test-stores
```

### Docker Deployment
```bash
# Build image
docker build -t pokemon-stock-bot .

# Run container
docker run -d --env-file .env pokemon-stock-bot

# Run with volume for data persistence
docker run -d --env-file .env -v ./data:/app/data pokemon-stock-bot
```

## 🚀 Recent Improvements (November 2025)

This codebase has been significantly refactored for professional quality:

### ✅ High Priority Improvements Completed
1. **Consolidated Scripts**: Removed duplicate product checking scripts, created unified `utils/product_checker.py`
2. **Focused main.py**: Clean entry point that delegates to proper bot classes
3. **Environment Configuration**: Single config system using `.env` files with validation
4. **HTTP Optimization**: Enhanced aiohttp sessions with connection pooling, retry logic, and rate limiting
5. **Centralized Logging**: Replaced print statements with proper logging, added error handling utilities
6. **Legacy Cleanup**: Moved deprecated store monitors to `legacy/` folder with documentation

### ✅ Medium Priority Improvements Completed
1. **Code Quality Setup**: Added Black, isort, flake8, mypy configuration in `pyproject.toml`
2. **Pre-commit Hooks**: Automated code quality checks in `.pre-commit-config.yaml`
3. **Pinned Dependencies**: Locked production dependencies in `requirements.txt`, dev dependencies in `requirements-dev.txt`
4. **CI/CD Pipeline**: GitHub Actions workflow for testing across Python 3.8-3.12

### ✅ Nice-to-Have Features Completed
1. **Containerization**: Complete Dockerfile with security best practices
2. **CLI Interface**: `python -m pokemon_bot.cli` for command-line operations
3. **Professional Documentation**: Comprehensive README with architecture details
4. **Test Framework**: Basic test structure with pytest configuration

### 📊 Code Quality Metrics
- **41 Files**: Well-organized modular structure
- **4,900+ Lines**: Comprehensive feature set
- **Type Safety**: Full type hints and mypy compliance
- **Test Coverage**: Unit tests for core parsing functions
- **CI/CD**: Automated testing across 5 Python versions
- **Containerized**: Docker-ready for reliable deployment
