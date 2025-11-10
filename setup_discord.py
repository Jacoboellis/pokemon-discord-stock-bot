#!/usr/bin/env python3
"""
Setup script for Pokemon Stock Discord Bot
This script helps you configure the bot for your specific Discord server.
"""

import os
import discord
from discord.ext import commands
import asyncio

# Your Discord bot token (set this in your .env file)
BOT_TOKEN = os.getenv('DISCORD_TOKEN', 'your_token_here')

async def setup_bot_channels():
    """Interactive setup to configure channels for your Discord server"""
    
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    
    bot = commands.Bot(command_prefix='!setup_', intents=intents)
    
    @bot.event
    async def on_ready():
        print(f'\n🤖 Bot connected as {bot.user}')
        print(f'📋 Found {len(bot.guilds)} servers')
        
        for guild in bot.guilds:
            print(f'\n🏰 Server: {guild.name} (ID: {guild.id})')
            print('📁 Categories and Channels:')
            
            # Group channels by category
            categories = {}
            
            for channel in guild.channels:
                if isinstance(channel, discord.CategoryChannel):
                    categories[channel.name] = {
                        'id': channel.id,
                        'channels': []
                    }
            
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel):
                    category_name = channel.category.name if channel.category else 'No Category'
                    if category_name not in categories:
                        categories[category_name] = {'channels': []}
                    
                    categories[category_name]['channels'].append({
                        'name': channel.name,
                        'id': channel.id,
                        'mention': channel.mention
                    })
            
            # Print organized channel list
            for category_name, category_data in categories.items():
                print(f'\n  📂 {category_name}:')
                for channel in category_data.get('channels', []):
                    print(f'    #{channel["name"]} (ID: {channel["id"]})')
        
        # Generate configuration template
        print('\n' + '='*60)
        print('📝 CONFIGURATION TEMPLATE')
        print('='*60)
        print('Copy the following to your .env file and update the channel IDs:')
        print()
        
        print('# Discord Configuration')
        if bot.guilds:
            print(f'GUILD_ID={bot.guilds[0].id}')
        
        print('\n# Channel IDs (Update these with your actual channel IDs)')
        channel_mapping = {
            'OFFICIAL_RESTOCKS_CHANNEL': 'official-restocks',
            'VERIFIED_SIGHTINGS_CHANNEL': 'verified-sightings', 
            'COMMUNITY_SIGHTINGS_CHANNEL': 'community-sightings',
            'BOT_LOGS_CHANNEL': 'bot-logs',
            'SUBMIT_SIGHTING_CHANNEL': 'submit-sighting',
        }
        
        for env_var, channel_name in channel_mapping.items():
            found_channel = None
            for guild in bot.guilds:
                for channel in guild.channels:
                    if isinstance(channel, discord.TextChannel) and channel_name in channel.name.lower():
                        found_channel = channel
                        break
            
            if found_channel:
                print(f'{env_var}={found_channel.id}  # #{found_channel.name}')
            else:
                print(f'{env_var}=YOUR_CHANNEL_ID_HERE  # #{channel_name}')
        
        print('\n' + '='*60)
        print('🚀 Setup complete! Update your .env file with the above values.')
        print('='*60)
        
        await bot.close()
    
    try:
        await bot.start(BOT_TOKEN)
    except discord.LoginFailure:
        print('❌ Invalid bot token. Please check your DISCORD_TOKEN in .env file.')
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == '__main__':
    if not BOT_TOKEN or BOT_TOKEN == 'your_token_here':
        print('❌ Please set your DISCORD_TOKEN in the .env file first!')
        print('1. Copy .env.example to .env')
        print('2. Replace "your_discord_bot_token_here" with your actual bot token')
        print('3. Run this setup script again')
    else:
        print('🔧 Starting Discord server setup...')
        print('This will help you configure channel IDs for your bot.')
        asyncio.run(setup_bot_channels())
