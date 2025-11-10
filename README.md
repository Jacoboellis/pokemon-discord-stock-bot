# 🎯 Pokemon Discord Stock Bot - New Zealand Edition

A comprehensive Discord bot for monitoring Pokemon card/product stock from New Zealand online retailers. Features real-time monitoring, community reporting, and automated daily scans.

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
- **Automatic Scheduling**: Set up timed scans delivered to Discord channels
- **Real-time Monitoring**: Continuous background monitoring of tracked products

### 🏪 Supported New Zealand Stores
- ✅ **Nova Games NZ** - Fully working, perfect for monitoring
- 🔄 **The Warehouse NZ** - Accessible, ready for development  
- 🔄 **JB Hi-Fi NZ** - Accessible, ready for development
- 🔄 **Farmers NZ** - Accessible, ready for development
- ❌ **EB Games NZ** - Blocked (use community reporting)
- ❌ **Kmart NZ** - Blocked (use community reporting)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Discord Bot Token
- Required packages (see requirements.txt)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Jacoboellis/pokemon-discord-stock-bot.git
   cd pokemon-discord-stock-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the bot**
   - Edit `config.py` with your Discord bot token and channel IDs
   - Update channel IDs for your Discord server

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

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Adding Store Support
We welcome contributions for additional NZ Pokemon stores! Please:
- Test the store with the generic monitor
- Add proper configuration
- Update documentation
- Submit examples of working products

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ for the New Zealand Pokemon community** 🇳🇿

*Perfect for tracking those elusive Pokemon card restocks across New Zealand!*
