# Legacy Store Monitors

This folder contains deprecated individual store monitor classes that have been replaced by the generic monitor system.

## Deprecated Files:
- `bestbuy.py` - Best Buy monitor (US store, removed for NZ focus)
- `pokemon_center.py` - Pokemon Center monitor (US store, removed for NZ focus)  
- `ebgames_nz.py` - EB Games NZ monitor (replaced by generic monitor)

## Current Implementation:
All store monitoring is now handled by `monitors/generic_monitor.py` with configuration in `store_config.yml`.

## Why Replaced:
1. **Maintainability**: Single generic monitor vs multiple store-specific classes
2. **Scalability**: Easy to add new stores via configuration 
3. **Consistency**: Unified approach to web scraping across all stores
4. **NZ Focus**: Removed US stores as requested by user

These files are kept for reference only and should not be used in the current codebase.