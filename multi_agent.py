# import os
# import asyncio
# from dotenv import load_dotenv
# from langchain_mcp_adapters.client import MultiServerMCPClient
# from langchain.chat_models import init_chat_model
# from langchain_core.tools.structured import StructuredTool
# from langgraph.prebuilt import create_react_agent
# from langgraph_supervisor import create_supervisor

# load_dotenv()

# from langchain_core.messages import convert_to_messages


# def wrap_structured_tool(tool: StructuredTool) -> StructuredTool:
#     if tool.func is not None:
#         return tool

#     async def async_wrapper(**kwargs):
#         return await tool.ainvoke(kwargs)

#     return StructuredTool.from_function(
#         func=lambda **kwargs: asyncio.run(async_wrapper(**kwargs)),
#         name=tool.name,
#         description=tool.description,
#         args_schema=tool.args_schema,
#         response_format=tool.response_format,
#     )


# def pretty_print_message(message, indent=False):
#     pretty_message = message.pretty_repr(html=True)
#     if not indent:
#         print(pretty_message)
#         return

#     indented = "\n".join("\t" + c for c in pretty_message.split("\n"))
#     print(indented)


# def pretty_print_messages(update, last_message=False):
#     is_subgraph = False
#     if isinstance(update, tuple):
#         ns, update = update
#         # skip parent graph updates in the printouts
#         if len(ns) == 0:
#             return

#         graph_id = ns[-1].split(":")[0]
#         print(f"Update from subgraph {graph_id}:")
#         print("\n")
#         is_subgraph = True

#     for node_name, node_update in update.items():
#         update_label = f"Update from node {node_name}:"
#         if is_subgraph:
#             update_label = "\t" + update_label

#         print(update_label)
#         print("\n")

#         messages = convert_to_messages(node_update["messages"])
#         if last_message:
#             messages = messages[-1:]

#         for m in messages:
#             pretty_print_message(m, indent=is_subgraph)
#         print("\n")


# async def run_agent(query):
#     client = MultiServerMCPClient(
#         {
#             "bright_data": {
#                 "command": "npx",
#                 "args": ["@brightdata/mcp"],
#                 "env": {
#                     "API_TOKEN": os.getenv("API_TOKEN") or os.getenv("BRIGHT_DATA_API_TOKEN")
#                 },
#                 "transport": "stdio",
#             },
#         }
#     )
#     tools = await client.get_tools()
#     tools = [wrap_structured_tool(tool) for tool in tools]
#     openai_key = os.getenv("OPENAI_API_KEY")
#     if openai_key:
#         model = init_chat_model(
#             model="gpt-4o-mini",
#             model_provider="openai",
#             api_key=openai_key,
#         )
#     else:
#         model = init_chat_model(
#             model="anthropic/claude-3-sonnet-20240229",
#             model_provider="anthropic",
#             api_key=os.getenv("ANTHROPIC_API_KEY"),
#         )

#     stock_finder_agent = create_react_agent(
#         model,
#         tools,
#         prompt="""You are a stock research analyst specializing in the Indian Stock Market (NSE). Your task is to select 2 promising, actively traded NSE-listed stocks for short term trading (buy/sell) based on recent performance, news buzz, volume or technical strength.
# Avoid penny stocks and illiquid companies.
# Output should include stock names, tickers, and brief reasoning for each choice.
# Respond in structured plain text format.""",
#         version="v1",
#         name="stock_finder_agent",
#     )

#     market_data_agent = create_react_agent(
#         model,
#         tools,
#         prompt="""You are a market data analyst for Indian stocks listed on NSE. Given a list of stock tickers (eg RELIANCE, INFY), your task is to gather recent market information for each stock, including:
# - Current price
# - Previous closing price
# - Today's volume
# - 7-day and 30-day price trend
# - Basic Technical indicators (RSI, 50/200-day moving averages)
# - Any notable spikes in volume or volatility

# Return your findings in a structured and readable format for each stock, suitable for further analysis by a recommendation engine. Use INR as the currency. Be concise but complete.""",
#         version="v1",
#         name="market_data_agent",
#     )

#     news_analyst_agent = create_react_agent(
#         model,
#         tools,
#         prompt="""You are a financial news analyst. Given the names or the tickers of Indian NSE listed stocks, your job is to:
# - Search for the most recent news articles (past 3-5 days)
# - Summarize key updates, announcements, and events for each stock
# - Classify each piece of news as positive, negative or neutral
# - Highlight how the news might affect short term stock price

# Present your response in a clear, structured format - one section per stock.

# Use bullet points where necessary. Keep it short, factual and analysis-oriented.""",
#         version="v1",
#         name="news_analyst_agent",
#     )

#     price_recommender_agent = create_react_agent(
#         model,
#         tools,
#         prompt="""You are a trading strategy advisor for the Indian Stock Market. You are given:
# - Recent market data (current price, volume, trend, indicators)
# - News summaries and sentiment for each stock

# Based on this info, for each stock:
# 1. Recommend an action: Buy, Sell or Hold
# 2. Suggest a specific target price for entry or exit (INR)
# 3. Briefly explain the reason behind your recommendation.

# Your goal is to provide practical, near-term trading advice for the next trading day.

# Keep the response concise and clearly structured.""",
#         version="v1",
#         name="price_recommender_agent",
#     )

#     openai_key = os.getenv("OPENAI_API_KEY")
#     supervisor_model = init_chat_model(
#         model="gpt-4o-mini" if openai_key else "anthropic/claude-3-sonnet-20240229",
#         model_provider="openai" if openai_key else "anthropic",
#         api_key=openai_key if openai_key else os.getenv("ANTHROPIC_API_KEY"),
#     )

#     supervisor = create_supervisor(
#         model=supervisor_model,
#         agents=[
#             stock_finder_agent,
#             market_data_agent,
#             news_analyst_agent,
#             price_recommender_agent,
#         ],
#         prompt=(
#             "You are a supervisor managing four agents:\n"
#             "- a stock_finder_agent. Assign research-related tasks to this agent and pick 2 promising NSE stocks\n"
#             "- a market_data_agent. Assign tasks to fetch current market data (price, volume, trends)\n"
#             "- a news_analyst_agent. Assign task to search and summarize recent news\n"
#             "- a price_recommender_agent. Assign task to give buy/sell decision with target price.\n"
#             "Assign work to one agent at a time, do not call agents in parallel.\n"
#             "Do not do any work yourself.\n"
#             "Make sure you complete till end and do not ask for proceed in between the task."
#         ),
#         add_handoff_back_messages=True,
#         output_mode="full_history",
#     ).compile()

#     # Capture the conversation and final result
#     conversation_log = []
#     final_chunk = None

#     for chunk in supervisor.stream(
#         {
#             "messages": [
#                 {
#                     "role": "user",
#                     "content": query,
#                 }
#             ]
#         },
#     ):
#         conversation_log.append(chunk)
#         final_chunk = chunk
#         # Only print for debugging, don't rely on prints for UI
#         # pretty_print_messages(chunk, last_message=True)

#     # Extract the final response from the last message
#     if final_chunk and "supervisor" in final_chunk:
#         final_messages = final_chunk["supervisor"]["messages"]
#         if final_messages:
#             # Get the last message content
#             last_message = final_messages[-1]
#             if hasattr(last_message, 'content'):
#                 return last_message.content
#             elif isinstance(last_message, dict) and 'content' in last_message:
#                 return last_message['content']

#     # Fallback: return a summary of the conversation
#     return "Analysis completed. Please check the logs for detailed results."


