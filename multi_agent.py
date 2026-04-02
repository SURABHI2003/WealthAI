import os
import re
import asyncio
import yfinance as yf
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

# -----------------------------
# TOP NSE STOCKS
# -----------------------------
TOP_NSE_STOCKS = [
    "RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS",
    "SBIN.NS","TATAMOTORS.NS","WIPRO.NS","HCLTECH.NS","AXISBANK.NS",
    "LT.NS","ITC.NS","BHARTIARTL.NS","KOTAKBANK.NS","BAJFINANCE.NS",
    "MARUTI.NS","SUNPHARMA.NS","ONGC.NS","TECHM.NS","POWERGRID.NS"
]

# -----------------------------
# FETCH DATA FROM YAHOO FINANCE
# -----------------------------
def get_stock_data(ticker: str):
    """Fetch stock information from Yahoo Finance"""

    try:
        stock = yf.Ticker(ticker)

        hist = stock.history(period="1d")
        price = hist["Close"].iloc[-1] if not hist.empty else None

        info = stock.info

        return {
            "ticker": ticker,
            "price": price,
            "pe": info.get("trailingPE"),
            "market_cap": info.get("marketCap"),
            "sector": info.get("sector")
        }

    except Exception:
        return {
            "ticker": ticker,
            "price": None,
            "pe": None,
            "market_cap": None,
            "sector": None
        }


# -----------------------------
# STOCK SCORING LOGIC
# -----------------------------
def score_stock(stock):
    """Score stock using PE and Market Cap"""

    score = 0

    pe = stock.get("pe")
    market_cap = stock.get("market_cap")

    if pe and pe < 30:
        score += 2
    elif pe and pe < 50:
        score += 1

    if market_cap and market_cap > 50_000_000_000:
        score += 2
    elif market_cap and market_cap > 10_000_000_000:
        score += 1

    return score


# -----------------------------
# MAIN AGENT
# -----------------------------
async def run_agent(query: str):

    model = init_chat_model(
        model="gpt-5.4-nano",
        model_provider="openai",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.85
    )

    classifier_model = init_chat_model(
        model="gpt-5.4-nano",
        model_provider="openai",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.85
    )

    # -----------------------------
    # STEP 1: INTENT CLASSIFICATION
    # -----------------------------
    intent_prompt = f"""
You are an intent classifier for a finance assistant.

Classify the user query into ONE of these labels:

STOCK_RECOMMENDATION
FINANCE_QUESTION
NON_FINANCE

Definitions:

STOCK_RECOMMENDATION:
User wants stock suggestions or investment picks.

FINANCE_QUESTION:
User is asking about personal finance, investing,
salary planning, savings, taxes, PF, SIP, etc.

NON_FINANCE:
Anything unrelated to finance.

Examples:

"Give me 3 best stocks" -> STOCK_RECOMMENDATION
"Suggest good Indian stocks" -> STOCK_RECOMMENDATION
"Which stocks should I buy?" -> STOCK_RECOMMENDATION
"How should I invest as a beginner?" -> FINANCE_QUESTION
"I got my first salary what should I do?" -> FINANCE_QUESTION
"What is SIP?" -> FINANCE_QUESTION
"What is PF?" -> FINANCE_QUESTION
"What is the capital of France?" -> NON_FINANCE
"Tell me a joke" -> NON_FINANCE

User Query:
{query}

Return ONLY the label.
"""

    intent = classifier_model.invoke(intent_prompt).content.strip()

    # -----------------------------
    # NON FINANCE
    # -----------------------------
    if intent == "NON_FINANCE":

        return """
I'm designed to answer **finance-related questions only**.

Try asking things like:

• Give me 3 good Indian stocks  
• How should I diversify my portfolio?  
• Explain PE ratio  
• What is SIP?  
• What is PF?  

Please ask a question related to **finance or investing**.
"""

    # -----------------------------
    # GENERAL FINANCE QUESTION
    # -----------------------------
    if intent == "FINANCE_QUESTION":

        response = model.invoke(f"""
You are a helpful financial advisor.

Answer the question clearly and practically.

Keep the advice structured and easy to read.

Give the response in points and sub points if needed.
                                
Don't ask any follow up questions. Just answer the user's question as best as you can.

Question:
{query}
""")

        return response.content


    # -----------------------------
    # STOCK RECOMMENDATION
    # -----------------------------
    match = re.search(r"\b(\d+)\b", query)
    count = int(match.group(1)) if match else 3
    count = min(count, len(TOP_NSE_STOCKS))

    all_stock_data = []

    for ticker in TOP_NSE_STOCKS:
        data = get_stock_data(ticker)
        data["score"] = score_stock(data)
        all_stock_data.append(data)

    all_stock_data = sorted(
        all_stock_data,
        key=lambda x: x["score"],
        reverse=True
    )

    selected_stocks = all_stock_data[:count]

    recommender_prompt = f"""
You are a professional financial analyst.

You have REAL stock data from Yahoo Finance.

Analyze the stocks below and give EXACTLY {count} recommendations.

Stock Data:
{selected_stocks}

FORMAT STRICTLY:

Stock Name: <ticker>
Price: <number>
PE Ratio: <number>
Market Cap: <number>
Sector: <sector>
Recommendation: Buy/Sell/Hold
Reason: <short explanation>
Risks: <short explanation>

Rules:
- Only analyze the stocks provided
- Do NOT say "as of my last update"
- Do NOT say you cannot access real-time data
- Keep explanations concise
- Separate each stock with ONE blank line
"""

    result = model.invoke(recommender_prompt)

    return result.content


# -----------------------------
# SYNC WRAPPER
# -----------------------------
def run_agent_sync(query):
    return asyncio.run(run_agent(query))