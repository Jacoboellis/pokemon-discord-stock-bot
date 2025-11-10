import discord
from typing import List, Dict, Any
import logging
from datetime import datetime, timezone

from utils.config import Config

class NotificationManager:
    """Handles Discord notifications for stock changes"""
    
    def __init__(self, bot, config: Config):
        self.bot = bot
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    async def send_stock_notifications(self, stock_changes: List[Dict[str, Any]]):
        """Send notifications for stock changes"""
        if not stock_changes:
            return
        
        try:
            channel = self.bot.get_channel(self.config.channel_id)
            if not channel:
                self.logger.error(f"Notification channel {self.config.channel_id} not found")
                return
            
            for change in stock_changes:
                embed = self._create_stock_embed(change)
                
                # Mention role if configured
                content = None
                if self.config.notification_role:
                    role = discord.utils.get(channel.guild.roles, name=self.config.notification_role)
                    if role:
                        content = role.mention
                
                await channel.send(content=content, embed=embed)
                
            self.logger.info(f"Sent {len(stock_changes)} stock notifications")
            
        except Exception as e:
            self.logger.error(f"Error sending notifications: {e}")
    
    def _create_stock_embed(self, change: Dict[str, Any]) -> discord.Embed:
        """Create embed for stock change notification"""
        stock_status = change.get('stock_status', 'Unknown')
        sku = change.get('sku', 'Unknown')
        store = change.get('store_name', 'Unknown')
        product_name = change.get('product_name', '')
        price = change.get('price')
        product_url = change.get('product_url')
        
        # Determine embed color and emoji based on stock status
        if stock_status.lower() == 'in stock':
            color = 0x00ff00  # Green
            emoji = "🟢"
            title = f"{emoji} STOCK ALERT - IN STOCK!"
        elif stock_status.lower() == 'out of stock':
            color = 0xff0000  # Red
            emoji = "🔴"
            title = f"{emoji} STOCK ALERT - OUT OF STOCK"
        else:
            color = self.config.embed_color
            emoji = "🟡"
            title = f"{emoji} STOCK ALERT - STATUS UPDATE"
        
        embed = discord.Embed(
            title=title,
            url=product_url if product_url else None,
            color=color,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Add product information in the style you requested
        if product_name:
            embed.add_field(
                name="📦 Item",
                value=product_name,
                inline=False
            )
        
        embed.add_field(
            name="🏪 Store",
            value=store.title(),
            inline=True
        )
        
        embed.add_field(
            name="🔢 SKU",
            value=f"`{sku}`",
            inline=True
        )
        
        embed.add_field(
            name="📍 Location",
            value="Online",
            inline=True
        )
        
        embed.add_field(
            name="📊 Stock Status",
            value=f"{emoji} {stock_status}",
            inline=True
        )
        
        if price:
            embed.add_field(
                name="💰 Price",
                value=f"${price:.2f}",
                inline=True
            )
        
        # Add current date
        current_date = datetime.now().strftime("%d/%m/%Y")
        embed.add_field(
            name="📅 Last Checked",
            value=current_date,
            inline=True
        )
        
        # Add product URL as button-style link if available
        if product_url:
            embed.add_field(
                name="🔗 Product Link",
                value=f"[View on {store.title()}]({product_url})",
                inline=False
            )
        
        # Add footer with bot info
        embed.set_footer(
            text="Pokemon Stock Bot • Real-time monitoring",
            icon_url=None
        )
        
        # Add thumbnail if it's Pokemon related
        if any(word in (product_name or '').lower() for word in ['pokemon', 'pokémon', 'tcg', 'card']):
            # You can add a Pokemon logo thumbnail here
            pass
        
        return embed
    
    async def send_error_notification(self, error_message: str):
        """Send error notification to channel"""
        try:
            channel = self.bot.get_channel(self.config.channel_id)
            if not channel:
                return
            
            embed = discord.Embed(
                title="⚠️ Bot Error",
                description=error_message,
                color=0xff0000,
                timestamp=datetime.now(timezone.utc)
            )
            
            await channel.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error sending error notification: {e}")
    
    async def send_status_update(self, message: str):
        """Send general status update"""
        try:
            channel = self.bot.get_channel(self.config.channel_id)
            if not channel:
                return
            
            embed = discord.Embed(
                title="ℹ️ Bot Status",
                description=message,
                color=self.config.embed_color,
                timestamp=datetime.now(timezone.utc)
            )
            
            await channel.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error sending status update: {e}")
    
    async def send_release_notification(self, release: Dict[str, Any], notification_type: str = "advance"):
        """Send notification for upcoming release"""
        try:
            # Use the dedicated upcoming releases channel
            channel = self.bot.get_channel(int(self.config.upcoming_releases_channel))
            if not channel:
                self.logger.error("Upcoming releases channel not found")
                return
            
            # Create different embeds based on notification type
            if notification_type == "advance":
                # Advance notification (7 days before)
                embed = discord.Embed(
                    title="📅 UPCOMING POKEMON RELEASE",
                    description=f"**{release['product_name']}** is coming soon!",
                    color=0x3498db,
                    timestamp=datetime.now(timezone.utc)
                )
                
                embed.add_field(
                    name="🗓️ Release Date",
                    value=release['release_date'],
                    inline=True
                )
                
                # Calculate days until release
                release_date = datetime.strptime(release['release_date'], '%Y-%m-%d').date()
                today = datetime.now().date()
                days_until = (release_date - today).days
                
                embed.add_field(
                    name="⏰ Days Until Release",
                    value=f"{days_until} days",
                    inline=True
                )
                
            else:  # release day
                # Release day notification
                embed = discord.Embed(
                    title="🚨 POKEMON RELEASE DAY!",
                    description=f"**{release['product_name']}** is OUT NOW!",
                    color=0xe74c3c,
                    timestamp=datetime.now(timezone.utc)
                )
                
                embed.add_field(
                    name="🎯 Released Today",
                    value=release['release_date'],
                    inline=True
                )
            
            # Common fields for both notification types
            if release.get('estimated_price'):
                embed.add_field(
                    name="💰 Price",
                    value=f"${release['estimated_price']:.2f}",
                    inline=True
                )
            
            if release.get('store_name'):
                embed.add_field(
                    name="🏪 Store",
                    value=release['store_name'],
                    inline=True
                )
            
            if release.get('description'):
                embed.add_field(
                    name="📝 Description",
                    value=release['description'],
                    inline=False
                )
            
            embed.set_footer(
                text="Pokemon Stock Bot • Release Alert",
                icon_url=None
            )
            
            # Mention role if configured
            content = None
            if self.config.notification_role:
                role = discord.utils.get(channel.guild.roles, name=self.config.notification_role)
                if role:
                    if notification_type == "advance":
                        content = f"{role.mention} Upcoming release reminder!"
                    else:
                        content = f"{role.mention} New release available NOW!"
            
            await channel.send(content=content, embed=embed)
            self.logger.info("Sent %s notification for %s", notification_type, release['product_name'])
            
        except (discord.HTTPException, discord.Forbidden) as e:
            self.logger.error("Error sending release notification: %s", e)
