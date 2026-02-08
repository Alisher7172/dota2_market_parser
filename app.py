# Import required packages
from flask import Flask, render_template, request, jsonify
import aiohttp
import asyncio
import json
import os
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from pathlib import Path
import time

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)

# Thread pool for blocking operations
executor = ThreadPoolExecutor(max_workers=10)

class FastDota2Parser:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = "https://market.dota2.net/api"
        self.usd_to_rub_rate = 90
        
    async def get_item_prices_async(self, session, market_hash_name):
        """
        Search for item and get prices
        Returns: min_sell_price, max_buy_price
        """
        print(f"[ASYNC] Searching: {market_hash_name}")
        
        try:
            # Step 1: Search for item to find exact market_hash_name
            search_url = f"{self.base_url}/SearchItemByName/{market_hash_name}"
            params = {'key': self.api_key} if self.api_key else {}
            
            async with session.get(search_url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    print(f"[ASYNC] Search failed with HTTP {response.status}")
                    return None
                
                search_result = await response.json()
                print(f"[DEBUG] Search result: {search_result}")
                
                if not search_result.get('success'):
                    print(f"[ASYNC] Search API failed for: {market_hash_name}")
                    return None
                
                items = search_result.get('data', [])
                if not items:
                    print(f"[ASYNC] No items found matching: {market_hash_name}")
                    return None
                
                # Get first match
                first_item = items[0]
                exact_name = first_item.get('market_hash_name')
                
                if not exact_name:
                    print(f"[ASYNC] No market_hash_name in result")
                    return None
                
                print(f"[ASYNC] Found match: {exact_name}")
            
            # Step 2: Get price for the exact item
            price_url = f"{self.base_url}/ItemInfo"
            price_params = {
                'key': self.api_key,
                'market_hash_name': exact_name
            } if self.api_key else {'market_hash_name': exact_name}
            
            async with session.get(price_url, params=price_params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    print(f"[ASYNC] Price fetch failed with HTTP {response.status}")
                    return None
                
                price_result = await response.json()
                print(f"[DEBUG] Price result: {price_result}")
                
                if not price_result.get('success'):
                    print(f"[ASYNC] Price API failed")
                    return None
                
                item_data = price_result.get('item', {})
                min_price_str = item_data.get('min')
                max_price_str = item_data.get('max')
                
                if min_price_str:
                    try:
                        min_sell_rub = float(min_price_str)
                        max_buy_rub = float(max_price_str) if max_price_str else min_sell_rub * 0.85
                        
                        print(f"[ASYNC] ✓ Success: {exact_name} - Min: {min_sell_rub}₽, Max: {max_buy_rub}₽")
                        return {
                            'name': exact_name,
                            'min_sell_price_rub': min_sell_rub,
                            'max_buy_price_rub': max_buy_rub
                        }
                    except (ValueError, TypeError) as e:
                        print(f"[ASYNC] Price parse error: {e}")
                        return None
                else:
                    print(f"[ASYNC] No price data available")
                    return None
                    
        except asyncio.TimeoutError:
            print(f"[ASYNC] Timeout for: {market_hash_name}")
        except Exception as e:
            print(f"[ASYNC] Error for {market_hash_name}: {e}")
        
        return None
    
    async def parse_items_batch_async(self, item_list):
        """
        Parse multiple items in parallel using async
        """
        print(f"\n[BATCH] Starting async parsing for {len(item_list)} items")
        start_time = time.time()
        
        connector = aiohttp.TCPConnector(limit=10)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # Create tasks for all items
            tasks = [
                self.get_item_prices_async(session, item)
                for item in item_list
            ]
            
            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        elapsed = time.time() - start_time
        print(f"[BATCH] Completed in {elapsed:.2f}s")
        
        # Filter out None results and exceptions
        valid_results = [r for r in results if r and not isinstance(r, Exception)]
        return valid_results

class Dota2MarketParserV2:
    """Async + Threading hybrid parser for maximum speed"""
    
    def __init__(self, api_key=None):
        self.parser = FastDota2Parser(api_key=api_key)
        self.usd_to_rub_rate = 90
    
    def parse_items(self, item_list):
        """
        Main parsing method - runs async code in thread pool
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            results = loop.run_until_complete(
                self.parser.parse_items_batch_async(item_list)
            )
        finally:
            loop.close()
        
        return self.format_results(results)
    
    def format_results(self, results):
        """Format results with USD conversion and summary"""
        formatted = []
        total_min_sell_rub = 0
        total_max_buy_rub = 0
        
        for item in results:
            min_sell_rub = item['min_sell_price_rub']
            max_buy_rub = item['max_buy_price_rub']
            
            formatted_item = {
                'name': item['name'],
                'min_sell_price_rub': round(min_sell_rub, 2),
                'max_buy_price_rub': round(max_buy_rub, 2),
                'min_sell_price_usd': round(min_sell_rub / self.usd_to_rub_rate, 2),
                'max_buy_price_usd': round(max_buy_rub / self.usd_to_rub_rate, 2),
                'profit_rub': round(min_sell_rub - max_buy_rub, 2),
                'profit_usd': round((min_sell_rub - max_buy_rub) / self.usd_to_rub_rate, 2)
            }
            formatted.append(formatted_item)
            total_min_sell_rub += min_sell_rub
            total_max_buy_rub += max_buy_rub
        
        summary = {
            'total_min_sell_rub': round(total_min_sell_rub, 2),
            'total_max_buy_rub': round(total_max_buy_rub, 2),
            'total_min_sell_usd': round(total_min_sell_rub / self.usd_to_rub_rate, 2),
            'total_max_buy_usd': round(total_max_buy_rub / self.usd_to_rub_rate, 2),
            'total_profit_rub': round(total_min_sell_rub - total_max_buy_rub, 2),
            'total_profit_usd': round((total_min_sell_rub - total_max_buy_rub) / self.usd_to_rub_rate, 2)
        }
        
        return {
            'items': formatted,
            'summary': summary,
            'count': len(formatted)
        }

# Initialize parser
api_key = os.getenv('DOTA2_API_KEY')
parser = Dota2MarketParserV2(api_key=api_key)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/parse', methods=['POST'])
def parse_items():
    """API endpoint for parsing items"""
    print("\n" + "="*80)
    print("REQUEST: /api/parse")
    print("="*80)
    
    try:
        data = request.get_json()
        items_text = data.get('items', '').strip()
        
        # Parse item list
        item_list = [
            item.strip() 
            for item in items_text.split('\n') 
            if item.strip()
        ]
        
        if not item_list:
            return jsonify({'error': 'Item list is empty'}), 400
        
        print(f"Parsing {len(item_list)} items:")
        for item in item_list:
            print(f"  - {item}")
        
        # Parse items using async
        results = parser.parse_items(item_list)
        
        print(f"\nResults: {len(results['items'])} items parsed")
        print(f"Summary: {json.dumps(results['summary'], indent=2)}")
        
        return jsonify(results)
    
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'api_key_loaded': bool(api_key)
    })

if __name__ == '__main__':
    print(f"API Key: {'LOADED' if api_key else 'NOT LOADED'}")
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