# if __name__ == "__main__":
#     asyncio.run(run_agent("Give me good stock recommendation from NSE"))



# multi_agent.py

# import asyncio


# async def run_agent(query):
#     """
#     Simulated multi-agent stock recommendation system
#     """

#     agents_workflow = [
#         "🔍 Stock Finder Agent: Analyzing NSE stocks...",
#         "📊 Market Data Agent: Gathering price and volume data...",
#         "📰 News Analyst Agent: Scanning recent news and sentiment...",
#         "💡 Price Recommender Agent: Generating buy/sell recommendations..."
#     ]

#     results = []

#     for step in agents_workflow:
#         results.append(step)
#         await asyncio.sleep(1)  # simulate delay

#     # sample response (replace later with real agents if needed)
#     sample_stocks = [
#         {
#             "name": "Reliance Industries Ltd",
#             "ticker": "RELIANCE",
#             "current_price": "₹2,847.50",
#             "recommendation": "BUY",
#             "target_price": "₹3,100",
#             "reason": "Strong quarterly results and expansion in digital services"
#         },
#         {
#             "name": "Infosys Ltd",
#             "ticker": "INFY",
#             "current_price": "₹1,789.25",
#             "recommendation": "HOLD",
#             "target_price": "₹1,850",
#             "reason": "Stable IT sector performance with moderate growth prospects"
#         }
#     ]

#     output = "\n".join(results) + "\n\n"
#     output += "📈 STOCK RECOMMENDATIONS:\n"
#     output += "=" * 50 + "\n\n"

#     for i, stock in enumerate(sample_stocks, 1):
#         output += f"{i}. {stock['name']} ({stock['ticker']})\n"
#         output += f"Current Price: {stock['current_price']}\n"
#         output += f"Recommendation: {stock['recommendation']}\n"
#         output += f"Target Price: {stock['target_price']}\n"
#         output += f"Reason: {stock['reason']}\n\n"

#     output += "⚠️ Disclaimer: Demo system only.\n"

#     return output


# # ✅ sync wrapper for Flask
# def run_agent_sync(query):
#     return asyncio.run(run_agent(query))


# multi_agent.py


# v1 ------------------------------------------------------

# import os
# import asyncio
# from dotenv import load_dotenv

# from langchain.chat_models import init_chat_model
# from langchain.agents import create_agent
# from langgraph_supervisor import create_supervisor

# load_dotenv()


# # -----------------------------
# # ✅ HELPER: INTENT CHECK
# # -----------------------------
# def is_stock_query(query: str) -> bool:
#     keywords = [
#         "stock", "stocks", "share", "market",
#         "trading", "invest", "nse", "sensex",
#         "price", "buy", "sell"
#     ]
#     return any(word in query.lower() for word in keywords)


# # -----------------------------
# # ✅ MAIN ASYNC FUNCTION
# # -----------------------------
# async def run_agent(query):
#     print("🔥 RUNNING REAL AGENT:", query)

#     # -----------------------------
#     # ✅ HANDLE NON-STOCK INPUT
#     # -----------------------------
#     if not is_stock_query(query):
#         return "Hi! 👋 I specialize in Indian stock recommendations. Ask me about stocks, trading, or market insights."

#     openai_key = os.getenv("OPENAI_API_KEY")

#     model = init_chat_model(
#         model="gpt-4o-mini",
#         model_provider="openai",
#         api_key=openai_key,
#     )

#     tools = []

#     # -----------------------------
#     # ✅ AGENT 1: STOCK FINDER
#     # -----------------------------
#     stock_finder_agent = create_agent(
#         model,
#         tools,
#         system_prompt="""
# You are an expert NSE stock analyst.

# Task:
# - Pick EXACTLY 2 strong Indian stocks for short-term trading
# - Avoid penny stocks
# - Use reasoning and market knowledge
# - ONLY respond if the query is about stocks
# - ALWAYS give final answer
# """,
#         name="stock_finder_agent",
#     )

#     # -----------------------------
#     # ✅ AGENT 2: RECOMMENDER
#     # -----------------------------
#     recommender_agent = create_agent(
#         model,
#         tools,
#         system_prompt="""
# You are a trading advisor.

# For EACH stock:
# - Give Buy / Sell / Hold
# - Give target price (approximate INR)
# - Give short reasoning

# ONLY respond if stocks are provided.
# ALWAYS give final recommendation.
# """,
#         name="recommender_agent",
#     )

#     # -----------------------------
#     # ✅ SUPERVISOR
#     # -----------------------------
#     supervisor = create_supervisor(
#         model=model,
#         agents=[stock_finder_agent, recommender_agent],
#         prompt="""
# You are a supervisor.

# Steps:
# 1. Call stock_finder_agent
# 2. Then call recommender_agent

# Rules:
# - ONLY proceed if the user query is about stocks/trading
# - If not, return a normal friendly response and DO NOT call agents
# - NEVER stop early
# - NEVER ask user questions
# - ALWAYS produce final output
# """,
#         output_mode="full_history",
#     ).compile()

#     # -----------------------------
#     # ✅ RUN PIPELINE
#     # -----------------------------
#     result = supervisor.invoke(
#         {
#             "messages": [
#                 {"role": "user", "content": query}
#             ]
#         }
#     )

#     # -----------------------------
#     # ✅ RETURN FINAL CLEAN OUTPUT
#     # -----------------------------
#     try:
#         messages = result.get("messages", [])

#         # 🔥 Pick LAST meaningful AI response
#         for msg in reversed(messages):
#             if hasattr(msg, "content") and msg.content.strip():
#                 return msg.content

#         return "No valid output generated."

#     except Exception as e:
#         return f"Error extracting response: {str(e)}"


# # -----------------------------
# # ✅ SYNC WRAPPER (FOR FLASK)
# # -----------------------------
# def run_agent_sync(query):
#     return asyncio.run(run_agent(query))


# ------------------------------------------------------------


# # v2

# import os
# import asyncio
# import yfinance as yf
# from dotenv import load_dotenv

# from langchain.chat_models import init_chat_model
# from langchain.agents import create_agent
# from langgraph_supervisor import create_supervisor

# load_dotenv()

# # -----------------------------
# # 📊 STOCK DATA TOOL (FIXED)
# # -----------------------------
# def get_stock_data(ticker: str):
#     """
#     Fetch stock data for a given ticker using Yahoo Finance.

#     Args:
#         ticker (str): Stock ticker (e.g., RELIANCE.NS)

#     Returns:
#         str: Stock details including price, PE, market cap, and sector.
#     """
#     try:
#         stock = yf.Ticker(ticker)
#         info = stock.info

#         return f"""
# Stock: {ticker.upper()}
# Price: {info.get("currentPrice")}
# PE: {info.get("trailingPE")}
# MarketCap: {info.get("marketCap")}
# Sector: {info.get("sector")}
# """
#     except Exception:
#         return f"Error fetching {ticker}"


# # -----------------------------
# # 🚀 MAIN PIPELINE
# # -----------------------------
# async def run_agent(query: str):
#     model = init_chat_model(
#         model="gpt-4o",
#         model_provider="openai",
#         api_key=os.getenv("OPENAI_API_KEY"),
#         temperature=0.85
#     )

#     # 🧠 STOCK FINDER
#     stock_finder_agent = create_agent(
#         model,
#         [],
#         system_prompt="""
# Identify 2-3 Indian stocks.

# Return ONLY tickers like:
# RELIANCE.NS
# TCS.NS
# INFY.NS
# """,
#         name="stock_finder_agent"   # ✅ FIX
#     )

