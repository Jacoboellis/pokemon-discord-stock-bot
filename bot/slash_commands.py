import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import logging

from utils.helpers import clean_sku

class SlashCommands(commands.Cog):
    """Slash command implementations for the Pokemon Stock Bot"""
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
    
    @app_commands.command(name="add_sku", description="Add a SKU to monitor for stock changes")
    @app_commands.describe(
        sku="The SKU/product code to monitor",
        store="The store name",
        product_name="Optional product name"
    )
    @app_commands.choices(store=[
        app_commands.Choice(name="Nova Games NZ", value="novagames_nz"),
        app_commands.Choice(name="EB Games NZ", value="ebgames_nz"),
        app_commands.Choice(name="The Warehouse NZ", value="thewarehouse_nz"),
        app_commands.Choice(name="JB Hi-Fi NZ", value="jbhifi_nz"),
        app_commands.Choice(name="Kmart NZ", value="kmart_nz"),
        app_commands.Choice(name="Farmers NZ", value="farmers_nz"),
    ])
    async def add_sku_slash(
        self, 
        interaction: discord.Interaction, 
        sku: str, 
        store: app_commands.Choice[str], 
        product_name: Optional[str] = None
    ):
        """Add a SKU to monitor via slash command"""
        await interaction.response.defer()
        
        try:
            clean_sku_value = clean_sku(sku)
            
            success = await self.bot.db_manager.add_product(
                sku=clean_sku_value,
                store_name=store.value,
                product_name=product_name
            )
            
            if success:
                embed = discord.Embed(
                    title="✅ SKU Added",
                    description=f"Now monitoring **{clean_sku_value}** from **{store.name}**",
                    color=0x00ff00
                )
                if product_name:
                    embed.add_field(name="Product", value=product_name, inline=False)
                
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send("❌ Failed to add SKU. It may already exist.")
                
        except Exception as e:
            self.logger.error(f"Error in add_sku slash command: {e}")
            await interaction.followup.send("❌ An error occurred while adding the SKU.")
    
    @app_commands.command(name="list_skus", description="List all monitored SKUs")
    async def list_skus_slash(self, interaction: discord.Interaction):
        """List all monitored SKUs via slash command"""
        await interaction.response.defer()
        
        try:
            products = await self.bot.db_manager.get_all_products()
            
            if not products:
                await interaction.followup.send("📭 No SKUs are currently being monitored.")
                return
            
            embed = discord.Embed(
                title="📋 Monitored SKUs",
                description=f"Currently monitoring {len(products)} products",
                color=self.bot.config.embed_color
            )
            
            # Group by store
            stores = {}
            for product in products:
                store = product['store_name']
                if store not in stores:
                    stores[store] = []
                stores[store].append(product)
            
            for store, store_products in stores.items():
                product_list = []
                for product in store_products[:10]:  # Limit to 10 per store
                    status_emoji = "🟢" if product['current_stock_status'] == 'In Stock' else "🔴"
                    product_info = f"{status_emoji} {product['sku']}"
                    if product['product_name']:
                        product_info += f" - {product['product_name'][:30]}..."
                    product_list.append(product_info)
                
                if len(store_products) > 10:
                    product_list.append(f"... and {len(store_products) - 10} more")
                
                embed.add_field(
                    name=f"🏪 {store.title()}",
                    value="\n".join(product_list) if product_list else "None",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in list_skus slash command: {e}")
            await interaction.followup.send("❌ An error occurred while fetching SKUs.")
    
    @app_commands.command(name="info", description="Display bot information and statistics")
    async def info_slash(self, interaction: discord.Interaction):
        """Display bot information via slash command"""
        await interaction.response.defer()
        
        try:
            products = await self.bot.db_manager.get_all_products()
            
            embed = discord.Embed(
                title="🤖 Pokemon Stock Bot Info",
                description="Real-time Pokemon product stock monitoring",
                color=self.bot.config.embed_color
            )
            
            embed.add_field(name="Monitored Products", value=len(products), inline=True)
            embed.add_field(name="Check Interval", value=f"{self.bot.config.check_interval}s", inline=True)
            embed.add_field(name="Supported Stores", value="Pokemon Center\nBest Buy\n(More coming soon)", inline=True)
            
            embed.add_field(
                name="Available Commands",
                value="Use `/` slash commands or `!` prefix commands",
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in info slash command: {e}")
            await interaction.followup.send("❌ An error occurred while fetching bot info.")
    
    @app_commands.command(name="add_release", description="Add an upcoming Pokemon release")
    @app_commands.describe(
        product_name="Name of the Pokemon product",
        release_date="Release date (YYYY-MM-DD format)",
        estimated_price="Estimated price (optional)",
        store_name="Store name (optional)",
        description="Product description (optional)"
    )
    async def add_release(
        self, 
        interaction: discord.Interaction, 
        product_name: str, 
        release_date: str,
        estimated_price: Optional[float] = None,
        store_name: Optional[str] = None,
        description: Optional[str] = None
    ):
        """Add upcoming release via slash command"""
        await interaction.response.defer()
        
        try:
            success = await self.bot.db_manager.add_upcoming_release(
                product_name=product_name,
                release_date=release_date,
                estimated_price=estimated_price,
                store_name=store_name,
                description=description
            )
            
            if success:
                embed = discord.Embed(
                    title="✅ Upcoming Release Added",
                    description=f"**{product_name}** scheduled for {release_date}",
                    color=0x00ff00
                )
                if estimated_price:
                    embed.add_field(name="💰 Estimated Price", value=f"${estimated_price:.2f}", inline=True)
                if store_name:
                    embed.add_field(name="🏪 Store", value=store_name, inline=True)
                if description:
                    embed.add_field(name="📝 Description", value=description, inline=False)
                
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send("❌ Failed to add upcoming release.")
                
        except Exception as e:
            self.logger.error(f"Error in add_release command: {e}")
            await interaction.followup.send("❌ An error occurred while adding the release.")
    
    @app_commands.command(name="report_sighting", description="Report Pokemon stock seen in the wild")
    @app_commands.describe(
        product_name="Name of the Pokemon product you found",
        store_name="Name of the store",
        location="Store location (city, address, etc.)",
        stock_count="How many items were available",
        price="Price you saw (optional)",
    )
    @app_commands.choices(store_name=[
        app_commands.Choice(name="Nova Games NZ", value="Nova Games NZ"),
        app_commands.Choice(name="EB Games NZ", value="EB Games NZ"),
        app_commands.Choice(name="The Warehouse NZ", value="The Warehouse NZ"),
        app_commands.Choice(name="JB Hi-Fi NZ", value="JB Hi-Fi NZ"),
        app_commands.Choice(name="Kmart NZ", value="Kmart NZ"),
        app_commands.Choice(name="Farmers NZ", value="Farmers NZ"),
        app_commands.Choice(name="Other NZ Store", value="Other"),
    ])
    async def report_sighting(
        self, 
        interaction: discord.Interaction, 
        product_name: str, 
        store_name: app_commands.Choice[str],
        location: str,
        stock_count: str,
        price: Optional[float] = None
    ):
        """Report community sighting via slash command"""
        await interaction.response.defer()
        
        try:
            sighting_id = await self.bot.db_manager.add_community_sighting(
                user_id=str(interaction.user.id),
                user_name=interaction.user.display_name,
                product_name=product_name,
                store_name=store_name.value,
                location=location,
                stock_count=stock_count,
                price=price
            )
            
            if sighting_id > 0:
                # Create embed for community sightings channel
                embed = discord.Embed(
                    title="👀 New Community Sighting",
                    description=f"**{product_name}** spotted at **{store_name.value}**",
                    color=0x3498db
                )
                embed.add_field(name="📍 Location", value=location, inline=True)
                embed.add_field(name="📦 Stock Count", value=stock_count, inline=True)
                if price:
                    embed.add_field(name="💰 Price", value=f"${price:.2f}", inline=True)
                embed.add_field(name="👤 Reported by", value=interaction.user.mention, inline=False)
                embed.set_footer(text=f"Sighting ID: {sighting_id}")
                
                # Send to community sightings channel
                community_channel_id = self.bot.config.community_sightings_channel
                if community_channel_id and community_channel_id != "your_community_sightings_channel_id":
                    channel = self.bot.get_channel(int(community_channel_id))
                    if channel:
                        await channel.send(embed=embed)
                
                await interaction.followup.send("✅ Your sighting has been reported! Thank you for helping the community!")
            else:
                await interaction.followup.send("❌ Failed to report sighting.")
                
        except Exception as e:
            self.logger.error(f"Error in report_sighting command: {e}")
            await interaction.followup.send("❌ An error occurred while reporting the sighting.")
    
    @app_commands.command(name="verify_sighting", description="Verify a community sighting (Mods only)")
    @app_commands.describe(
        sighting_id="ID of the sighting to verify",
        notes="Verification notes (optional)"
    )
    @app_commands.default_permissions(manage_messages=True)
    async def verify_sighting(
        self, 
        interaction: discord.Interaction, 
        sighting_id: int,
        notes: Optional[str] = None
    ):
        """Verify community sighting via slash command (Mods only)"""
        await interaction.response.defer()
        
        try:
            success = await self.bot.db_manager.verify_sighting(
                sighting_id=sighting_id,
                verified_by=interaction.user.display_name,
                notes=notes
            )
            
            if success:
                # Create verified sighting embed
                embed = discord.Embed(
                    title="✅ VERIFIED SIGHTING",
                    description=f"Sighting #{sighting_id} has been verified!",
                    color=0x00ff00
                )
                embed.add_field(name="✅ Verified by", value=interaction.user.mention, inline=True)
                if notes:
                    embed.add_field(name="📝 Notes", value=notes, inline=False)
                
                # Send to verified sightings channel
                verified_channel_id = self.bot.config.verified_sightings_channel
                if verified_channel_id and verified_channel_id != "your_verified_sightings_channel_id":
                    channel = self.bot.get_channel(int(verified_channel_id))
                    if channel:
                        await channel.send(embed=embed)
                
                await interaction.followup.send(f"✅ Sighting #{sighting_id} has been verified!")
            else:
                await interaction.followup.send("❌ Failed to verify sighting or sighting not found.")
                
        except Exception as e:
            self.logger.error(f"Error in verify_sighting command: {e}")
            await interaction.followup.send("❌ An error occurred while verifying the sighting.")
    
    @app_commands.command(name="pending_sightings", description="View unverified community sightings (Mods only)")
    @app_commands.default_permissions(manage_messages=True)
    async def pending_sightings(self, interaction: discord.Interaction):
        """View pending sightings via slash command (Mods only)"""
        await interaction.response.defer()
        
        try:
            sightings = await self.bot.db_manager.get_unverified_sightings()
            
            if not sightings:
                await interaction.followup.send("📭 No pending sightings to verify.")
                return
            
            embed = discord.Embed(
                title="⏳ Pending Sightings for Verification",
                description=f"{len(sightings)} sightings awaiting verification",
                color=0xff9900
            )
            
            for sighting in sightings[:10]:  # Limit to 10
                embed.add_field(
                    name=f"ID: {sighting['id']} - {sighting['product_name']}",
                    value=f"**Store:** {sighting['store_name']}\n**Location:** {sighting['location']}\n**Reported by:** {sighting['user_name']}",
                    inline=True
                )
            
            if len(sightings) > 10:
                embed.add_field(
                    name="More sightings...",
                    value=f"And {len(sightings) - 10} more pending verification",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in pending_sightings command: {e}")
            await interaction.followup.send("❌ An error occurred while fetching pending sightings.")
    
    @app_commands.command(name="daily_scan", description="Perform a comprehensive daily scan of all NZ Pokemon stores")
    @app_commands.describe(
        send_report="Whether to send the report to a channel (default: current channel)"
    )
    async def daily_scan_slash(
        self, 
        interaction: discord.Interaction,
        send_report: Optional[bool] = True
    ):
        """Slash command to perform daily stock scan"""
        await interaction.response.defer(thinking=True)
        
        try:
            # Import here to avoid circular imports
            from bot.daily_reporter import DailyStockReporter
            
            reporter = DailyStockReporter(self.bot)
            
            # Perform the scan
            report_channel_id = interaction.channel.id if send_report else None
            scan_results = await reporter.perform_daily_scan(report_channel_id)
            
            # Send immediate response
            total_products = len(scan_results['products_found'])
            new_arrivals = len(scan_results['new_arrivals'])
            stores_scanned = len(scan_results['stores_scanned'])
            
            embed = discord.Embed(
                title="🔍 Daily Scan Complete",
                description=f"Scanned **{stores_scanned}** NZ stores",
                color=0x2ecc71
            )
            
            embed.add_field(
                name="📊 Results",
                value=f"**{total_products}** products found\n**{new_arrivals}** new arrivals",
                inline=True
            )
            
            if scan_results['errors']:
                embed.add_field(
                    name="⚠️ Issues",
                    value=f"{len(scan_results['errors'])} stores had errors",
                    inline=True
                )
            
            embed.set_footer(text="📋 Detailed report sent above (if enabled)")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in daily_scan command: {e}")
            await interaction.followup.send("❌ An error occurred during the daily scan.")
    
    @app_commands.command(name="stock_summary", description="Get a summary of current monitored products and today's sightings")
    async def stock_summary_slash(self, interaction: discord.Interaction):
        """Slash command to get stock summary"""
        await interaction.response.defer()
        
        try:
            # Import here to avoid circular imports
            from bot.daily_reporter import DailyStockReporter
            
            reporter = DailyStockReporter(self.bot)
            summary = await reporter.get_stock_summary()
            
            embed = discord.Embed(
                title="📊 Current Stock Summary",
                description=f"Overview of monitored products and community activity",
                color=0x3498db
            )
            
            # Monitored products
            monitored_count = summary.get('total_monitored', 0)
            embed.add_field(
                name="🎯 Monitored Products",
                value=f"**{monitored_count}** products being tracked",
                inline=True
            )
            
            # Community sightings
            sightings_count = summary.get('todays_sightings', 0)
            embed.add_field(
                name="👥 Today's Sightings",
                value=f"**{sightings_count}** community reports",
                inline=True
            )
            
            # Recent activity
            if summary.get('community_sightings'):
                recent_sightings = []
                for sighting in summary['community_sightings'][:3]:
                    store, product, price, reporter, reported_at = sighting
                    price_text = f"${price:.2f}" if price else "No price"
                    recent_sightings.append(f"• **{product}** - {price_text}\n  📍 {store} (by {reporter})")
                
                embed.add_field(
                    name="🆕 Recent Community Reports",
                    value="\n".join(recent_sightings) if recent_sightings else "No reports today",
                    inline=False
                )
            
            embed.set_footer(text="💡 Use /daily_scan for fresh store scan • /report_sighting to add new findings")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in stock_summary command: {e}")
            await interaction.followup.send("❌ An error occurred while getting stock summary.")
    
    @app_commands.command(name="schedule_daily", description="Set up automatic daily scans (Admin only)")
    @app_commands.describe(
        channel="Channel to send daily reports to",
        time="Time for daily scans (24h format, e.g., '08:00' or '20:30')"
    )
    async def schedule_daily_slash(
        self, 
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        time: str
    ):
        """Slash command to schedule daily scans"""
        # Check if user has permissions (you might want to add role checks)
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You need administrator permissions to schedule daily scans.", ephemeral=True)
            return
            
        await interaction.response.defer()
        
        try:
            # Validate time format
            import re
            if not re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', time):
                await interaction.followup.send("❌ Invalid time format. Please use 24h format like '08:00' or '20:30'")
                return
            
            # Save schedule to database
            import sqlite3
            conn = sqlite3.connect('data/pokemon_stock.db')
            cursor = conn.cursor()
            
            # Create schedule table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_schedules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    schedule_time TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Remove existing schedule for this guild
            cursor.execute('DELETE FROM daily_schedules WHERE guild_id = ?', (interaction.guild.id,))
            
            # Add new schedule
            cursor.execute('''
                INSERT INTO daily_schedules (guild_id, channel_id, schedule_time) 
                VALUES (?, ?, ?)
            ''', (interaction.guild.id, channel.id, time))
            
            conn.commit()
            conn.close()
            
            embed = discord.Embed(
                title="⏰ Daily Scan Scheduled",
                description=f"Daily Pokemon stock scans will be sent to {channel.mention} at **{time}**",
                color=0x2ecc71
            )
            
            embed.add_field(
                name="📋 What happens daily:",
                value="• Scan all NZ Pokemon stores\n• Report new arrivals\n• Track stock changes\n• Community activity summary",
                inline=False
            )
            
            embed.set_footer(text="Use /daily_scan for manual scans anytime")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in schedule_daily command: {e}")
            await interaction.followup.send("❌ An error occurred while scheduling daily scans.")
    
    @app_commands.command(name="check_nova_games", description="Check current Pokemon stock at Nova Games NZ")
    async def check_nova_games(self, interaction: discord.Interaction):
        """Check Nova Games NZ stock via slash command"""
        await interaction.response.defer(thinking=True)
        
        try:
            from monitors.generic_monitor import GenericStoreMonitor
            
            # Create mock config for the monitor
            class MockConfig:
                check_interval = 60
                max_concurrent_checks = 5
            
            monitor = GenericStoreMonitor(MockConfig())
            products = await monitor.get_nova_games_products()
            
            if not products:
                embed = discord.Embed(
                    title="🏪 Nova Games NZ",
                    description="❌ No Pokemon products found or store is unavailable",
                    color=0xe74c3c
                )
                await interaction.followup.send(embed=embed)
                return
            
            embed = discord.Embed(
                title="🏪 Nova Games NZ - Current Stock",
                description=f"Found **{len(products)}** Pokemon products",
                color=0x2ecc71,
                url="https://novagames.co.nz/collections/pokemon"
            )
            
            # Add products (limit to 10 for space)
            for i, product in enumerate(products[:10]):
                stock_status = "🟢 Available" if product.get('available', False) else "🔴 Out of Stock"
                price_text = f"${product['price']:.2f}" if product.get('price') and product['price'] > 0 else "TBA"
                
                embed.add_field(
                    name=f"{i+1}. {product['name'][:50]}{'...' if len(product['name']) > 50 else ''}",
                    value=f"{stock_status} • {price_text}\n[View Product]({product.get('url', 'https://novagames.co.nz')})",
                    inline=False
                )
            
            if len(products) > 10:
                embed.add_field(
                    name=f"+ {len(products) - 10} More Products",
                    value=f"Visit [Nova Games Pokemon Collection](https://novagames.co.nz/collections/pokemon) to see all products",
                    inline=False
                )
            
            embed.set_footer(text="💡 Use /daily_scan for all stores • Data refreshed on each command")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in check_nova_games command: {e}")
            embed = discord.Embed(
                title="🏪 Nova Games NZ",
                description="❌ Error checking store - may be temporarily unavailable",
                color=0xe74c3c
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="check_card_merchant", description="Check current Pokemon stock at Card Merchant NZ")
    async def check_card_merchant(self, interaction: discord.Interaction):
        """Check Card Merchant NZ stock via slash command"""
        await interaction.response.defer(thinking=True)
        
        try:
            from monitors.generic_monitor import GenericStoreMonitor
            
            # Create mock config for the monitor
            class MockConfig:
                check_interval = 60
                max_concurrent_checks = 5
            
            monitor = GenericStoreMonitor(MockConfig())
            products = await monitor.get_cardmerchant_products()
            
            if not products:
                embed = discord.Embed(
                    title="🏪 Card Merchant NZ",
                    description="❌ No Pokemon products found or store is unavailable",
                    color=0xe74c3c
                )
                await interaction.followup.send(embed=embed)
                return
            
            embed = discord.Embed(
                title="🏪 Card Merchant NZ - Current Stock",
                description=f"Found **{len(products)}** Pokemon products",
                color=0x2ecc71,
                url="https://cardmerchant.co.nz/collections/pokemon-sealed"
            )
            
            # Add products (limit to 10 for space)
            for i, product in enumerate(products[:10]):
                stock_status = "🟢 Available" if product.get('available', False) else "🔴 Out of Stock"
                price_text = f"${product['price']:.2f}" if product.get('price') and product['price'] > 0 else "Price TBA"
                
                embed.add_field(
                    name=f"{i+1}. {product['name'][:50]}{'...' if len(product['name']) > 50 else ''}",
                    value=f"{stock_status} • {price_text}\n[View Product]({product.get('url', 'https://cardmerchant.co.nz')})",
                    inline=False
                )
            
            if len(products) > 10:
                embed.add_field(
                    name=f"+ {len(products) - 10} More Products",
                    value=f"Visit [Card Merchant Pokemon Collection](https://cardmerchant.co.nz/collections/pokemon-sealed) to see all products",
                    inline=False
                )
            
            embed.set_footer(text="💡 Use /daily_scan for all stores • Data refreshed on each command")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in check_card_merchant command: {e}")
            embed = discord.Embed(
                title="🏪 Card Merchant NZ",
                description="❌ Error checking store - may be temporarily unavailable",
                color=0xe74c3c
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="check_eb_games", description="Check EB Games NZ Pokemon TCG stock")
    async def check_eb_games(self, interaction: discord.Interaction):
        """Check EB Games NZ stock via slash command"""
        await interaction.response.defer(thinking=True)
        
        try:
            from monitors.generic_monitor import GenericStoreMonitor
            
            # Create mock config for the monitor
            class MockConfig:
                check_interval = 60
                max_concurrent_checks = 5
            
            monitor = GenericStoreMonitor(MockConfig())
            products = await monitor.get_ebgames_products_selenium()
            
            if not products:
                embed = discord.Embed(
                    title="🏪 EB Games NZ",
                    description="❌ No Pokemon TCG products found or store is temporarily unavailable",
                    color=0xe74c3c
                )
                embed.add_field(
                    name="🔧 Status", 
                    value="May be temporarily down\nUsing Selenium browser automation",
                    inline=True
                )
                embed.add_field(
                    name="🌐 Manual Check",
                    value="[Visit EB Games Pokemon](https://www.ebgames.co.nz/search?q=pokemon)",
                    inline=True
                )
                await interaction.followup.send(embed=embed)
                return
            
            embed = discord.Embed(
                title="🏪 EB Games NZ - Pokemon TCG Stock",
                description=f"Found **{len(products)}** Pokemon TCG products\n*Using Selenium to bypass bot detection*",
                color=0x2ecc71,
                url="https://www.ebgames.co.nz/search?q=pokemon"
            )
            
            # Add products (limit to 10 for space)
            for i, product in enumerate(products[:10]):
                stock_status = "🟢 Available" if product.get('available', False) else "🔴 Out of Stock"
                price_text = f"${product['price']:.2f}" if product.get('price') and product['price'] > 0 else "Price TBA"
                
                embed.add_field(
                    name=f"{i+1}. {product['name'][:50]}{'...' if len(product['name']) > 50 else ''}",
                    value=f"{stock_status} • {price_text}\n[View Product]({product.get('url', 'https://www.ebgames.co.nz')})",
                    inline=False
                )
            
            if len(products) > 10:
                embed.add_field(
                    name=f"+ {len(products) - 10} More Products",
                    value="Visit [EB Games Pokemon Search](https://www.ebgames.co.nz/search?q=pokemon) to see all products",
                    inline=False
                )
            
            embed.set_footer(text="💡 This uses browser automation to access EB Games • Data refreshed on each command")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in check_eb_games command: {e}")
            embed = discord.Embed(
                title="🏪 EB Games NZ",
                description="❌ Error checking store - Selenium automation may have failed",
                color=0xe74c3c
            )
            embed.add_field(
                name="💡 Note",
                value="This command uses browser automation which may occasionally fail",
                inline=False
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="check_warehouse", description="Check The Warehouse NZ Pokemon TCG stock")
    async def check_warehouse(self, interaction: discord.Interaction):
        """Check The Warehouse NZ stock via slash command"""
        await interaction.response.defer(thinking=True)
        
        try:
            from monitors.generic_monitor import GenericStoreMonitor
            
            # Create mock config for the monitor
            class MockConfig:
                check_interval = 60
                max_concurrent_checks = 5
            
            monitor = GenericStoreMonitor(MockConfig())
            products = await monitor.get_warehouse_products_selenium()
            
            if not products:
                embed = discord.Embed(
                    title="🏪 The Warehouse NZ",
                    description="⚙️ **No Pokemon TCG products found**\n\nThis could be due to:\n• No Pokemon TCG stock currently available\n• Website changes or bot detection\n• Products not matching TCG keywords",
                    color=0xf39c12,
                    url="https://thewarehouse.co.nz"
                )
                embed.add_field(
                    name="🔧 Status",
                    value="Selenium scraper active\nSearching for Pokemon TCG only",
                    inline=True
                )
                embed.add_field(
                    name="🌐 Manual Check",
                    value="[Search Pokemon at The Warehouse](https://thewarehouse.co.nz/search?q=pokemon)",
                    inline=True
                )
                embed.set_footer(text="💡 Use /report_sighting to manually report Warehouse finds")
                await interaction.followup.send(embed=embed)
                return
            
            embed = discord.Embed(
                title="🏪 The Warehouse NZ - Pokemon TCG Stock",
                description=f"Found **{len(products)}** Pokemon TCG products",
                color=0x2ecc71,
                url="https://thewarehouse.co.nz/search?q=pokemon"
            )
            
            # Add products (limit to 10 for space)
            for i, product in enumerate(products[:10]):
                stock_status = "🟢 Available" if product.get('available', False) else "🔴 Out of Stock"
                price_text = f"${product['price']:.2f}" if product.get('price') and product['price'] > 0 else "Price TBA"
                
                embed.add_field(
                    name=f"{i+1}. {product['name'][:50]}{'...' if len(product['name']) > 50 else ''}",
                    value=f"{stock_status} • {price_text}\n[View Product]({product.get('url', 'https://thewarehouse.co.nz')})",
                    inline=False
                )
            
            if len(products) > 10:
                embed.add_field(
                    name=f"+ {len(products) - 10} More Products",
                    value="Visit [The Warehouse Pokemon Search](https://thewarehouse.co.nz/search?q=pokemon) to see all products",
                    inline=False
                )
            
            embed.set_footer(text="🤖 Powered by Selenium • Pokemon TCG products only")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in check_warehouse command: {e}")
            embed = discord.Embed(
                title="🏪 The Warehouse NZ",
                description="❌ Error checking store with Selenium - may be temporarily unavailable",
                color=0xe74c3c
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="check_jb_hifi", description="Check JB Hi-Fi NZ Pokemon TCG stock")
    async def check_jb_hifi(self, interaction: discord.Interaction):
        """Check JB Hi-Fi NZ stock via slash command"""
        await interaction.response.defer(thinking=True)
        
        try:
            from monitors.generic_monitor import GenericStoreMonitor
            
            # Create mock config for the monitor
            class MockConfig:
                check_interval = 60
                max_concurrent_checks = 5
            
            monitor = GenericStoreMonitor(MockConfig())
            products = await monitor.get_jbhifi_products_selenium()
            
            if not products:
                embed = discord.Embed(
                    title="🏪 JB Hi-Fi NZ",
                    description="⚙️ **No Pokemon TCG products found**\n\nThis could be due to:\n• No Pokemon TCG stock currently available\n• Website changes or bot detection\n• Products not matching TCG keywords",
                    color=0xf39c12,
                    url="https://jbhifi.co.nz"
                )
                embed.add_field(
                    name="🔧 Status",
                    value="Selenium scraper active\nSearching for Pokemon TCG only",
                    inline=True
                )
                embed.add_field(
                    name="🌐 Manual Check",
                    value="[Search Pokemon at JB Hi-Fi](https://jbhifi.co.nz/search/?query=pokemon)",
                    inline=True
                )
                embed.set_footer(text="💡 Use /report_sighting to manually report JB Hi-Fi finds")
                await interaction.followup.send(embed=embed)
                return
            
            embed = discord.Embed(
                title="🏪 JB Hi-Fi NZ - Pokemon TCG Stock", 
                description=f"Found **{len(products)}** Pokemon TCG products",
                color=0x2ecc71,
                url="https://jbhifi.co.nz/search/?query=pokemon"
            )
            
            # Add products (limit to 10 for space)
            for i, product in enumerate(products[:10]):
                stock_status = "🟢 Available" if product.get('available', False) else "🔴 Out of Stock"
                price_text = f"${product['price']:.2f}" if product.get('price') and product['price'] > 0 else "Price TBA"
                
                embed.add_field(
                    name=f"{i+1}. {product['name'][:50]}{'...' if len(product['name']) > 50 else ''}",
                    value=f"{stock_status} • {price_text}\n[View Product]({product.get('url', 'https://jbhifi.co.nz')})",
                    inline=False
                )
            
            if len(products) > 10:
                embed.add_field(
                    name=f"+ {len(products) - 10} More Products",
                    value="Visit [JB Hi-Fi Pokemon Search](https://jbhifi.co.nz/search/?query=pokemon) to see all products",
                    inline=False
                )
            
            embed.set_footer(text="🤖 Powered by Selenium • Pokemon TCG products only")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in check_jb_hifi command: {e}")
            embed = discord.Embed(
                title="🏪 JB Hi-Fi NZ",
                description="❌ Error checking store with Selenium - may be temporarily unavailable",
                color=0xe74c3c
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="check_mighty_ape", description="Check Mighty Ape NZ Pokemon TCG stock")
    async def check_mighty_ape(self, interaction: discord.Interaction):
        """Check Mighty Ape NZ stock via slash command"""
        await interaction.response.defer(thinking=True)
        
        try:
            from monitors.generic_monitor import GenericStoreMonitor
            
            # Create mock config for the monitor
            class MockConfig:
                check_interval = 60
                max_concurrent_checks = 5
            
            monitor = GenericStoreMonitor(MockConfig())
            products = await monitor.get_mightyape_products_selenium()
            
            if not products:
                embed = discord.Embed(
                    title="🏪 Mighty Ape NZ",
                    description="⚙️ **No Pokemon TCG products found**\n\nThis could be due to:\n• No Pokemon TCG stock currently available\n• Website changes or bot detection\n• Products not matching TCG keywords",
                    color=0xf39c12,
                    url="https://www.mightyape.co.nz"
                )
                embed.add_field(
                    name="🔧 Status",
                    value="Selenium scraper active\nSearching for Pokemon TCG only",
                    inline=True
                )
                embed.add_field(
                    name="🌐 Manual Check",
                    value="[Search Pokemon TCG at Mighty Ape](https://www.mightyape.co.nz/mn/shop/?q=pokemon+tcg)",
                    inline=True
                )
                embed.set_footer(text="💡 Use /report_sighting to manually report Mighty Ape finds")
                await interaction.followup.send(embed=embed)
                return
            
            embed = discord.Embed(
                title="🏪 Mighty Ape NZ - Pokemon TCG Stock",
                description=f"Found **{len(products)}** Pokemon TCG products",
                color=0x2ecc71,
                url="https://www.mightyape.co.nz/mn/shop/?q=pokemon+tcg"
            )
            
            # Add products (limit to 10 for space)
            for i, product in enumerate(products[:10]):
                stock_status = "🟢 Available" if product.get('available', False) else "🔴 Out of Stock"
                price_text = f"${product['price']:.2f}" if product.get('price') and product['price'] > 0 else "Price TBA"
                
                embed.add_field(
                    name=f"{i+1}. {product['name'][:50]}{'...' if len(product['name']) > 50 else ''}",
                    value=f"{stock_status} • {price_text}\n[View Product]({product.get('url', 'https://www.mightyape.co.nz')})",
                    inline=False
                )
            
            if len(products) > 10:
                embed.add_field(
                    name=f"+ {len(products) - 10} More Products",
                    value="Visit [Mighty Ape Pokemon TCG Search](https://www.mightyape.co.nz/mn/shop/?q=pokemon+tcg) to see all products",
                    inline=False
                )
            
            embed.set_footer(text="🤖 Powered by Selenium • Pokemon TCG products only")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in check_mighty_ape command: {e}")
            embed = discord.Embed(
                title="🏪 Mighty Ape NZ",
                description="❌ Error checking store with Selenium - may be temporarily unavailable",
                color=0xe74c3c
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="check_kmart", description="Check Kmart NZ Pokemon TCG stock")
    async def check_kmart(self, interaction: discord.Interaction):
        """Check Kmart NZ stock via slash command"""
        await interaction.response.defer(thinking=True)
        
        try:
            from monitors.generic_monitor import GenericStoreMonitor
            
            # Create mock config for the monitor
            class MockConfig:
                check_interval = 60
                max_concurrent_checks = 5
            
            monitor = GenericStoreMonitor(MockConfig())
            products = await monitor.get_kmart_products_selenium()
            
            if not products:
                embed = discord.Embed(
                    title="🏪 Kmart NZ",
                    description="⚙️ **No Pokemon TCG products found**\n\nThis could be due to:\n• No Pokemon TCG stock currently available\n• Website changes or bot detection\n• Products not matching TCG keywords",
                    color=0xf39c12,
                    url="https://kmart.co.nz"
                )
                embed.add_field(
                    name="🔧 Status",
                    value="Selenium scraper active\nSearching for Pokemon TCG only",
                    inline=True
                )
                embed.add_field(
                    name="🌐 Manual Check",
                    value="[Search Pokemon at Kmart](https://www.kmart.co.nz/search/?text=pokemon)",
                    inline=True
                )
                embed.set_footer(text="💡 Use /report_sighting to manually report Kmart finds")
                await interaction.followup.send(embed=embed)
                return
            
            embed = discord.Embed(
                title="🏪 Kmart NZ - Pokemon TCG Stock",
                description=f"Found **{len(products)}** Pokemon TCG products",
                color=0x2ecc71,
                url="https://www.kmart.co.nz/search/?text=pokemon"
            )
            
            # Add products (limit to 10 for space)
            for i, product in enumerate(products[:10]):
                stock_status = "🟢 Available" if product.get('available', False) else "🔴 Out of Stock"
                price_text = f"${product['price']:.2f}" if product.get('price') and product['price'] > 0 else "Price TBA"
                
                embed.add_field(
                    name=f"{i+1}. {product['name'][:50]}{'...' if len(product['name']) > 50 else ''}",
                    value=f"{stock_status} • {price_text}\n[View Product]({product.get('url', 'https://kmart.co.nz')})",
                    inline=False
                )
            
            if len(products) > 10:
                embed.add_field(
                    name=f"+ {len(products) - 10} More Products",
                    value="Visit [Kmart Pokemon Search](https://www.kmart.co.nz/search/?text=pokemon) to see all products",
                    inline=False
                )
            
            embed.set_footer(text="🤖 Powered by Selenium • Pokemon TCG products only")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in check_kmart command: {e}")
            embed = discord.Embed(
                title="🏪 Kmart NZ",
                description="❌ Error checking store with Selenium - may be temporarily unavailable",
                color=0xe74c3c
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="check_farmers", description="Check Farmers NZ Pokemon section")
    async def check_farmers(self, interaction: discord.Interaction):
        """Check Farmers NZ stock via slash command"""
        await interaction.response.defer(thinking=True)
        
        embed = discord.Embed(
            title="🏪 Farmers NZ",
            description="⚙️ **Pokemon Parsing Not Yet Implemented**\n\nStore scanning functionality not yet built.",
            color=0xf39c12,
            url="https://farmers.co.nz"
        )
        
        embed.add_field(
            name="🔧 Status",
            value="Store parsing not implemented\nFuture development planned",
            inline=True
        )
        
        embed.add_field(
            name="🌐 Manual Check",
            value="[Visit Farmers NZ](https://farmers.co.nz)",
            inline=True
        )
        
        embed.set_footer(text="💡 Use /report_sighting to manually report Farmers finds")
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(SlashCommands(bot))