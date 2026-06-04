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
                
                if not search_result.get('success'):
                    print(f"[ASYNC] Search API failed for: {market_hash_name}")
                    return None
                
                items = search_result.get('list', [])  # API returns 'list' not 'data'!
                if not items:
                    print(f"[ASYNC] No items found matching: {market_hash_name}")
                    return None
                
                # The search results contain SELL prices (what buyers pay)
                # Get lowest sell price (best deal if you're buying)
                first_item = items[0]  # Already sorted by price ascending
                exact_name = first_item.get('market_hash_name')
                classid = first_item.get('i_classid')
                instanceid = first_item.get('i_instanceid')
                min_sell_kopeks = first_item.get('price')  # Lowest sell price from search
                
                if not exact_name or not classid or not instanceid:
                    print(f"[ASYNC] Missing required fields in result")
                    return None
                
                # For BUY requests, we need to check a different endpoint
                # Let's use the Buy endpoint to get actual buy offers
                print(f"[ASYNC] Found: {exact_name}, checking auto-purchase requests...")
            
            # Step 2: Get BUY offers using BuyOffers endpoint (correct API path)
            buy_url = f"{self.base_url}/BuyOffers/{classid}_{instanceid}"
            buy_params = {'key': self.api_key} if self.api_key else {}
            
            print(f"[DEBUG] Calling BuyOffers: {buy_url}")
            print(f"[DEBUG] API Key present: {bool(self.api_key)}")
            
            async with session.get(buy_url, params=buy_params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                response_text = await response.text()
                print(f"[DEBUG] BuyOffers HTTP Status: {response.status}")
                print(f"[DEBUG] BuyOffers Raw Response: {response_text[:500]}")
                
                if response.status != 200:
                    print(f"[ERROR] BuyOffers failed! Using estimate (90% of sell price)")
                    # Fallback: use estimate
                    min_sell_rub = float(min_sell_kopeks) / 100 if min_sell_kopeks else 0
                    max_buy_rub = min_sell_rub * 0.90
                else:
                    try:
                        buy_result = json.loads(response_text)
                        print(f"[DEBUG] BuyOffers JSON: {json.dumps(buy_result, indent=2)}")
                    
                        # Priority: best_offer field (already the highest auto-purchase price)
                        if buy_result.get('success') and buy_result.get('best_offer'):
                            max_buy_kopeks = int(buy_result['best_offer'])
                            max_buy_rub = float(max_buy_kopeks) / 100
                            offers_count = len(buy_result.get('offers', []))
                            print(f"[SUCCESS] HIGHEST auto-purchase from best_offer: {max_buy_rub}₽ ({offers_count} total requests)")
                        elif buy_result.get('success') and buy_result.get('offers'):
                            # Fallback: calculate from offers array if best_offer missing
                            buy_offers_list = buy_result['offers']
                            max_buy_kopeks = max(int(offer.get('o_price', 0)) for offer in buy_offers_list)
                            max_buy_rub = float(max_buy_kopeks) / 100
                            print(f"[SUCCESS] Calculated HIGHEST from {len(buy_offers_list)} offers: {max_buy_rub}₽")
                        else:
                            # No buy offers exist, use estimate (90% of sell price)
                            max_buy_rub = (float(min_sell_kopeks) / 100 * 0.90) if min_sell_kopeks else 0
                            print(f"[WARNING] No auto-purchase requests exist, using estimate: {max_buy_rub}₽")
                    except Exception as e:
                        print(f"[ERROR] Failed to parse BuyOffers response: {e}")
                        min_sell_rub = float(min_sell_kopeks) / 100 if min_sell_kopeks else 0
                        max_buy_rub = min_sell_rub * 0.90
                    
                    min_sell_rub = float(min_sell_kopeks) / 100 if min_sell_kopeks else 0
                
                print(f"[RESULT] ✓ {exact_name}")
                print(f"         Min Sell: {min_sell_rub}₽ (you pay to buy)")
                print(f"         Max Buy:  {max_buy_rub}₽ (you get when selling to auto-purchase)")
                
                return {
                    'name': exact_name,
                    'min_sell_price_rub': min_sell_rub,
                    'max_buy_price_rub': max_buy_rub
                }
                    
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
