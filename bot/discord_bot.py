import discord
from discord.ext import commands, tasks
import asyncio
import logging
from typing import Dict, List, Any
from datetime import datetime

from utils.config import Config
from database.manager import DatabaseManager
from monitors.monitor_manager import MonitorManager
from bot.commands import setup_commands
from bot.notifications import NotificationManager
from bot.daily_scheduler import DailyScanScheduler

class PokemonStockBot(commands.Bot):
    """Main Discord bot class for Pokemon stock monitoring"""
    
    def __init__(self, config: Config, db_manager: DatabaseManager):
        intents = discord.Intents.default()
        # Start with minimal intents - we'll add message_content later
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=commands.DefaultHelpCommand()
        )
        
        self.config = config
        self.db_manager = db_manager
        self.monitor_manager = MonitorManager(config, db_manager)
        self.notification_manager = NotificationManager(self, config)
        self.daily_scheduler = DailyScanScheduler(self)
        self.logger = logging.getLogger(__name__)
        
        # Setup commands
        setup_commands(self)
    
    async def setup_hook(self):
        """Initialize bot components"""
        self.logger.info("Setting up bot...")
        
        # Load slash commands
        try:
            await self.load_extension('bot.slash_commands')
            self.logger.info("Loaded slash commands")
        except Exception as e:
            self.logger.error("Failed to load slash commands: %s", e)
        
        # Start monitoring loops
        self.stock_monitor_loop.start()
        self.release_notification_loop.start()
        
        # Start daily scheduler
        asyncio.create_task(self.daily_scheduler.start_scheduler())
        
        # Sync commands for the specific guild
        if self.config.guild_id:
            guild = discord.Object(id=self.config.guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            self.logger.info("Synced commands to guild %s", self.config.guild_id)
    
    async def on_ready(self):
        """Event when bot is ready"""
        self.logger.info(f'{self.user} has connected to Discord!')
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="for Pokemon stock updates 📦"
            )
        )
        
        # Log guild information
        for guild in self.guilds:
            self.logger.info(f'Bot is in guild: {guild.name} (id: {guild.id})')
    
    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("❌ Unknown command. Use `!help` to see available commands.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: `{error.param.name}`")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"❌ Invalid argument: {error}")
        else:
            self.logger.error(f"Unexpected error: {error}")
            await ctx.send("❌ An unexpected error occurred.")
    
    @tasks.loop(seconds=300)  # Default 5 minutes, will be overridden by config
    async def stock_monitor_loop(self):
        """Main stock monitoring loop"""
        try:
            self.logger.info("Starting stock check...")
            
            # Get all monitored products
            products = await self.db_manager.get_all_products()
            
            if not products:
                self.logger.info("No products to monitor")
                return
            
            # Check stock for all products
            stock_changes = await self.monitor_manager.check_all_products(products)
            
            # Send notifications for changes
            if stock_changes:
                await self.notification_manager.send_stock_notifications(stock_changes)
            
            self.logger.info(f"Stock check completed. Found {len(stock_changes)} changes.")
            
        except Exception as e:
            self.logger.error(f"Error in stock monitor loop: {e}")
    
    @stock_monitor_loop.before_loop
    async def before_stock_monitor_loop(self):
        """Wait for bot to be ready before starting loop"""
        await self.wait_until_ready()
        
        # Update loop interval from config
        self.stock_monitor_loop.change_interval(seconds=self.config.check_interval)
        self.logger.info(f"Stock monitoring interval set to {self.config.check_interval} seconds")
    
    @tasks.loop(hours=12)
    async def release_notification_loop(self):
        """Check for upcoming releases and send notifications"""
        try:
            self.logger.info("Checking for release notifications...")
            
            # Check for advance notifications (7 days before release)
            advance_releases = await self.db_manager.get_releases_for_advance_notification(days_ahead=7)
            for release in advance_releases:
                await self.notification_manager.send_release_notification(release, "advance")
                await self.db_manager.mark_advance_notification_sent(release['id'])
                self.logger.info("Sent advance notification for %s", release['product_name'])
            
            # Check for release day notifications
            release_day_releases = await self.db_manager.get_releases_for_today()
            for release in release_day_releases:
                await self.notification_manager.send_release_notification(release, "release")
                await self.db_manager.mark_release_day_notification_sent(release['id'])
                self.logger.info("Sent release day notification for %s", release['product_name'])
            
        except Exception as e:
            self.logger.error("Error in release notification loop: %s", e)
    
    @release_notification_loop.before_loop
    async def before_release_notification_loop(self):
        """Wait for bot to be ready before starting release notification loop"""
        await self.wait_until_ready()
    
    async def close(self):
        """Cleanup when bot is shutting down"""
        self.logger.info("Shutting down bot...")
        
        # Cancel monitoring loops
        self.stock_monitor_loop.cancel()
        self.release_notification_loop.cancel()
        
        # Close database
        self.db_manager.close()
        
        # Close bot
        await super().close()
