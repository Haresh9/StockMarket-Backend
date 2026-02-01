import requests

base_url = "http://localhost:8000"

def test_add():
    print("Adding RELIANCE to watchlist...")
    res = requests.post(f"{base_url}/watchlist/add", params={"symbol": "RELIANCE.BSE", "token": "500325"})
    print("Response:", res.json())

    print("\nChecking if it appears in market-strength...")
    res = requests.get(f"{base_url}/market-strength")
    data = res.json()
    symbols = [item['symbol'] for item in data]
    print("Symbols in market-strength:", symbols)
    
    if "RELIANCE.BSE" in symbols:
        print("\nSUCCESS: RELIANCE found in market data!")
    else:
        print("\nFAILURE: RELIANCE NOT found in market data.")

if __name__ == "__main__":
    try:
        test_add()
    except Exception as e:
        print("Error:", e)
