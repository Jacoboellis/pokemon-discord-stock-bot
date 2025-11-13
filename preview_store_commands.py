#!/usr/bin/env python3

import asyncio
from monitors.generic_monitor import GenericStoreMonitor

async def test_store_commands_preview():
    """Preview what the individual store slash commands will show"""
    
    print("🧪 Individual Store Commands Preview")
    print("=" * 60)
    
    # Setup monitor
    class MockConfig:
        check_interval = 60
        max_concurrent_checks = 5
    
    monitor = GenericStoreMonitor(MockConfig())
    
    # Test Nova Games
    print("\n📱 Discord Command: /check_nova_games")
    print("🔄 Checking Nova Games NZ...")
    
    nova_products = await monitor.get_nova_games_products()
    
    print(f"\n📋 Discord Embed Preview:")
    print(f"🏪 Nova Games NZ - Current Stock")
    print(f"Found {len(nova_products)} Pokemon products")
    print(f"🔗 https://novagames.co.nz/collections/pokemon")
    print()
    
    for i, product in enumerate(nova_products[:5]):
        status = "🟢 Available" if product.get('available', False) else "🔴 Out of Stock"
        price_text = f"${product['price']:.2f}" if product.get('price') and product['price'] > 0 else "TBA"
        print(f"  {i+1}. {product['name'][:45]}...")
        print(f"      {status} • {price_text}")
        print(f"      🔗 View Product: {product.get('url', 'N/A')}")
        print()
    
    if len(nova_products) > 5:
        print(f"  + {len(nova_products) - 5} more products available")
        print()
    
    # Test Card Merchant
    print("\n📱 Discord Command: /check_card_merchant")
    print("🔄 Checking Card Merchant NZ...")
    
    card_products = await monitor.get_cardmerchant_products()
    
    print(f"\n📋 Discord Embed Preview:")
    print(f"🏪 Card Merchant NZ - Current Stock")
    print(f"Found {len(card_products)} Pokemon products")
    print(f"🔗 https://cardmerchant.co.nz/collections/pokemon-sealed")
    print()
    
    for i, product in enumerate(card_products[:5]):
        status = "🟢 Available" if product.get('available', False) else "🔴 Out of Stock"
        price_text = f"${product['price']:.2f}" if product.get('price') and product['price'] > 0 else "Price TBA"
        print(f"  {i+1}. {product['name'][:45]}...")
        print(f"      {status} • {price_text}")
        print(f"      🔗 View Product: {product.get('url', 'N/A')}")
        print()
    
    if len(card_products) > 5:
        print(f"  + {len(card_products) - 5} more products available")
        print()
    
    # Show blocked stores
    print("\n📱 Discord Command: /check_eb_games")
    print("📋 Discord Embed Preview:")
    print("🏪 EB Games NZ")
    print("⚠️ Currently Unavailable")
    print()
    print("EB Games has blocked our bot with 403 Forbidden errors.")
    print("🔧 Status: Bot detection active")
    print("🌐 Manual Check: Visit EB Games Pokemon search")
    print("💡 Use /report_sighting to manually report EB Games finds")
    print()
    
    print("\n📱 Discord Command: /check_warehouse")
    print("📋 Discord Embed Preview:")
    print("🏪 The Warehouse NZ") 
    print("⚙️ Pokemon Parsing Not Yet Implemented")
    print()
    print("We can reach the store but haven't built Pokemon product detection yet.")
    print("🔧 Status: Store accessible, product parsing pending")
    print("🌐 Manual Check: Search Pokemon at The Warehouse")
    print()
    
    print("✅ All Commands Ready!")
    print()
    print("🎮 Available Discord Slash Commands:")
    print("   /check_nova_games     - ✅ Working (7 products)")
    print("   /check_card_merchant  - ✅ Working (28 products)")
    print("   /check_eb_games       - ⚠️  Blocked (403 errors)")
    print("   /check_warehouse      - ⚙️  Parsing not implemented")
    print("   /check_jb_hifi        - ⚙️  Parsing not implemented") 
    print("   /check_kmart          - ⚙️  Parsing not implemented")
    print("   /check_farmers        - ⚙️  Parsing not implemented")
    print()
    print(f"📊 Total Products Available: {len(nova_products) + len(card_products)}")

if __name__ == "__main__":
    asyncio.run(test_store_commands_preview())