#     # 📊 DATA AGENT
#     data_agent = create_agent(
#         model,
#         [get_stock_data],
#         system_prompt="""
# Use the tool to fetch stock data.
# Return raw data only.
# """,
#         name="data_agent"   # ✅ FIX
#     )

#     # 🎯 FINAL RECOMMENDER
#     recommender_agent = create_agent(
#         model,
#         [],
#         system_prompt="""
# You are an investment advisor.

# STRICT FORMAT:

# Stock Name: <name>
# Recommendation: Buy/Sell/Hold
# Target: <number>
# Reason: <short line>
# Risks: <short line>

# No extra text.
# """,
#         name="recommender_agent"   # ✅ FIX
#     )

#     # 🧠 SUPERVISOR (FIXED)
#     supervisor = create_supervisor(
#         model=model,
#         agents=[stock_finder_agent, data_agent, recommender_agent],
#         prompt="""
# 1. Find stocks
# 2. Fetch data
# 3. Recommend

# Return ONLY final formatted answer.
# """,
#         output_mode="last_message"
#     ).compile(name="finance_supervisor")   # ✅ FIX

#     result = supervisor.invoke({
#         "messages": [{"role": "user", "content": query}]
#     })

#     return result["messages"][-1].content


# # -----------------------------
# # 🔁 SYNC WRAPPER
# # -----------------------------
# def run_agent_sync(query):
#     return asyncio.run(run_agent(query))

# -------------------------------------



# import os
# import re
# import asyncio
# import random
# import yfinance as yf
# from dotenv import load_dotenv

# from langchain.chat_models import init_chat_model
# from langchain.agents import create_agent
# from langgraph_supervisor import create_supervisor

# load_dotenv()

# # -----------------------------
# # ✅ VALID TOP NSE STOCKS
# # -----------------------------
# TOP_NSE_STOCKS = [
#     "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
#     "SBIN.NS", "TATAMOTORS.NS", "WIPRO.NS", "HCLTECH.NS", "AXISBANK.NS",
#     "LT.NS", "ITC.NS", "BHARTIARTL.NS", "KOTAKBANK.NS", "BAJFINANCE.NS",
#     "MARUTI.NS", "SUNPHARMA.NS", "ONGC.NS", "TECHM.NS", "POWERGRID.NS"
# ]

# # -----------------------------
# # 📊 STOCK DATA TOOL
# # -----------------------------
# def get_stock_data(ticker: str):
#     """
#     Fetch stock data for a given ticker using Yahoo Finance.
#     """
#     try:
#         stock = yf.Ticker(ticker)
#         hist = stock.history(period="1d")
#         price = hist["Close"].iloc[-1] if not hist.empty else None
#         info = stock.info

#         return f"""
# Stock: {ticker.upper()}
# Price: {price}
# PE: {info.get("trailingPE")}
# MarketCap: {info.get("marketCap")}
# Sector: {info.get("sector")}
# """
#     except Exception:
#         return f"Error fetching {ticker}"


# # -----------------------------
# # 🚀 MAIN PIPELINE
# # -----------------------------
# async def run_agent(query: str):
#     # Extract requested number of stocks (default 3)
#     match = re.search(r'\b(\d+)\b', query)
#     count = int(match.group(1)) if match else 3
#     count = min(count, len(TOP_NSE_STOCKS))  # cap at list length

#     model = init_chat_model(
#         model="gpt-4o-mini",
#         model_provider="openai",
#         api_key=os.getenv("OPENAI_API_KEY"),
#         temperature=0.2
#     )

#     # -----------------------------
#     # 🧠 STOCK SELECTOR
#     # -----------------------------
#     stock_finder_agent = create_agent(
#         model,
#         [],
#         system_prompt=f"""
# User wants EXACTLY {count} top Indian stocks.
# You can ONLY pick from this list:

# {', '.join(TOP_NSE_STOCKS)}

# Return EXACTLY {count} tickers, one per line, no explanation.
# """,
#         name="stock_finder_agent"
#     )

#     # -----------------------------
#     # 📊 DATA AGENT
#     # -----------------------------
#     data_agent = create_agent(
#         model,
#         [get_stock_data],
#         system_prompt="Use the tool to fetch stock data for each ticker.",
#         name="data_agent"
#     )

#     # -----------------------------
#     # 🎯 RECOMMENDER AGENT
#     # -----------------------------
#     recommender_agent = create_agent(
#         model,
#         [],
#         system_prompt=f"""
# You are a professional investment advisor.
# Return EXACTLY {count} stocks in this format:

# Stock Name: <name>
# Recommendation: Buy/Sell/Hold
# Target: <number>
# Reason: <short line>
# Risks: <short line>

# Separate each stock with ONE blank line.
# No extra explanation.
# """,
#         name="recommender_agent"
#     )

#     # -----------------------------
#     # 🧠 SUPERVISOR
#     # -----------------------------
#     supervisor = create_supervisor(
#         model=model,
#         agents=[stock_finder_agent, data_agent, recommender_agent],
#         prompt=f"""
# User asked for {count} stocks.

# Steps:
# 1. Select EXACTLY {count} stocks from top NSE list
# 2. Fetch stock data
# 3. Provide structured recommendations

# Return ONLY final formatted output.
# """,
#         output_mode="last_message"
#     ).compile(name="finance_supervisor")

#     result = supervisor.invoke({
#         "messages": [{"role": "user", "content": query}]
#     })

#     final_output = result["messages"][-1].content

#     # Safety check
#     actual_count = final_output.count("Stock Name:")
#     if actual_count != count:
#         return f"Error: Expected {count} stocks but got {actual_count}. Please try again."

#     return final_output


# # -----------------------------
# # 🔁 SYNC WRAPPER
# # -----------------------------
# def run_agent_sync(query):
#     return asyncio.run(run_agent(query))

# ------------------------------------------------------
# new version

# import os
# import re
# import asyncio
# import yfinance as yf
# from dotenv import load_dotenv
# from langchain.chat_models import init_chat_model
# from langchain.agents import create_agent

# load_dotenv()

# # -----------------------------
# # ✅ VALID TOP NSE STOCKS
# # -----------------------------
# TOP_NSE_STOCKS = [
#     "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
#     "SBIN.NS", "TATAMOTORS.NS", "WIPRO.NS", "HCLTECH.NS", "AXISBANK.NS",
#     "LT.NS", "ITC.NS", "BHARTIARTL.NS", "KOTAKBANK.NS", "BAJFINANCE.NS",
#     "MARUTI.NS", "SUNPHARMA.NS", "ONGC.NS", "TECHM.NS", "POWERGRID.NS"
# ]

# # -----------------------------
# # 📊 STOCK DATA TOOL
# # -----------------------------
# def get_stock_data(ticker: str):
#     """
#     Fetch stock data for a given ticker using Yahoo Finance.
#     Returns formatted string with price, PE, MarketCap, and sector.
#     """
#     try:
#         stock = yf.Ticker(ticker)
#         hist = stock.history(period="1d")
#         price = hist["Close"].iloc[-1] if not hist.empty else "N/A"
#         info = stock.info

#         return f"""
# Stock: {ticker.upper()}
# Price: ₹{price}
# PE: {info.get("trailingPE", 'N/A')}
# MarketCap: ₹{info.get("marketCap", 'N/A')}
# Sector: {info.get("sector", 'N/A')}
# """
#     except Exception:
#         return f"Error fetching data for {ticker}"

