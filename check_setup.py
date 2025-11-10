"""
Pokemon Discord Stock Bot - Setup Status Check
This script checks if everything is properly configured.
"""
import os
import sys
from pathlib import Path

def check_setup():
    """Check if the bot is properly set up"""
    print("🔍 Pokemon Discord Bot Setup Check")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info >= (3, 8):
        print("✅ Python version:", sys.version.split()[0])
    else:
        print("❌ Python 3.8+ required, found:", sys.version.split()[0])
        return False
    
    # Check required packages
    required_packages = [
        ('discord', 'discord'), 
        ('aiohttp', 'aiohttp'), 
        ('bs4', 'beautifulsoup4'),
        ('requests', 'requests'), 
        ('dotenv', 'python-dotenv'), 
        ('aiosqlite', 'aiosqlite')
    ]
    
    missing_packages = []
    for import_name, package_name in required_packages:
        try:
            __import__(import_name)
            print(f"✅ {package_name} installed")
        except ImportError:
            missing_packages.append(package_name)
            print(f"❌ {package_name} missing")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    # Check .env file
    env_path = Path('.env')
    if env_path.exists():
        print("✅ .env file exists")
        
        # Check if it has required variables
        with open(env_path, 'r') as f:
            env_content = f.read()
        
        required_vars = ['DISCORD_TOKEN', 'GUILD_ID', 'CHANNEL_ID']
        missing_vars = []
        
        for var in required_vars:
            if f"{var}=your_" in env_content:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"⚠️  Configure these in .env: {', '.join(missing_vars)}")
        else:
            print("✅ .env file configured")
    else:
        print("❌ .env file missing")
        return False
    
    # Check project structure
    required_dirs = ['bot', 'database', 'monitors', 'utils']
    for directory in required_dirs:
        if Path(directory).exists():
            print(f"✅ {directory}/ directory exists")
        else:
            print(f"❌ {directory}/ directory missing")
            return False
    
    print("\n" + "=" * 50)
    if missing_packages or not env_path.exists():
        print("❌ Setup incomplete - see issues above")
        return False
    else:
        print("✅ Setup complete! Ready to configure Discord bot")
        print("\nNext steps:")
        print("1. Create Discord bot at https://discord.com/developers/applications")
        print("2. Copy bot token to .env file")
        print("3. Copy your Discord server and channel IDs to .env")
        print("4. Run: python main.py")
        return True

if __name__ == "__main__":
    check_setup()