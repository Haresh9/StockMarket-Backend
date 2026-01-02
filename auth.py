from SmartApi import SmartConnect
import pyotp
import os
from typing import Dict, Optional

class AngelOneAuth:
    """
    Handles authentication with Angel One SmartAPI.
    """
    def __init__(self):
        self.api_key = os.getenv("ANGEL_API_KEY")
        self.client_id = os.getenv("ANGEL_CLIENT_ID")
        self.pin = os.getenv("ANGEL_PIN")
        self.totp_key = os.getenv("ANGEL_TOTP_KEY")
        self.smart_api = None

    def login(self) -> Dict:
        """
        Logs in to Angel One and returns the session data including tokens.
        """
        if not all([self.api_key, self.client_id, self.pin, self.totp_key]):
             raise ValueError("Missing Angel One credentials in environment variables.")

        try:
            self.smart_api = SmartConnect(api_key=self.api_key)
            
            # Generate TOTP
            totp = pyotp.TOTP(self.totp_key).now()
            
            # Generate Session
            data = self.smart_api.generateSession(self.client_id, self.pin, totp)
            
            if data['status'] == False:
                raise Exception(f"Login Failed: {data['message']}")
                
            return {
                "jwtToken": data['data']['jwtToken'],
                "feedToken": data['data']['feedToken'],
                "refreshToken": data['data']['refreshToken']
            }
        except Exception as e:
            print(f"Authentication Error: {e}")
            raise e

    def get_smart_api_instance(self):
        if not self.smart_api:
             self.login()
        return self.smart_api
