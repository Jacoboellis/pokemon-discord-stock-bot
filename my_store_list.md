# My Pokemon Store Watch List - New Zealand Focus
# Just add stores and SKUs here - no coding needed!

## New Zealand Stores

### Nova Games NZ ⭐⭐⭐ (BEST OPTION!)
- Base URL: https://novagames.co.nz
- Pokemon Collection: https://novagames.co.nz/collections/pokemon
- Status: ✅ PERFECT - Only shows in-stock items!
- Location: Auckland, NZ (Local business)

**Why This Store is Perfect:**
- 🎯 Only displays items that are actually in stock
- 💰 Clear pricing visible immediately  
- 🏪 Local NZ business (good for community)
- 🔄 Easy to monitor - if it's listed, it's available

**Current Products Available (9 items):**
- Trainer's Toolkit (2025) - $84.00
  SKU: `trainers-toolkit-2025`
- Ex Battle Deck - Victini Ex - $22.00
  SKU: `ex-battle-deck-victini-ex`
- Mega Evolution Booster Pack - $10.00 (IN-STORE ONLY)
  SKU: `mega-evolution-booster-pack` 
- League Battle Deck - Charizard Ex - $65.00
  SKU: `league-battle-deck-charizard-ex-1`
- League Battle Deck - Dragapult Ex - $65.00  
  SKU: `league-battle-deck-dragapult-ex`

### EB Games New Zealand
- Base URL: https://www.ebgames.co.nz
- Pokemon TCG search: https://www.ebgames.co.nz/search?q=pokemon%20tcg
- Status: ⚠️ BLOCKING REQUESTS - HTTP 403 errors

Products to monitor:
- SKU: 331696 - Pokemon TCG Mega Heroes Mini Tins - $25.00
  URL: https://www.ebgames.co.nz/product/toys-and-collectibles/331696-pokemon-tcg-mega-heroes-mini-tins-assorted

### The Warehouse NZ
- Base URL: https://www.thewarehouse.co.nz
- Pokemon TCG search: https://www.thewarehouse.co.nz/search?q=pokemon+tcg&lang=default&search-button=
- Status: 🔄 READY TO ADD

Products found:
- Pokemon 2024 World Championships Deck - $45.00
- Pokemon S&V 10.5 Unova Poster Box - $45.00
- SKU format: R2984751 (starts with R)

### JB Hi-Fi NZ
- Base URL: https://www.jbhifi.co.nz  
- Pokemon TCG search: https://www.jbhifi.co.nz/search?query=pokemon%20tcg
- Status: 🔄 READY TO ADD

### Kmart NZ
- Base URL: https://www.kmart.co.nz
- Pokemon search: https://www.kmart.co.nz/search/?searchTerm=pokemon%20cards
- Status: 🔄 READY TO ADD

### Farmers NZ
- Base URL: https://www.farmers.co.nz
- Pokemon TCG search: https://www.farmers.co.nz/search?SearchTerm=pokemon%20tcg
- Status: 🔄 READY TO ADD

## International Stores (For Later)

### Pokemon Center USA
- Base URL: https://www.pokemoncenter.com
- Pokemon TCG search: https://www.pokemoncenter.com/search?q=pokemon+tcg

### Target (US)
- Base URL: https://www.target.com
- Pokemon search: https://www.target.com/s?searchTerm=pokemon+cards

### Walmart (US)
- Base URL: https://www.walmart.com
- Pokemon search: https://www.walmart.com/search?q=pokemon+cards

### GameStop (US)
- Base URL: https://www.gamestop.com
- Pokemon search: https://www.gamestop.com/search/?q=pokemon+cards

### Best Buy (US)
- Base URL: https://www.bestbuy.com
- Pokemon search: https://www.bestbuy.com/site/searchpage.jsp?st=pokemon+cards

## Next Steps - Start Small Strategy 🎯

### Week 1: EB Games NZ (CURRENT)
- ✅ Bot already monitors EB Games NZ
- Add 3-5 specific Pokemon products you want to track
- Test notifications work properly

### Week 2: Add The Warehouse NZ
- Find specific Pokemon products you want
- Add SKUs using /add_sku command
- Test stock monitoring

### Week 3: Add JB Hi-Fi NZ
- Same process - find products, add SKUs
- Monitor how well the bot handles multiple NZ stores

### Week 4+: Scale Up
- Add Kmart NZ and Farmers NZ
- Fine-tune notification settings
- Consider international stores

## Quick Add Template:
When you find a specific product you want to monitor:

```
/add_sku sku:[SKU] store:[store_name] product_name:[Product Name]
```

Examples:
```
/add_sku sku:331696 store:ebgames_nz product_name:Pokemon TCG Mega Heroes Mini Tins
/add_sku sku:R2984751 store:thewarehouse_nz product_name:Pokemon 2024 World Championships Deck
```