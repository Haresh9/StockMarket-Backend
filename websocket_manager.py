from SmartApi.smartWebSocketV2 import SmartWebSocketV2
from fastapi import WebSocket
from typing import List
import json
import asyncio
from market import MarketAnalyzer

class ConnectionManager:
    """
    Manages WebSocket connections with the Frontend and Angel One.
    """
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.angel_socket = None
        self.angel_api = None
    def set_api_instance(self, api_instance):
        self.angel_api = api_instance

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def fetch_real_data(self, ticker, token):
        """
        Fetches Real LTP and Volume (Yesterday's Close) from Angel One.
        Runs blocking API calls in a separate thread to avoid blocking the event loop.
        """
        try:
            # Helper function for blocking calls
            def fetch_sync():
                ltp_val = None
                vol_val = 0
                
                try:
                    # 1. Get LTP
                    ltp_res = self.angel_api.ltpData("BSE", ticker.replace(".BSE", ""), token)
                    if ltp_res and 'data' in ltp_res:
                        ltp_val = ltp_res['data']['ltp']
                    
                    # 2. Get Volume (Latest available Candle)
                    from datetime import datetime, timedelta
                    today = datetime.now().strftime("%Y-%m-%d")
                    five_days_ago = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
                    
                    historicParam={
                        "exchange": "BSE",
                        "symboltoken": token,
                        "interval": "ONE_DAY",
                        "fromdate": f"{five_days_ago} 00:00", 
                        "todate": f"{today} 23:59"
                    }
                    candle_res = self.angel_api.getCandleData(historicParam)
                    if candle_res and candle_res['data']:
                        # Get the last candle (latest date)
                        last_candle = candle_res['data'][-1]
                        # Input: [timestamp, open, high, low, close, volume]
                        vol_val = last_candle[5]
                except Exception as inner_e:
                    print(f"API call error for {ticker}: {inner_e}")
                    
                return ltp_val, vol_val

            # Run in thread pool
            ltp, volume = await asyncio.to_thread(fetch_sync)
            return ltp, volume

        except Exception as e:
            print(f"Error fetching real data for {ticker}: {e}")
            return None, None

    async def mock_data_generator(self):
        """
        HYBRID: Uses Real Data if available (via API), else Mock.
        """
        import random
        
        # Token Map (Discovered via Script)
        token_map = {
            "RPOWER.BSE": "532939",
            "TCS.BSE": "532540",
            "HDFCBANK.BSE": "500180",
            "ICICIBANK.BSE": "532174",
            "INFY.BSE": "500209",
            "IREDA.BSE": "544026",
            "HINDCOPPER.BSE": "513599",
            "KAYNES.BSE": "543664",
            "HFCL.BSE": "500183",
            "SOLARINDS.BSE": "532725",
            "GROWW.BSE": "544603",
            "ORKLAINDIA.BSE": "544595",
            "EXCELSOFT.BSE": "544617",
            "MTARTECH.BSE": "543270",
            "PARAS.BSE": "543367",
            "HAL.BSE": "541154",
            "SUZLON.BSE": "532667",
            "GMDCLTD.BSE": "532181",
            "SWIGGY.BSE": "544285",
            "BEL.BSE": "500049",
            "ADANIPOWER.BSE": "533096",
            "ZOMATO.BSE": "543320",
            "LTF.BSE": "533519",
            "POWERINDIA.BSE": "543187",
            "TENNECO.BSE": "544612",
            "SUDEEP.BSE": "544619"
        }
        
        tickers = list(token_map.keys())
        market_data = []

        for ticker in tickers:
            token = token_map.get(ticker)
            real_ltp = None
            real_vol = None
            
            if self.angel_api and token:
                real_ltp, real_vol = await self.fetch_real_data(ticker, token)

            # Fallback to Random if API fails or token unknown
            if real_ltp is None:
                real_ltp = random.uniform(100, 3000)
            if real_vol is None:
                real_vol = random.randint(10000, 5000000)

            # Simulate Depth based on Real LTP
            # We create specific orders around the LTP to make it look realistic
            spread = real_ltp * 0.001 # 0.1% spread
            buy_price = real_ltp - spread
            sell_price = real_ltp + spread
            
            # Weighted quantity based on volume
            avg_qty = int(real_vol / 500) if real_vol else 1000
            
            depth = {
                'buy': [{'quantity': random.randint(int(avg_qty*0.5), int(avg_qty*1.5)), 'price': buy_price} for _ in range(5)],
                'sell': [{'quantity': random.randint(int(avg_qty*0.5), int(avg_qty*1.5)), 'price': sell_price} for _ in range(5)],
                'tradedVolume': real_vol
            }
            
            analysis = MarketAnalyzer.calculate_strength(depth)
            analysis['symbol'] = ticker
            analysis['ltp'] = real_ltp # ADDED: Inject Real LTP for display
            # Override with Real LTP for display if you want, but analysis uses depth
            market_data.append(analysis)
            
        return market_data

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

    def start_angel_socket(self, auth_token, api_key, client_code, feed_token):
        """
        Initializes Angel One WebSocket.
        """
        self.angel_socket = SmartWebSocketV2(auth_token, api_key, client_code, feed_token)
        
        def on_data(wsapp, msg):
            # Process incoming tick data
            # Note: The actual processing depends on the message structure from Angel One
            # We assume we subscribed to SNAPQUOTE or DEPTH to get buy/sell quantities
            
            # For this example, we parse the message and use MarketAnalyzer
            # Since real parsing is complex without live docs, we'll assume 'msg' 
            # contains 'best_5_buy_data' and 'best_5_sell_data' if subscribed to depth.
            
            # This is a PLACEHOLDER for the callback logic to bridge the gap.
            # In production, specific byte-parsing or JSON parsing from the SDK is needed.
            
            # If the SDK returns a python dict directly:
            if isinstance(msg, dict):
                 # Transform to format expected by MarketAnalyzer
                 # This mapping is crucial and depends on exact SDK response format
                 pass

        def on_open(wsapp):
            print("Angel One WebSocket Connected")
            # Subscribe to Nifty 50 or specific tokens
            # mode: 2 for FULL depth (Best 5) is required for our logic
            # exchange_type: 1 (NSE), 3 (BSE)
            # tokens: ["500325"] # Example BSE Token (RPOWER)
            
            # self.angel_socket.subscribe(correlation_id="abc", mode=2, token_list=[{"exchangeType": 3, "tokens": ["500325"]}])
            pass

        self.angel_socket.on_data = on_data
        self.angel_socket.on_open = on_open
        self.angel_socket.connect()
        


socket_manager = ConnectionManager()