# # -----------------------------
# # 🚀 MAIN PIPELINE
# # -----------------------------
# async def run_agent(query: str):
#     # Extract requested number of stocks (default 3)
#     match = re.search(r'\b(\d+)\b', query)
#     count = int(match.group(1)) if match else 3
#     count = min(count, len(TOP_NSE_STOCKS))

#     # ✅ Pick top N stocks directly
#     selected_tickers = TOP_NSE_STOCKS[:count]

#     # Fetch stock data
#     stock_data_list = [get_stock_data(t) for t in selected_tickers]

#     # Initialize LLM for recommendations
#     model = init_chat_model(
#         model="gpt-4o",
#         model_provider="openai",
#         api_key=os.getenv("OPENAI_API_KEY"),
#         temperature=0.85
#     )

#     # -----------------------------
#     # 🎯 RECOMMENDER AGENT
#     # -----------------------------
#     recommender_agent = create_agent(
#         model,
#         [],
#         system_prompt=f"""
# You are a professional investment advisor.
# Return EXACTLY {count} stocks in this format:

# Stock Name: <name>
# Recommendation: Buy/Sell/Hold
# Target Price: <number>
# PE Ratio: <number>
# Market Cap: <number>
# Reason: <short line>
# Risks: <short line>

# Use this stock data:

# {chr(10).join(stock_data_list)}

# Separate each stock with ONE blank line.
# No extra explanation.
# """,
#         name="recommender_agent"
#     )

#     # Invoke recommender
#     result = recommender_agent.invoke({"messages": [{"role": "user", "content": query}]})
#     final_output = result["messages"][-1].content

#     # Safety check
#     actual_count = final_output.count("Stock Name:")
#     if actual_count != count:
#         return f"Error: Expected {count} stocks but got {actual_count}. Please try again."

#     return final_output

# # -----------------------------
# # 🔁 SYNC WRAPPER
# # -----------------------------
# def run_agent_sync(query):
#     return asyncio.run(run_agent(query))

# ----------------------------------------------------
# version new

# import os
# import asyncio
# import random
# import yfinance as yf
# from dotenv import load_dotenv

# from langchain.chat_models import init_chat_model
# from langchain.agents import create_agent

# load_dotenv()

# # -----------------------------
# # ✅ VALID TOP NSE STOCKS
# # -----------------------------
# TOP_NSE_STOCKS = [
#     "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
#     "SBIN.NS", "TATAMOTORS.NS", "WIPRO.NS", "HCLTECH.NS", "AXISBANK.NS",
#     "LT.NS", "ITC.NS", "BHARTIARTL.NS", "KOTAKBANK.NS", "BAJFINANCE.NS",
#     "MARUTI.NS", "SUNPHARMA.NS", "ONGC.NS", "TECHM.NS", "POWERGRID.NS"
# ]

# # -----------------------------
# # 📊 STOCK DATA TOOL
# # -----------------------------
# def get_stock_data(ticker: str):
#     """
#     Fetch stock data for a given ticker using Yahoo Finance.
#     Returns formatted dict with price, PE, MarketCap, Sector.
#     """
#     try:
#         stock = yf.Ticker(ticker)

#         # Latest price
#         hist = stock.history(period="1d")
#         price = hist["Close"].iloc[-1] if not hist.empty else "N/A"

#         # Fast info for Market Cap
#         fast = getattr(stock, "fast_info", {})
#         market_cap = fast.get("market_cap", "N/A")

#         # Fallback info for PE and Sector
#         info = getattr(stock, "info", {})
#         pe = info.get("trailingPE", "N/A")
#         sector = info.get("sector", "N/A")

#         return {
#             "ticker": ticker,
#             "price": price,
#             "pe": pe,
#             "market_cap": market_cap,
#             "sector": sector
#         }

#     except Exception:
#         return {
#             "ticker": ticker,
#             "price": "N/A",
#             "pe": "N/A",
#             "market_cap": "N/A",
#             "sector": "N/A"
#         }

# # -----------------------------
# # 🚀 MAIN PIPELINE
# # -----------------------------
# async def run_agent(query: str):
#     # Extract requested number of stocks (default 3)
#     import re
#     match = re.search(r'\b(\d+)\b', query)
#     count = int(match.group(1)) if match else 3
#     count = min(count, len(TOP_NSE_STOCKS))

#     # Step 1: Pick N tickers
#     selected_tickers = random.sample(TOP_NSE_STOCKS, count)

#     # Step 2: Fetch stock data
#     stock_data_list = [get_stock_data(t) for t in selected_tickers]

#     # Step 3: Initialize LLM for recommendations
#     model = init_chat_model(
#         model="gpt-4o",
#         model_provider="openai",
#         api_key=os.getenv("OPENAI_API_KEY"),
#         temperature=0.85
#     )

#     # Step 4: Create recommender agent
#     recommender_agent = create_agent(
#         model,
#         [],
#         system_prompt=f"""
# You are a professional investment advisor.
# For each stock provided, analyze the data and give a recommendation (Buy/Sell/Hold),
# Target Price, Reason, and Risks. Include the Price, PE, MarketCap, and Sector in your output.
# Output format for EACH stock:

# Stock Name: <name>
# Price: <price>
# PE: <pe>
# MarketCap: <market_cap>
# Sector: <sector>
# Recommendation: <Buy/Sell/Hold>
# Target: <number>
# Reason: <short line>
# Risks: <short line>

# Separate each stock with ONE blank line. Do NOT add extra explanations.
# """,
#         name="recommender_agent"
#     )

#     # Step 5: Generate recommendation for all stocks in one go
#     stock_messages = "\n\n".join([
#         f"{s['ticker']}\nPrice: {s['price']}\nPE: {s['pe']}\nMarketCap: {s['market_cap']}\nSector: {s['sector']}"
#         for s in stock_data_list
#     ])

#     result = recommender_agent.invoke({
#         "messages": [{"role": "user", "content": f"Analyze these stocks:\n\n{stock_messages}"}]
#     })

#     final_output = result["messages"][-1].content

#     return final_output

# # -----------------------------
# # 🔁 SYNC WRAPPER
# # -----------------------------
# def run_agent_sync(query):
#     return asyncio.run(run_agent(query))

# ------------------------------------------------------------------------
# new version

# import os
# import asyncio
# import random
# import yfinance as yf
# from dotenv import load_dotenv

# from langchain.chat_models import init_chat_model
# from langchain.agents import create_agent
# from langgraph_supervisor import create_supervisor

# load_dotenv()

# # -----------------------------
# # ✅ VALID TOP NSE STOCKS
# # -----------------------------
# TOP_NSE_STOCKS = [
#     "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
#     "SBIN.NS", "TATAMOTORS.NS", "WIPRO.NS", "HCLTECH.NS", "AXISBANK.NS",
#     "LT.NS", "ITC.NS", "BHARTIARTL.NS", "KOTAKBANK.NS", "BAJFINANCE.NS",
#     "MARUTI.NS", "SUNPHARMA.NS", "ONGC.NS", "TECHM.NS", "POWERGRID.NS"
# ]

# # -----------------------------
# # 🧠 STOCK SELECTOR (FIXED)
# # -----------------------------
# def select_stocks(count: int):
#     """
#     Randomly pick exactly `count` tickers from TOP_NSE_STOCKS.
#     """
#     return random.sample(TOP_NSE_STOCKS, count)

# # -----------------------------
# # 📊 STOCK DATA TOOL
# # -----------------------------
# def get_stock_data(ticker: str):
#     """
#     Fetch stock data from Yahoo Finance and print raw info for debugging.
#     """
#     try:
#         stock = yf.Ticker(ticker)
#         hist = stock.history(period="1d")
#         info = stock.info
#         price = hist["Close"].iloc[-1] if not hist.empty else None

