import discord
from discord.ext import commands
from typing import Optional
import logging

from utils.helpers import clean_sku

async def handle_add_sku(bot, ctx, sku: str, store: str, product_name: Optional[str] = None):
    """Handle adding a SKU to monitor"""
    try:
        clean_sku_value = clean_sku(sku)
        
        success = await bot.db_manager.add_product(
            sku=clean_sku_value,
            store_name=store.lower(),
            product_name=product_name
        )
        
        if success:
            embed = discord.Embed(
                title="✅ SKU Added",
                description=f"Now monitoring **{clean_sku_value}** from **{store}**",
                color=0x00ff00
            )
            if product_name:
                embed.add_field(name="Product", value=product_name, inline=False)
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Failed to add SKU. It may already exist.")
            
    except Exception as e:
        logging.error(f"Error in add_sku command: {e}")
        await ctx.send("❌ An error occurred while adding the SKU.")

async def handle_remove_sku(bot, ctx, sku: str, store: Optional[str] = None):
    """Handle removing a SKU from monitoring"""
    try:
        clean_sku_value = clean_sku(sku)
        
        success = await bot.db_manager.remove_product(
            sku=clean_sku_value,
            store_name=store.lower() if store else None
        )
        
        if success:
            embed = discord.Embed(
                title="✅ SKU Removed",
                description=f"No longer monitoring **{clean_sku_value}**",
                color=0xff9900
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ SKU not found or failed to remove.")
            
    except Exception as e:
        logging.error(f"Error in remove_sku command: {e}")
        await ctx.send("❌ An error occurred while removing the SKU.")

async def handle_list_skus(bot, ctx):
    """Handle listing all monitored SKUs"""
    try:
        products = await bot.db_manager.get_all_products()
        
        if not products:
            await ctx.send("📭 No SKUs are currently being monitored.")
            return
        
        embed = discord.Embed(
            title="📋 Monitored SKUs",
            description=f"Currently monitoring {len(products)} products",
            color=bot.config.embed_color
        )
        
        # Group by store
        stores = _group_products_by_store(products)
        
        for store, store_products in stores.items():
            product_list = _format_product_list(store_products)
            
            embed.add_field(
                name=f"🏪 {store.title()}",
                value="\n".join(product_list) if product_list else "None",
                inline=False
            )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        logging.error(f"Error in list_skus command: {e}")
        await ctx.send("❌ An error occurred while fetching SKUs.")

def _group_products_by_store(products):
    """Group products by store name"""
    stores = {}
    for product in products:
        store = product['store_name']
        if store not in stores:
            stores[store] = []
        stores[store].append(product)
    return stores

def _format_product_list(store_products):
    """Format product list for display"""
    product_list = []
    for product in store_products[:10]:  # Limit to 10 per store
        status_emoji = "🟢" if product['current_stock_status'] == 'In Stock' else "🔴"
        product_info = f"{status_emoji} {product['sku']}"
        if product['product_name']:
            product_info += f" - {product['product_name'][:30]}..."
        product_list.append(product_info)
    
    if len(store_products) > 10:
        product_list.append(f"... and {len(store_products) - 10} more")
    
    return product_list

async def handle_check_now(bot, ctx):
    """Handle immediate stock check"""
    try:
        await ctx.send("🔄 Starting immediate stock check...")
        
        products = await bot.db_manager.get_all_products()
        
        if not products:
            await ctx.send("📭 No products to check.")
            return
        
        stock_changes = await bot.monitor_manager.check_all_products(products)
        
        if stock_changes:
            await bot.notification_manager.send_stock_notifications(stock_changes)
            
        embed = discord.Embed(
            title="✅ Stock Check Complete",
            description=f"Checked {len(products)} products\nFound {len(stock_changes)} changes",
            color=0x00ff00
        )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        logging.error(f"Error in check_now command: {e}")
        await ctx.send("❌ An error occurred during the stock check.")

def setup_commands(bot):
    """Setup all bot commands"""
    
    @bot.command(name='add_sku')
    async def add_sku(ctx, sku: str, store: str, *, product_name: Optional[str] = None):
        """Add a SKU to monitor
        
        Usage: !add_sku SKU123 pokemon_center Pokemon Card Name
        """
        await handle_add_sku(bot, ctx, sku, store, product_name)
    
    @bot.command(name='remove_sku')
    async def remove_sku(ctx, sku: str, store: Optional[str] = None):
        """Remove a SKU from monitoring
        
        Usage: !remove_sku SKU123 [store_name]
        """
        await handle_remove_sku(bot, ctx, sku, store)
    
    @bot.command(name='list_skus')
    async def list_skus(ctx):
        """List all monitored SKUs
        
        Usage: !list_skus
        """
        await handle_list_skus(bot, ctx)
    
    @bot.command(name='check_now')
    async def check_now(ctx):
        """Force an immediate stock check
        
        Usage: !check_now
        """
        await handle_check_now(bot, ctx)
    
    @bot.command(name='set_interval')
    @commands.has_permissions(administrator=True)
    async def set_interval(ctx, seconds: int):
        """Set the check interval (admin only)
        
        Usage: !set_interval 300
        """
        try:
            if seconds < 60:
                await ctx.send("❌ Interval must be at least 60 seconds.")
                return
            
            if seconds > 3600:
                await ctx.send("❌ Interval cannot exceed 1 hour (3600 seconds).")
                return
            
            bot.config.check_interval = seconds
            bot.stock_monitor_loop.change_interval(seconds=seconds)
            
            embed = discord.Embed(
                title="✅ Interval Updated",
                description=f"Check interval set to {seconds} seconds ({seconds // 60} minutes)",
                color=0x00ff00
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logging.error(f"Error in set_interval command: {e}")
            await ctx.send("❌ An error occurred while setting the interval.")
    
    @bot.command(name='bot_info')
    async def bot_info(ctx):
        """Display bot information and statistics
        
        Usage: !bot_info
        """
        try:
            products = await bot.db_manager.get_all_products()
            
            embed = discord.Embed(
                title="🤖 Pokemon Stock Bot Info",
                description="Real-time Pokemon product stock monitoring",
                color=bot.config.embed_color
            )
            
            embed.add_field(name="Monitored Products", value=len(products), inline=True)
            embed.add_field(name="Check Interval", value=f"{bot.config.check_interval}s", inline=True)
            embed.add_field(name="Supported Stores", value="Pokemon Center\nTCGPlayer\nBest Buy\nGameStop", inline=True)
            
            embed.add_field(
                name="Commands",
                value="`!add_sku` - Add SKU to monitor\n`!remove_sku` - Remove SKU\n`!list_skus` - List all SKUs\n`!check_now` - Force check",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logging.error(f"Error in bot_info command: {e}")
            await ctx.send("❌ An error occurred while fetching bot info.")
