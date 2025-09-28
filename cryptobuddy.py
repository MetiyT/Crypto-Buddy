import re
import json
import datetime

# ---------- 2. Predefined Crypto Data ----------
crypto_db = {
    "Bitcoin": {
        "price_trend": "rising",
        "market_cap": "high",
        "energy_use": "high",
        "sustainability_score": 3.0
    },
    "Ethereum": {
        "price_trend": "stable",
        "market_cap": "high",
        "energy_use": "medium",
        "sustainability_score": 6.0
    },
    "Cardano": {
        "price_trend": "rising",
        "market_cap": "medium",
        "energy_use": "low",
        "sustainability_score": 8.0
    }
}

BOT_NAME = "CryptoBuddy"
TONE_PREFIX = "🌟 CryptoBuddy:"

# ---------- Helpers: scoring & rules ----------
def _trend_score(trend):
    t = trend.lower()
    if t == "rising":
        return 1.0
    if t == "stable":
        return 0.5
    return 0.0  # falling or unknown

def _market_score(market):
    m = market.lower()
    if m == "high":
        return 1.0
    if m == "medium":
        return 0.5
    return 0.0

def profitability_score(coin):
    """Combine trend, market cap, sustainability into a single 0..1 score."""
    data = crypto_db[coin]
    trend_s = _trend_score(data.get("price_trend", ""))
    market_s = _market_score(data.get("market_cap", ""))
    # sustainability normalized 0..1 (assuming input is 0..10)
    sustain_s = max(0.0, min(1.0, data.get("sustainability_score", 0) / 10.0))
    # weights: trend 40%, market 30%, sustainability 30%
    return 0.4 * trend_s + 0.3 * market_s + 0.3 * sustain_s

def most_profitable(n=1):
    ranked = sorted(crypto_db.keys(), key=profitability_score, reverse=True)
    return ranked[:n]

def most_sustainable(n=1, min_score=7.0):
    candidates = [c for c, d in crypto_db.items()
                  if d.get("energy_use", "").lower() == "low" and d.get("sustainability_score", 0) >= min_score]
    if not candidates:
        # fallback: rank by sustainability_score
        ranked = sorted(crypto_db.keys(), key=lambda c: crypto_db[c].get("sustainability_score", 0), reverse=True)
        return ranked[:n]
    return candidates[:n]

def coin_info(coin):
    d = crypto_db.get(coin)
    if not d:
        return None
    lines = [f"{coin}:"]
    for k, v in d.items():
        lines.append(f"  {k}: {v}")
    lines.append(f"  profitability_score: {profitability_score(coin):.2f}")
    return "\n".join(lines)

# ---------- Simple NLP-ish keyword matching ----------
def interpret_query(query):
    q = query.lower().strip()
    # direct keywords
    if any(word in q for word in ("sustain", "eco", "green", "environment")):
        return ("sustainability", None)
    if any(word in q for word in ("trend", "trending", "up", "rising")):
        return ("trending", None)
    if any(word in q for word in ("buy", "invest", "long-term", "growth", "best")):
        return ("recommend_profit", None)
    if "show" in q or "list" in q or "all" in q or "what coins" in q:
        return ("list", None)
    if "info" in q or "info about" in q or "tell me about" in q:
        # try to extract coin name
        for coin in crypto_db.keys():
            if coin.lower() in q:
                return ("info", coin)
    if q in ("help", "h", "?"):
        return ("help", None)
    if q in ("exit", "quit", "q"):
        return ("exit", None)
    # fallback: assume general recommend
    return ("recommend_profit", None)

# ---------- Bot response builder ----------
def respond(query):
    kind, payload = interpret_query(query)
    if kind == "sustainability":
        best = most_sustainable(n=1)
        coin = best[0]
        return f"{TONE_PREFIX} Invest in {coin}! 🌱 It's one of the most sustainable coins in the dataset.\n\n{coin_info(coin)}"
    if kind == "trending":
        best = most_profitable(n=1)
        coin = best[0]
        return f"{TONE_PREFIX} {coin} is trending up and scores well for growth potential. 🚀\n\n{coin_info(coin)}"
    if kind == "recommend_profit":
        ranked = most_profitable(n=3)
        lines = [f"{TONE_PREFIX} Top picks for potential long-term growth:"]
        for i, c in enumerate(ranked, 1):
            lines.append(f"{i}. {c} — trend: {crypto_db[c]['price_trend']}, market: {crypto_db[c]['market_cap']}, sustainability: {crypto_db[c]['sustainability_score']}/10")
        lines.append("\n⚠️ Not financial advice — always do your own research.")
        return "\n".join(lines)
    if kind == "list":
        lines = [f"{TONE_PREFIX} Current crypto DB:"]
        for c in crypto_db.keys():
            lines.append(f"- {c}")
        return "\n".join(lines)
    if kind == "info" and payload:
        return f"{TONE_PREFIX}\n{coin_info(payload)}"
    if kind == "help":
        return (f"{TONE_PREFIX} Try queries like:\n"
                "- 'Which crypto is trending up?'\n"
                "- 'What's the most sustainable coin?'\n"
                "- 'Which crypto should I buy for long-term growth?'\n"
                "- 'Show all coins' or 'Info about Cardano'\n"
                "Type 'exit' to quit.")
    if kind == "exit":
        return "exit"
    # default
    return (f"{TONE_PREFIX} I didn't get that. Type 'help' for example queries.")

# ---------- Main interactive loop ----------
def run_chat():
    print(f"Hello! I'm {BOT_NAME} — friendly crypto helper. Type 'help' for tips. (Type 'exit' to quit.)\n")
    transcript = []
    while True:
        try:
            user = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye — saved session to transcript.")
            break
        if not user:
            continue
        ts = datetime.datetime.now().isoformat(timespec='seconds')
        transcript.append({"time": ts, "you": user})
        reply = respond(user)
        if reply == "exit":
            print("CryptoBuddy: Bye! Stay curious and cautious. ⚠️")
            transcript.append({"time": datetime.datetime.now().isoformat(timespec='seconds'), "bot": "Bye"})
            break
        print(reply)
        transcript.append({"time": datetime.datetime.now().isoformat(timespec='seconds'), "bot": reply})

    # Save transcript for screenshots / submission
    try:
        with open("cryptobuddy_transcript.json", "w", encoding="utf-8") as f:
            json.dump(transcript, f, indent=2)
        print("Transcript saved to cryptobuddy_transcript.json")
    except Exception as e:
        print("Couldn't save transcript:", e)

if __name__ == "__main__":
    run_chat()