#         print(f"\n--- Raw Yahoo Data for {ticker} ---")
#         print("History:")
#         print(hist)
#         print("Fast Info:")
#         print(stock.fast_info)
#         print("Info:")
#         print(info)
#         print("--- End Raw Data ---\n")

#         return {
#             "ticker": ticker,
#             "price": price,
#             "pe": info.get("trailingPE"),
#             "market_cap": info.get("marketCap"),
#             "sector": info.get("sector")
#         }

#     except Exception as e:
#         print(f"Error fetching {ticker}: {e}")
#         return {"ticker": ticker, "error": str(e)}

# # -----------------------------
# # 🚀 MAIN PIPELINE
# # -----------------------------
# async def run_agent(query: str):
#     # Extract requested number of stocks (default 3)
#     import re
#     match = re.search(r'\b(\d+)\b', query)
#     count = int(match.group(1)) if match else 3
#     count = min(count, len(TOP_NSE_STOCKS))

#     # -----------------------------
#     # 🌟 Pick stocks directly
#     # -----------------------------
#     selected_stocks = select_stocks(count)
#     print(f"Selected tickers: {selected_stocks}")

#     # -----------------------------
#     # 🧠 Initialize LLM
#     # -----------------------------
#     model = init_chat_model(
#         model="gpt-4o-mini",
#         model_provider="openai",
#         api_key=os.getenv("OPENAI_API_KEY"),
#         temperature=0.5
#     )

#     # -----------------------------
#     # 📊 DATA AGENT
#     # -----------------------------
#     stock_data_list = [get_stock_data(t) for t in selected_stocks]

#     # -----------------------------
#     # 🎯 RECOMMENDER AGENT
#     # -----------------------------
#     recommender_agent = create_agent(
#         model,
#         [],
#         system_prompt=f"""
# You are a professional investment advisor.

# Given the following stock data:
# - Include Price, PE, MarketCap, Sector in your reasoning.
# - For each stock, return EXACTLY this format:

# Stock Name: <ticker>
# Recommendation: Buy/Sell/Hold
# Target: <number>
# Reason: <short line>
# Risks: <short line>

# Separate each stock with ONE blank line. No extra explanation.
# """,
#         name="recommender_agent"
#     )

#     # Prepare the input content for recommender
#     stock_info_text = ""
#     for sd in stock_data_list:
#         if "error" in sd:
#             stock_info_text += f"{sd['ticker']}: Error fetching data: {sd['error']}\n\n"
#         else:
#             stock_info_text += (
#                 f"{sd['ticker']}:\n"
#                 f"Price: {sd['price']}\n"
#                 f"PE: {sd['pe']}\n"
#                 f"MarketCap: {sd['market_cap']}\n"
#                 f"Sector: {sd['sector']}\n\n"
#             )

#     # -----------------------------
#     # 🧠 SUPERVISOR
#     # -----------------------------
#     supervisor = create_supervisor(
#         model=model,
#         agents=[recommender_agent],
#         prompt=f"""
# User asked for {count} best Indian stocks.
# Stock data provided below:

# {stock_info_text}

# Provide structured recommendations as per agent's instructions.
# Return ONLY final formatted output.
# """,
#         output_mode="last_message"
#     ).compile(name="finance_supervisor")

#     result = supervisor.invoke({
#         "messages": [{"role": "user", "content": query}]
#     })

#     final_output = result["messages"][-1].content

#     return final_output

# # -----------------------------
# # 🔁 SYNC WRAPPER
# # -----------------------------
# def run_agent_sync(query):
#     return asyncio.run(run_agent(query))


# ----------------------------------------------------------
# version


# import os
# import asyncio
# import random
# import yfinance as yf
# from dotenv import load_dotenv

# from langchain.chat_models import init_chat_model
# from langchain.agents import create_agent
# from langgraph_supervisor import create_supervisor

# load_dotenv()

# # -----------------------------
# # ✅ VALID TOP NSE STOCKS
# # -----------------------------
# TOP_NSE_STOCKS = [
#     "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
#     "SBIN.NS", "TATAMOTORS.NS", "WIPRO.NS", "HCLTECH.NS", "AXISBANK.NS",
#     "LT.NS", "ITC.NS", "BHARTIARTL.NS", "KOTAKBANK.NS", "BAJFINANCE.NS",
#     "MARUTI.NS", "SUNPHARMA.NS", "ONGC.NS", "TECHM.NS", "POWERGRID.NS"
# ]

# # -----------------------------
# # 🧠 STOCK SELECTOR (FIXED)
# # -----------------------------
# def select_stocks(count: int):
#     """
#     Randomly pick exactly `count` tickers from TOP_NSE_STOCKS.
#     """
#     return random.sample(TOP_NSE_STOCKS, count)

# # -----------------------------
# # 📊 STOCK DATA TOOL
# # -----------------------------
# def get_stock_data(ticker: str):
#     """
#     Fetch stock data from Yahoo Finance and print raw info for debugging.
#     """
#     try:
#         stock = yf.Ticker(ticker)
#         hist = stock.history(period="1d")
#         info = stock.info
#         price = hist["Close"].iloc[-1] if not hist.empty else None

#         print(f"\n--- Raw Yahoo Data for {ticker} ---")
#         print("History:")
#         print(hist)
#         print("Fast Info:")
#         print(stock.fast_info)
#         print("Info:")
#         print(info)
#         print("--- End Raw Data ---\n")

#         return {
#             "ticker": ticker,
#             "price": price,
#             "pe": info.get("trailingPE"),
#             "market_cap": info.get("marketCap"),
#             "sector": info.get("sector")
#         }

#     except Exception as e:
#         print(f"Error fetching {ticker}: {e}")
#         return {"ticker": ticker, "error": str(e)}

# # -----------------------------
# # 🚀 MAIN PIPELINE
# # -----------------------------
# async def run_agent(query: str):
#     # Extract requested number of stocks (default 3)
#     import re
#     match = re.search(r'\b(\d+)\b', query)
#     count = int(match.group(1)) if match else 3
#     count = min(count, len(TOP_NSE_STOCKS))

#     # -----------------------------
#     # 🌟 Pick stocks directly
#     # -----------------------------
#     selected_stocks = select_stocks(count)
#     print(f"Selected tickers: {selected_stocks}")

#     # -----------------------------
#     # 🧠 Initialize LLM
#     # -----------------------------
#     model = init_chat_model(
#         model="gpt-4o-mini",
#         model_provider="openai",
#         api_key=os.getenv("OPENAI_API_KEY"),
#         temperature=0.5
#     )

#     # -----------------------------
#     # 📊 DATA AGENT
#     # -----------------------------
#     stock_data_list = [get_stock_data(t) for t in selected_stocks]

#     # -----------------------------
#     # 🎯 RECOMMENDER AGENT
#     # -----------------------------
#     recommender_agent = create_agent(
#         model,
#         [],
#         system_prompt=f"""
# You are a professional investment advisor.

# Given the following stock data:
# - Include Price, PE, MarketCap, Sector in your reasoning.
# - For each stock, return EXACTLY this format:

# Stock Name: <ticker>
# Recommendation: Buy/Sell/Hold
# Target: <number>
# Reason: <short explanation>
# Risks: <short explanation>

# Separate each stock with ONE blank line. No extra explanation.
# """,
#         name="recommender_agent"
#     )

