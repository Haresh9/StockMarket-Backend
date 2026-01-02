import os
from dotenv import load_dotenv
from SmartApi import SmartConnect
import pyotp
from datetime import datetime

# Load Env
load_dotenv()

api_key = os.getenv("ANGEL_API_KEY")
client_id = os.getenv("ANGEL_CLIENT_ID")
pin = os.getenv("ANGEL_PIN")
totp_key = os.getenv("ANGEL_TOTP_KEY")

try:
    smart_api = SmartConnect(api_key=api_key)
    totp = pyotp.TOTP(totp_key).now()
    data = smart_api.generateSession(client_id, pin, totp)
    
    if data['status'] == False:
        print(f"Login Failed: {data['message']}")
        exit()
        
    print("Login Success. Fetching Candle Data for RPOWER...")

    # Exchange: BSE (segment "3"?) SmartApi usually takes "BSE"
    # Token: 532939
    # Interval: ONE_DAY
    # From/To: 2024-01-01 
    
    # Note: Historical API format
    # historicParam={
    # "exchange": "BSE",
    # "symboltoken": "532939",
    # "interval": "ONE_DAY",
    # "fromdate": "2024-01-01 09:00", 
    # "todate": "2024-01-01 15:30"
    # }
    
    historicParam={
    "exchange": "BSE",
    "symboltoken": "532939",
    "interval": "ONE_DAY",
    "fromdate": "2026-01-01 00:00", 
    "todate": "2026-01-01 23:59"
    }
    
    print(f"Params: {historicParam}")
    
    res = smart_api.getCandleData(historicParam)
    print(f"Result: {res}")
    
except Exception as e:
    print(f"Error: {e}")
