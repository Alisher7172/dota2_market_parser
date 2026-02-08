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
        Get item prices using MassInfo API (optimized)
        Returns: min_sell_price, max_buy_price
        """
        print(f"[ASYNC] Fetching: {market_hash_name}")
        
        try:
            # Use MassInfo endpoint for all data at once
            # Parameters: SELL=2 (best sell), BUY=2 (best buy), HISTORY=0, INFO=0
            url = f"{self.base_url}/MassInfo/2/2/0/0"
            
            data = {
                'list': f"{market_hash_name}"
            }
            
            params = {'key': self.api_key} if self.api_key else {}
            
            async with session.post(url, data=data, params=params, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    if result.get('success') and result.get('results'):
                        item = result['results'][0]
                        
                        # Safely extract sell offers (minimum price)
                        sell_offers = item.get('sell_offers') if item else None
                        min_sell_price_kopeks = sell_offers.get('best_offer') if sell_offers else None
                        
                        # Safely extract buy offers (maximum buy price)
                        buy_offers = item.get('buy_offers') if item else None
                        max_buy_price_kopeks = buy_offers.get('best_offer') if buy_offers else None
                        
                        if min_sell_price_kopeks:
                            min_sell_rub = float(min_sell_price_kopeks) / 100
                            max_buy_rub = float(max_buy_price_kopeks) / 100 if max_buy_price_kopeks else min_sell_rub * 0.85
                            
                            print(f"[ASYNC] Success: {market_hash_name}")
                            return {
                                'name': market_hash_name,
                                'min_sell_price_rub': min_sell_rub,
                                'max_buy_price_rub': max_buy_rub
                            }
                        else:
                            print(f"[ASYNC] No price data for: {market_hash_name}")
                    else:
                        print(f"[ASYNC] API returned no results for: {market_hash_name}")
                    
                    return None
                else:
                    print(f"[ASYNC] HTTP {response.status} for: {market_hash_name}")
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