#     # Prepare the input content for recommender
#     stock_info_text = ""
#     for sd in stock_data_list:
#         if "error" in sd:
#             stock_info_text += f"{sd['ticker']}: Error fetching data: {sd['error']}\n\n"
#         else:
#             stock_info_text += (
#                 f"{sd['ticker']}:\n"
#                 f"Price: {sd['price']}\n"
#                 f"PE: {sd['pe']}\n"
#                 f"MarketCap: {sd['market_cap']}\n"
#                 f"Sector: {sd['sector']}\n\n"
#             )

#     # -----------------------------
#     # 🧠 SUPERVISOR
#     # -----------------------------
#     supervisor = create_supervisor(
#         model=model,
#         agents=[recommender_agent],
#         prompt=f"""
# User asked for {count} best Indian stocks.
# Stock data provided below:

# {stock_info_text}

# Provide structured recommendations as per agent's instructions.
# Return ONLY final formatted output.
# """,
#         output_mode="last_message"
#     ).compile(name="finance_supervisor")

#     result = supervisor.invoke({
#         "messages": [{"role": "user", "content": query}]
#     })

#     final_output = result["messages"][-1].content

#     return final_output

# # -----------------------------
# # 🔁 SYNC WRAPPER
# # -----------------------------
# def run_agent_sync(query):
#     return asyncio.run(run_agent(query))


# ---------------------------------------------------------------------
# version new


# import os
# import re
# import asyncio
# import random
# import yfinance as yf
# from dotenv import load_dotenv

# from langchain.chat_models import init_chat_model
# from langchain.agents import create_agent
# from langgraph_supervisor import create_supervisor

# load_dotenv()

# # -----------------------------
# # ✅ VALID TOP NSE STOCKS
# # -----------------------------
# TOP_NSE_STOCKS = [
#     "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
#     "SBIN.NS", "TATAMOTORS.NS", "WIPRO.NS", "HCLTECH.NS", "AXISBANK.NS",
#     "LT.NS", "ITC.NS", "BHARTIARTL.NS", "KOTAKBANK.NS", "BAJFINANCE.NS",
#     "MARUTI.NS", "SUNPHARMA.NS", "ONGC.NS", "TECHM.NS", "POWERGRID.NS"
# ]

# # -----------------------------
# # 📊 STOCK DATA TOOL
# # -----------------------------
# def get_stock_data(ticker: str):
#     """
#     Fetch stock data for a given ticker using Yahoo Finance.
#     Prints raw data for debugging.
#     """
#     try:
#         stock = yf.Ticker(ticker)
#         hist = stock.history(period="1d")
#         price = hist["Close"].iloc[-1] if not hist.empty else None
#         info = stock.info

#         # Print raw data to terminal
#         print(f"--- Raw Yahoo Data for {ticker} ---")
#         print(f"Price: {price}, PE: {info.get('trailingPE')}, "
#               f"MarketCap: {info.get('marketCap')}, Sector: {info.get('sector')}")
#         print("--- End Raw Data ---\n")

#         return {
#             "ticker": ticker,
#             "price": price,
#             "pe": info.get("trailingPE"),
#             "market_cap": info.get("marketCap"),
#             "sector": info.get("sector")
#         }
#     except Exception as e:
#         print(f"Error fetching {ticker}: {e}")
#         return {
#             "ticker": ticker,
#             "price": None,
#             "pe": None,
#             "market_cap": None,
#             "sector": None
#         }


# # -----------------------------
# # 🚀 MAIN PIPELINE
# # -----------------------------
# async def run_agent(query: str):
#     # Extract requested number of stocks (default 3)
#     match = re.search(r'\b(\d+)\b', query)
#     count = int(match.group(1)) if match else 3
#     count = min(count, len(TOP_NSE_STOCKS))  # cap at list length

#     model = init_chat_model(
#         model="gpt-4o-mini",
#         model_provider="openai",
#         api_key=os.getenv("OPENAI_API_KEY"),
#         temperature=0.2
#     )

#     # -----------------------------
#     # 🧠 STOCK SELECTOR
#     # -----------------------------
#     stock_finder_agent = create_agent(
#         model,
#         [],
#         system_prompt=f"""
# User wants EXACTLY {count} top Indian stocks.
# You can ONLY pick from this list:

# {', '.join(TOP_NSE_STOCKS)}

# Return EXACTLY {count} tickers, one per line, no explanation.
# """,
#         name="stock_finder_agent"
#     )

#     # -----------------------------
#     # 📊 DATA AGENT
#     # -----------------------------
#     data_agent = create_agent(
#         model,
#         [get_stock_data],
#         system_prompt="Use the tool to fetch stock data for each ticker.",
#         name="data_agent"
#     )

#     # -----------------------------
#     # 🎯 RECOMMENDER AGENT
#     # -----------------------------
#     recommender_agent = create_agent(
#         model,
#         [],
#         system_prompt=f"""
# You are a professional investment advisor.
# Return EXACTLY {count} stocks in this format:

# Stock Name: <name>
# Price: <number>
# PE Ratio: <number>
# Market Cap: <number>
# Sector: <sector>
# Recommendation: Buy/Sell/Hold
# Reason: <short line>
# Risks: <short line>

# Separate each stock with ONE blank line.
# No extra explanation.
# """,
#         name="recommender_agent"
#     )

#     # -----------------------------
#     # 🧠 SUPERVISOR
#     # -----------------------------
#     supervisor = create_supervisor(
#         model=model,
#         agents=[stock_finder_agent, data_agent, recommender_agent],
#         prompt=f"""
# User asked for {count} stocks.

# Steps:
# 1. Select EXACTLY {count} stocks from top NSE list
# 2. Fetch stock data
# 3. Provide structured recommendations

# Return ONLY final formatted output.
# """,
#         output_mode="last_message"
#     ).compile(name="finance_supervisor")

#     # Synchronous invocation
#     result = supervisor.invoke({
#         "messages": [{"role": "user", "content": query}]
#     })

#     # Safely extract final output
#     if "messages" in result and len(result["messages"]) > 0:
#         final_output = result["messages"][-1].content
#     else:
#         final_output = str(result)

#     # Return whatever the LLM generated
#     if not final_output.strip():
#         return "Error: LLM returned empty output. Please try again."

#     return final_output


# # -----------------------------
# # 🔁 SYNC WRAPPER
# # -----------------------------
# def run_agent_sync(query):
#     return asyncio.run(run_agent(query))


# ----------------------------------------------------------------------------------------------------
# best version



# import os
# import re
# import asyncio
# import yfinance as yf
# from dotenv import load_dotenv
# from langchain.chat_models import init_chat_model

# load_dotenv()

# # -----------------------------
# # TOP NSE STOCKS
# # -----------------------------
# TOP_NSE_STOCKS = [
#     "RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS",
#     "SBIN.NS","TATAMOTORS.NS","WIPRO.NS","HCLTECH.NS","AXISBANK.NS",
#     "LT.NS","ITC.NS","BHARTIARTL.NS","KOTAKBANK.NS","BAJFINANCE.NS",
#     "MARUTI.NS","SUNPHARMA.NS","ONGC.NS","TECHM.NS","POWERGRID.NS"
# ]

# # -----------------------------
# # STOCK DATA FETCHER
# # -----------------------------
# def get_stock_data(ticker: str):
#     """
#     Fetch stock data from Yahoo Finance
#     """
#     try:
#         stock = yf.Ticker(ticker)
#         hist = stock.history(period="1d")
#         price = hist["Close"].iloc[-1] if not hist.empty else None
#         info = stock.info

