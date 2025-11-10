import asyncio
import logging
import os
from dotenv import load_dotenv

from bot.discord_bot import PokemonStockBot
from utils.config import Config
from utils.logger import setup_logger
from database.manager import DatabaseManager

# Load environment variables
load_dotenv()

async def main():
    """Main entry point for the Pokemon Stock Bot"""
    
    # Setup logging
    logger = setup_logger()
    logger.info("Starting Pokemon Stock Bot...")
    
    # Initialize configuration
    config = Config()
    
    # Initialize database
    db_manager = DatabaseManager(config.database_path)
    await db_manager.initialize()
    
    # Create and start the bot
    bot = PokemonStockBot(config, db_manager)
    
    try:
        # Start the bot
        await bot.start(config.discord_token)
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested...")
    except Exception as e:
        logger.error(f"Bot encountered an error: {e}")
    finally:
        await bot.close()
        db_manager.close()
        logger.info("Bot shutdown complete.")

if __name__ == "__main__":
    asyncio.run(main())
