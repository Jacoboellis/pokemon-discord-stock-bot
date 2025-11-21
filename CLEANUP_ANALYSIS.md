# Pokemon Discord Stock Bot - Cleanup Analysis

## 📁 CURRENT STATE ANALYSIS

### ✅ KEEP - Essential Core Files
**Main Application:**
- `main.py` - Main entry point ✅
- `bot/` directory - Discord bot functionality ✅
- `database/` directory - Database management ✅
- `monitors/` directory - Store monitoring ✅
- `utils/` directory - Helper utilities ✅
- `tests/` directory - Test suite ✅

**Configuration & Setup:**
- `.env` & `.env.example` - Environment config ✅
- `requirements.txt` - Dependencies ✅
- `pyproject.toml` - Project config ✅
- `README.md` - Documentation ✅
- `store_config.yml` - Store configurations ✅

**Working Scrapers:**
- `universal_selenium_scraper.py` - Our main scraper with bypass techniques ✅

### 🔄 CONSOLIDATE - Useful but needs integration
**Market Research (choose best one):**
- `nz_pokemon_market_survey.py` - Most comprehensive ✅ KEEP
- `advanced_phantasmal_search.py` - Has good bypass techniques ✅ MERGE INTO UNIVERSAL
- `current_pokemon_availability.py` - Basic version ❌ DELETE

**Status Checking:**
- `quick_status_check.py` - Working store checker ✅ KEEP

### ❌ DELETE - Debug/Experimental Files
**Debug Files (generated during troubleshooting):**
- `debug_ebgames.py`
- `debug_ebgames_detailed.py` 
- `debug_ebgames_html.py`
- `debug_pbtech.py`
- `simple_debug_ebgames.py`
- `save_ebgames_html.py`
- `save_pbtech_html.py`

**Debug HTML Output:**
- `ebgames_debug.html`
- `pbtech_debug.html`

**Experimental/Test Scripts:**
- `analyze_pbtech.py`
- `simple_test.py`
- `quick_pbtech_test.py`
- `quick_phantasmal_test.py`
- `simple_phantasmal_search.py`
- `search_phantasmal_flames.py`
- `quick_store_test.py`
- `test_pbtech_scraper.py`
- `test_store_status.py`
- `test_all_stores_status.py`

**Old/Legacy:**
- `config.py` (replaced by utils/config.py)
- `config.py.example`
- `daily_scan.py` (functionality in bot now)

### 📂 QUESTIONABLE DIRECTORIES
- `legacy/` - Check if still needed
- `pokemon_bot/` - Might be duplicate of `bot/`
- `data/` - Contains generated files, check if needed

## 🎯 CLEANUP PLAN

1. **Delete all debug files**
2. **Delete experimental test scripts**
3. **Merge best bypass techniques into universal_selenium_scraper.py**
4. **Check legacy/ and pokemon_bot/ directories**
5. **Update universal scraper with our working Cloudflare bypass**
6. **Test that the bot still works after cleanup**

## 📊 EXPECTED RESULT
- **Before:** ~45+ Python files
- **After:** ~10-15 essential files
- **Benefit:** Cleaner, more maintainable codebase