#         return {
#             "ticker": ticker,
#             "price": price,
#             "pe": info.get("trailingPE"),
#             "market_cap": info.get("marketCap"),
#             "sector": info.get("sector")
#         }

#     except Exception:
#         return {
#             "ticker": ticker,
#             "price": None,
#             "pe": None,
#             "market_cap": None,
#             "sector": None
#         }

# # -----------------------------
# # MAIN PIPELINE
# # -----------------------------
# async def run_agent(query: str):

#     # Extract number of stocks requested
#     match = re.search(r"\b(\d+)\b", query)
#     count = int(match.group(1)) if match else 3
#     count = min(count, len(TOP_NSE_STOCKS))

#     model = init_chat_model(
#         model="gpt-4o",
#         # model="gpt-5.4-mini",
#         model_provider="openai",
#         api_key=os.getenv("OPENAI_API_KEY"),
#         temperature=0.85
#     )

#     # -----------------------------
#     # STEP 1: SELECT STOCKS
#     # -----------------------------
#     selector_prompt = f"""
# User asked: {query}

# Select EXACTLY {count} tickers from this list:

# {', '.join(TOP_NSE_STOCKS)}

# Return ONLY tickers one per line.
# """

#     response = model.invoke(selector_prompt)
#     tickers = [t.strip() for t in response.content.split("\n") if t.strip()]

#     tickers = tickers[:count]

#     # -----------------------------
#     # STEP 2: FETCH DATA
#     # -----------------------------
#     stock_data = []

#     for ticker in tickers:
#         data = get_stock_data(ticker)
#         stock_data.append(data)

#     # -----------------------------
#     # STEP 3: GENERATE RECOMMENDATION
#     # -----------------------------
#     recommender_prompt = f"""
# You are a professional investment advisor.

# Analyze this stock data and provide recommendations.

# DATA:
# {stock_data}

# Return EXACTLY {count} stocks.

# FORMAT STRICTLY:

# Stock Name: <ticker>
# Price: <number>
# PE Ratio: <number>
# Market Cap: <number>
# Sector: <sector>
# Recommendation: Buy/Sell/Hold
# Reason: <short explanation>
# Risks: <short explanation>

# Separate stocks with ONE blank line.
# """

#     result = model.invoke(recommender_prompt)

#     return result.content


# # -----------------------------
# # SYNC WRAPPER
# # -----------------------------
# def run_agent_sync(query):
#     return asyncio.run(run_agent(query))

# -------------------------------------------------------------------------------------------------------
# most stable version having data from yahoo finance and proper stock scoring logic based on PE and Market Cap




# import os
# import re
# import asyncio
# import yfinance as yf
# from dotenv import load_dotenv
# from langchain.chat_models import init_chat_model

# load_dotenv()

# # -----------------------------
# # TOP NSE STOCKS
# # -----------------------------
# TOP_NSE_STOCKS = [
#     "RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS",
#     "SBIN.NS","TATAMOTORS.NS","WIPRO.NS","HCLTECH.NS","AXISBANK.NS",
#     "LT.NS","ITC.NS","BHARTIARTL.NS","KOTAKBANK.NS","BAJFINANCE.NS",
#     "MARUTI.NS","SUNPHARMA.NS","ONGC.NS","TECHM.NS","POWERGRID.NS"
# ]

# # -----------------------------
# # FETCH DATA FROM YAHOO FINANCE
# # -----------------------------
# def get_stock_data(ticker: str):
#     """Fetch stock information from Yahoo Finance"""

#     try:
#         stock = yf.Ticker(ticker)

#         hist = stock.history(period="1d")
#         price = hist["Close"].iloc[-1] if not hist.empty else None

#         info = stock.info

#         return {
#             "ticker": ticker,
#             "price": price,
#             "pe": info.get("trailingPE"),
#             "market_cap": info.get("marketCap"),
#             "sector": info.get("sector")
#         }

#     except Exception:
#         return {
#             "ticker": ticker,
#             "price": None,
#             "pe": None,
#             "market_cap": None,
#             "sector": None
#         }


# # -----------------------------
# # STOCK SCORING LOGIC
# # -----------------------------
# def score_stock(stock):
#     """Score stock using PE and Market Cap"""

#     score = 0

#     pe = stock.get("pe")
#     market_cap = stock.get("market_cap")

#     if pe and pe < 30:
#         score += 2
#     elif pe and pe < 50:
#         score += 1

#     if market_cap and market_cap > 50_000_000_000:
#         score += 2
#     elif market_cap and market_cap > 10_000_000_000:
#         score += 1

#     return score


# # -----------------------------
# # MAIN AGENT
# # -----------------------------
# async def run_agent(query: str):

#     model = init_chat_model(
#         model="gpt-4o",
#         model_provider="openai",
#         api_key=os.getenv("OPENAI_API_KEY"),
#         temperature=0.85
#     )

#     query_lower = query.lower()

#     # -----------------------------
#     # STEP 1: FINANCE FILTER
#     # -----------------------------
#     finance_keywords = [
#         "stock","stocks","invest","investment","portfolio",
#         "market","trading","finance","bank","mutual fund",
#         "sip","etf","crypto","economy","diversify",
#         "pe ratio","dividend","pf","provident fund",
#         "epf","fd","fixed deposit","ipo","equity",
#         "bond","interest","loan","inflation"
#     ]

#     if not any(word in query_lower for word in finance_keywords):

#         return """
# I'm designed to answer **finance-related questions only**.

# Try asking things like:

# • Give me 3 good Indian stocks  
# • How should I diversify my portfolio?  
# • Explain PE ratio  
# • What is SIP?  
# • What is PF?  

# Please ask a question related to **finance or investing**.
# """

#     # -----------------------------
#     # STEP 2: INTENT DETECTION
#     # -----------------------------
#     intent_prompt = f"""
# Classify the user's intent.

# Possible intents:
# STOCK_RECOMMENDATION
# FINANCE_QUESTION

# Examples:
# "Give me 3 best stocks" -> STOCK_RECOMMENDATION
# "Which stocks should I buy?" -> STOCK_RECOMMENDATION
# "Suggest good Indian stocks" -> STOCK_RECOMMENDATION
# "How should I invest as a beginner?" -> FINANCE_QUESTION
# "What is SIP?" -> FINANCE_QUESTION

# User query:
# {query}

# Return ONLY one label.
# """

#     intent = model.invoke(intent_prompt).content.strip()

#     # -----------------------------
#     # STEP 3: GENERAL FINANCE QUESTION
#     # -----------------------------
#     if intent == "FINANCE_QUESTION":

#         response = model.invoke(f"""
# You are a helpful financial advisor.

# Answer the following finance question clearly and simply.

# Question:
# {query}
# """)

#         return response.content


#     # -----------------------------
#     # STEP 4: NUMBER OF STOCKS
#     # -----------------------------
#     match = re.search(r"\b(\d+)\b", query)
#     count = int(match.group(1)) if match else 3
#     count = min(count, len(TOP_NSE_STOCKS))

#     # -----------------------------
#     # STEP 5: FETCH ALL STOCK DATA
#     # -----------------------------
#     all_stock_data = []

#     for ticker in TOP_NSE_STOCKS:
#         data = get_stock_data(ticker)
#         data["score"] = score_stock(data)
#         all_stock_data.append(data)

#     # -----------------------------
#     # STEP 6: SORT BY SCORE
#     # -----------------------------
#     all_stock_data = sorted(
#         all_stock_data,
#         key=lambda x: x["score"],
#         reverse=True
#     )

