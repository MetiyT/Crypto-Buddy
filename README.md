# CryptoBuddy

CryptoBuddy is a small, friendly rule-based chatbot that recommends cryptocurrencies from a predefined dataset based on profitability and sustainability rules.

## Files
- `cryptobuddy.py` — main chatbot script (run with `python cryptobuddy.py`)
- `cryptobuddy_transcript.json` — auto-generated after a session
- `README.md` — this file
- `requirements.txt` — required packages (optional)

## Run locally
1. (Optional) create venv: `python -m venv venv && source venv/bin/activate` (Windows: `venv\Scripts\activate`)
2. Install deps (if using optional features): `pip install -r requirements.txt`
3. Run: `python cryptobuddy.py`

## How this works
- Keyword matching interprets user intent.
- Simple scoring (trend, market cap, sustainability) ranks coins for profitability.
- Another rule picks sustainable coins (low energy + high sustainability score).
- Provides safe disclaimer: Not financial advice.

