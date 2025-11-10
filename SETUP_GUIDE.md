# 🎯 Pokemon Stock Discord Bot - Quick Start Guide

Welcome to your Pokemon Stock Discord Bot! This bot is specifically designed for your Discord server structure.

## 📋 Server Structure Configured

Your bot is set up to work with these channels:

### 📁 Welcome Category
- **#welcome** - Automatic welcome messages
- **#roles** - Role selection

### 📁 Information Category
- **#announcements** - Official announcements
- **#how-to-report** - Instructions for reporting sightings

### 📁 Drops Category (Main Bot Functions)
- **#official-restocks** 🤖 - Automated website stock alerts (PRIMARY)
- **#verified-sightings** ✅ - Mod-verified community reports
- **#community-sightings** 👀 - Unverified community reports

### 📁 Community Category
- **#general-chat** - General discussion
- **#showcase** - Collection showcases
- **#trades** - Trading discussions
- **#store-discussion** - Store-specific talks
- **#submit-sighting** - Submit reports for verification

### 📁 Mods Category
- **#mod-chat** - Moderator discussions
- **#bot-logs** 📊 - Bot activity logs (SECONDARY)

## 🚀 Setup Steps

### 1. Create Your Bot Token
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section
4. Create a bot and copy the token
5. Enable "Message Content Intent" under Privileged Gateway Intents

### 2. Configure Environment
1. Copy `.env.example` to `.env`
2. Add your bot token: `DISCORD_TOKEN=your_actual_token_here`
3. Add your server ID: `GUILD_ID=your_server_id_here`

### 3. Get Channel IDs
Run the setup script to automatically detect your channels:
```bash
python setup_discord.py
```

Or manually get channel IDs:
1. Enable Developer Mode in Discord (User Settings > Advanced)
2. Right-click each channel → Copy ID
3. Add to your `.env` file

### 4. Install Dependencies & Run
```bash
pip install -r requirements.txt
python main.py
```

## 🎮 Bot Commands

### Stock Management Commands
- `!add_sku SKU123 pokemon_center [Product Name]` - Monitor a Pokemon product
- `!remove_sku SKU123` - Stop monitoring a product
- `!list_skus` - Show all monitored products
- `!check_now` - Force immediate stock check

### Admin Commands (Mods Only)
- `!set_interval 300` - Change check frequency (seconds)
- `!bot_info` - Show bot statistics

## 🏪 Supported Stores

### Currently Active:
- **Pokemon Center** (Primary focus)
- **Best Buy** (Pokemon products)

### Planned:
- TCGPlayer
- GameStop
- Target

## 🔧 Channel Functions

### #official-restocks
- Automated alerts when monitored products come in stock
- High-priority notifications with role mentions
- Direct links to purchase

### #verified-sightings
- Community reports verified by moderators
- Include photos, timestamps, locations
- Trusted information source

### #community-sightings
- Immediate community reports
- Unverified but quick information
- Good for breaking news

### #submit-sighting
- Template for submitting sightings
- Requires: Photo, Store, Location, Timestamp
- Mods review and promote to verified

### #bot-logs
- All bot activity tracking
- Error reports and status updates
- Performance monitoring

## 🎯 Usage Examples

### Adding Pokemon Products to Monitor:
```
!add_sku 290-85506 pokemon_center Pokemon TCG: Scarlet & Violet Booster Box
!add_sku 875983 bestbuy Charizard Figure
```

### Community Sighting Format:
```
📍 **Store:** Target - Downtown Seattle
🕐 **Time:** 2:30 PM PST
📦 **Product:** Pokemon Booster Boxes
💰 **Price:** $89.99
📸 **Photo:** [Attach image]
```

## 🛡️ Permissions Needed

The bot needs these permissions in your Discord server:
- Read Messages
- Send Messages
- Embed Links
- Attach Files
- Read Message History
- Use External Emojis
- Mention @everyone, @here, and All Roles

## 🆘 Support

If you need help:
1. Check the logs in #bot-logs
2. Use `!bot_info` to see current status
3. Restart with `python main.py` if needed

## 🎉 You're Ready!

Your Pokemon Stock Discord Bot is configured and ready to help your community track Pokemon product availability across multiple stores. The bot will automatically post to #official-restocks when monitored items come in stock, and your community can use the other channels for verified and community sightings.

Happy hunting! 🎯