#     selected_stocks = all_stock_data[:count]

#     # -----------------------------
#     # STEP 7: GENERATE RECOMMENDATIONS
#     # -----------------------------
#     recommender_prompt = f"""
# You are a professional financial analyst.

# You have REAL stock data from Yahoo Finance.

# Analyze the stocks below and give EXACTLY {count} recommendations.

# Stock Data:
# {selected_stocks}

# FORMAT STRICTLY:

# Stock Name: <ticker>
# Price: <number>
# PE Ratio: <number>
# Market Cap: <number>
# Sector: <sector>
# Recommendation: Buy/Sell/Hold
# Reason: <short explanation>
# Risks: <short explanation>

# Rules:
# - Only analyze the stocks provided
# - Do NOT say "as of my last update"
# - Do NOT say you cannot access real-time data
# - Keep explanations concise

# Separate each stock with ONE blank line.
# """

#     result = model.invoke(recommender_prompt)

#     return result.content


# # -----------------------------
# # SYNC WRAPPER
# # -----------------------------
# def run_agent_sync(query):
#     return asyncio.run(run_agent(query))


# ---------------------------------------------------------------------------------------------
# good version




# import os
# import re
# import asyncio
# import yfinance as yf
# from dotenv import load_dotenv
# from langchain.chat_models import init_chat_model

# load_dotenv()

# # -----------------------------
# # TOP NSE STOCKS
# # -----------------------------
# TOP_NSE_STOCKS = [
#     "RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS",
#     "SBIN.NS","TATAMOTORS.NS","WIPRO.NS","HCLTECH.NS","AXISBANK.NS",
#     "LT.NS","ITC.NS","BHARTIARTL.NS","KOTAKBANK.NS","BAJFINANCE.NS",
#     "MARUTI.NS","SUNPHARMA.NS","ONGC.NS","TECHM.NS","POWERGRID.NS"
# ]

# # -----------------------------
# # FETCH DATA FROM YAHOO FINANCE
# # -----------------------------
# def get_stock_data(ticker: str):
#     """Fetch stock information from Yahoo Finance"""

#     try:
#         stock = yf.Ticker(ticker)

#         hist = stock.history(period="1d")
#         price = hist["Close"].iloc[-1] if not hist.empty else None

#         info = stock.info

#         return {
#             "ticker": ticker,
#             "price": price,
#             "pe": info.get("trailingPE"),
#             "market_cap": info.get("marketCap"),
#             "sector": info.get("sector")
#         }

#     except Exception:
#         return {
#             "ticker": ticker,
#             "price": None,
#             "pe": None,
#             "market_cap": None,
#             "sector": None
#         }


# # -----------------------------
# # STOCK SCORING LOGIC
# # -----------------------------
# def score_stock(stock):
#     """Score stock using PE and Market Cap"""

#     score = 0

#     pe = stock.get("pe")
#     market_cap = stock.get("market_cap")

#     if pe and pe < 30:
#         score += 2
#     elif pe and pe < 50:
#         score += 1

#     if market_cap and market_cap > 50_000_000_000:
#         score += 2
#     elif market_cap and market_cap > 10_000_000_000:
#         score += 1

#     return score


# # -----------------------------
# # MAIN AGENT
# # -----------------------------
# async def run_agent(query: str):

#     model = init_chat_model(
#         model="gpt-4o",
#         model_provider="openai",
#         api_key=os.getenv("OPENAI_API_KEY"),
#         temperature=0.85
#     )

#     query_lower = query.lower()

#     # -----------------------------
#     # STEP 1: FINANCE FILTER
#     # -----------------------------
#     finance_keywords = [
#         "stock","stocks","invest","investment","portfolio",
#         "market","trading","finance","bank","mutual fund",
#         "sip","etf","crypto","economy","diversify",
#         "pe ratio","dividend","pf","provident fund",
#         "epf","fd","fixed deposit","ipo","equity",
#         "bond","interest","loan","inflation"
#     ]

#     if not any(word in query_lower for word in finance_keywords):

#         return """
# I'm designed to answer **finance-related questions only**.

# Try asking things like:

# • Give me 3 good Indian stocks  
# • How should I diversify my portfolio?  
# • Explain PE ratio  
# • What is SIP?  
# • What is PF?  

# Please ask a question related to **finance or investing**.
# """

#     # -----------------------------
#     # STEP 2: INTENT DETECTION
#     # -----------------------------
#     intent_prompt = f"""
# Classify the user's intent.

# Possible intents:
# STOCK_RECOMMENDATION
# FINANCE_QUESTION

# Examples:
# "Give me 3 best stocks" -> STOCK_RECOMMENDATION
# "Which stocks should I buy?" -> STOCK_RECOMMENDATION
# "Suggest good Indian stocks" -> STOCK_RECOMMENDATION
# "How should I invest as a beginner?" -> FINANCE_QUESTION
# "What is SIP?" -> FINANCE_QUESTION

# User query:
# {query}

# Return ONLY one label.
# """

#     intent = model.invoke(intent_prompt).content.strip()

#     # -----------------------------
#     # STEP 3: GENERAL FINANCE QUESTION
#     # -----------------------------
#     if intent == "FINANCE_QUESTION":

#         response = model.invoke(f"""
# You are a helpful financial advisor.

# Answer clearly and concisely.

# Structure the answer like this:

# Short Explanation:
# 2-3 sentences explaining the concept.

# Key Points:
# • point
# • point
# • point

# Practical Tip:
# 1 actionable tip for beginners if applicable.

# Question:
# {query}

# Rules:
# - Keep answer under 120 words
# - Avoid long paragraphs
# - Be simple and practical
# """)

#         return response.content


#     # -----------------------------
#     # STEP 4: NUMBER OF STOCKS
#     # -----------------------------
#     match = re.search(r"\b(\d+)\b", query)
#     count = int(match.group(1)) if match else 3
#     count = min(count, len(TOP_NSE_STOCKS))

#     # -----------------------------
#     # STEP 5: FETCH ALL STOCK DATA
#     # -----------------------------
#     all_stock_data = []

#     for ticker in TOP_NSE_STOCKS:
#         data = get_stock_data(ticker)
#         data["score"] = score_stock(data)
#         all_stock_data.append(data)

#     # -----------------------------
#     # STEP 6: SORT BY SCORE
#     # -----------------------------
#     all_stock_data = sorted(
#         all_stock_data,
#         key=lambda x: x["score"],
#         reverse=True
#     )

#     selected_stocks = all_stock_data[:count]

#     # -----------------------------
#     # STEP 7: GENERATE RECOMMENDATIONS
#     # -----------------------------
#     recommender_prompt = f"""
# You are a professional financial analyst.

# You have REAL stock data from Yahoo Finance.

# Analyze the stocks below and give EXACTLY {count} recommendations.

# Stock Data:
# {selected_stocks}

# FORMAT STRICTLY:

# Stock Name: <ticker>
# Price: <number>
# PE Ratio: <number>
# Market Cap: <number>
# Sector: <sector>
# Recommendation: Buy/Sell/Hold
# Reason: <short explanation>
# Risks: <short explanation>

# Rules:
# - Only analyze the stocks provided
# - Do NOT say "as of my last update"
# - Do NOT say you cannot access real-time data
# - Keep explanations concise

# Separate each stock with ONE blank line.
# """

#     result = model.invoke(recommender_prompt)

#     return result.content


# # -----------------------------
# # SYNC WRAPPER
# # -----------------------------
# def run_agent_sync(query):
#     return asyncio.run(run_agent(query))




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