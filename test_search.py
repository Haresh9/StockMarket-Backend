import os
from dotenv import load_dotenv
from SmartApi import SmartConnect
import pyotp
import json

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
        
    print("Login Success. Searching for TCS...")
    res = smart_api.searchScrip(exchange="BSE", searchscrip="TCS")
    
    if res and res.get('status') and res.get('data'):
        first_item = res['data'][0]
        print("First result keys:", first_item.keys())
        print("First result full data:", json.dumps(first_item, indent=2))
    else:
        print("Search failed or no data:", res)
        
except Exception as e:
    print(f"Error: {e}")
