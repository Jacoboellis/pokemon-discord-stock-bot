<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Pokemon Discord Stock Bot - Copilot Instructions

## Project Context
This is a Discord bot project for monitoring Pokemon card/product stock from online retailers. The bot scrapes multiple store websites, tracks inventory changes, and sends Discord notifications when products become available.

## Code Style Guidelines
- Follow PEP 8 for Python code formatting
- Use async/await patterns for Discord and HTTP operations
- Implement proper error handling and logging
- Use type hints where appropriate
- Keep functions focused and modular

## Key Technologies
- **discord.py**: For Discord bot functionality
- **aiohttp/requests**: For web scraping and API calls
- **BeautifulSoup4**: For HTML parsing
- **SQLite**: For data persistence
- **asyncio**: For concurrent operations

## Architecture Patterns
- **Monitor Pattern**: Each store has its own monitor class inheriting from BaseMonitor
- **Command Pattern**: Discord commands are organized in separate modules
- **Observer Pattern**: Database triggers notifications when stock changes
- **Factory Pattern**: Store monitors are created based on configuration

## Important Notes
- Always use async functions for Discord operations
- Implement rate limiting to avoid being blocked by stores
- Use proper user agents and headers when scraping
- Store sensitive data (tokens, APIs) in environment variables
- Implement proper database connection management
- Include comprehensive error handling for network operations

## Testing Guidelines
- Mock external API calls and web scraping in tests
- Test Discord command functionality
- Verify database operations work correctly
- Test rate limiting and error scenarios
