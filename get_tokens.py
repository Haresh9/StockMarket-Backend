import os
from dotenv import load_dotenv
from SmartApi import SmartConnect
import pyotp

# Load Env
load_dotenv()

api_key = os.getenv("ANGEL_API_KEY")
client_id = os.getenv("ANGEL_CLIENT_ID")
pin = os.getenv("ANGEL_PIN")
totp_key = os.getenv("ANGEL_TOTP_KEY")

print(f"Logging in with Client ID: {client_id}")

try:
    smart_api = SmartConnect(api_key=api_key)
    totp = pyotp.TOTP(totp_key).now()
    data = smart_api.generateSession(client_id, pin, totp)
    
    if data['status'] == False:
        print(f"Login Failed: {data['message']}")
        exit()
        
    print("Login Success. Verifying Tokens...")

    # Potential tokens found via web search
    test_tokens = {
        "POWERINDIA": "543187",
        "TENNECO": "544612",
        "SUDEEP": "544619",
        "ZOMATO": "543320",
        "L&TFH": "533519",
        "ETERNAL": "543320" # Likely brand name for Zomato
    }
    
    for symbol, token in test_tokens.items():
        try:
            print(f"Testing {symbol} (Token: {token})...")
            res = smart_api.ltpData("BSE", symbol, token)
            if res['status'] and res['data'] and 'ltp' in res['data']:
                print(f"SUCCESS: {symbol} (Token {token}) LTP = {res['data']['ltp']}")
            else:
                print(f"FAILED: {symbol} (Token {token}) - {res.get('message', 'No message')}")
        except Exception as e:
             print(f"ERROR: {symbol} - {e}")

except Exception as e:
    print(f"Error: {e}")
