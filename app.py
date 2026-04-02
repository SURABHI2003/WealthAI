# # START GENAI
# from flask import Flask, render_template, request, jsonify
# import asyncio
# import os
# from dotenv import load_dotenv
# import threading
# from queue import Queue

# load_dotenv()

# app = Flask(__name__)

# # Try to import the full multi-agent system, fallback to simple agent
# try:
#     from multi_agent import run_agent
#     # Test if the full system actually works by doing a quick check
#     import subprocess
#     result = subprocess.run(['which', 'npx'], capture_output=True, text=True)
#     if result.returncode != 0:
#         raise ImportError("npx not found - Node.js not available")
#     USE_FULL_AGENT = True
#     print("✅ Full multi-agent system loaded and dependencies available")
# except (ImportError, Exception) as e:
#     print(f"⚠️ Full multi-agent system not available: {e}")
#     from simple_agent import run_simple_agent as run_agent
#     USE_FULL_AGENT = False
#     print("✅ Using simplified agent system")

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/get_recommendation', methods=['POST'])
# def get_recommendation():
#     try:
#         data = request.get_json()
#         query = data.get('query', 'Give me good stock recommendation from NSE')

#         # Create a queue to capture the output
#         output_queue = Queue()

#         def capture_output():
#             try:
#                 # Run the async function in a new event loop
#                 loop = asyncio.new_event_loop()
#                 asyncio.set_event_loop(loop)
#                 result = loop.run_until_complete(run_agent(query))

#                 # Always return the actual result content
#                 output_queue.put({"status": "success", "result": result})
#             except Exception as e:
#                 output_queue.put({"status": "error", "error": str(e)})

#         # Run in a separate thread
#         thread = threading.Thread(target=capture_output)
#         thread.start()
#         thread.join(timeout=30)  # 30 second timeout

#         if not output_queue.empty():
#             result = output_queue.get()
#             return jsonify(result)
#         else:
#             return jsonify({"status": "error", "error": "Request timed out"})

#     except Exception as e:
#         return jsonify({"status": "error", "error": str(e)})

# @app.route('/status')
# def status():
#     return jsonify({
#         "agent_type": "Full Multi-Agent System" if USE_FULL_AGENT else "Simplified Demo Agent",
#         "status": "ready"
#     })

# if __name__ == '__main__':
#     print(f"🚀 Starting NSE Stock Recommendation System")
#     print(f"📊 Agent Type: {'Full Multi-Agent' if USE_FULL_AGENT else 'Simplified Demo'}")
#     print(f"🌐 Server will be available at: http://localhost:5000")
#     app.run(debug=True, host='0.0.0.0', port=5000)
# # END GENAI



# app.py





# from flask import Flask, request, render_template_string
# from multi_agent import run_agent_sync

# app = Flask(__name__)

# HTML_PAGE = """
# <!DOCTYPE html>
# <html>
# <head>
#     <title>Stock Recommender</title>
# </head>
# <body>

# <h2>📈 Stock Recommendation System</h2>

# <form method="post">
#     <input type="text" name="query" placeholder="Enter your query" required>
#     <button type="submit">Submit</button>
# </form>

# {% if response %}
#     <h3>Result:</h3>
#     <pre>{{ response }}</pre>
# {% endif %}

# </body>
# </html>
# """

# @app.route("/", methods=["GET", "POST"])
# def home():
#     response = None

#     if request.method == "POST":
#         query = request.form.get("query")
#         response = run_agent_sync(query)

#     return render_template_string(HTML_PAGE, response=response)

# if __name__ == "__main__":
#     app.run(debug=True)



# from flask import Flask, request, render_template_string
# from multi_agent import run_agent_sync
# import markdown
# import re

# app = Flask(__name__)


# # -----------------------------
# # ✅ FORMAT STOCK RESPONSE → CARDS
# # -----------------------------
# def format_stock_response(text):
#     stocks = text.strip().split("\n\n")
#     html = ""

#     for stock in stocks:
#         lines = stock.strip().split("\n")
#         if len(lines) < 2:
#             continue

#         name = lines[0].strip()
#         rec = ""
#         target = ""
#         reason = ""

#         for line in lines:
#             if "Recommendation" in line:
#                 rec = line.split(":")[-1].strip()
#             elif "Target" in line:
#                 target = line.split(":")[-1].strip()
#             elif "Reason" in line:
#                 reason = line.split(":")[-1].strip()

#         color = "#00e676" if rec.lower() == "buy" else "#ff5252" if rec.lower() == "sell" else "#ffd600"

#         html += f"""
#         <div class="card">
#             <h3>{name}</h3>
#             <p><strong style="color:{color}">Recommendation:</strong> {rec}</p>
#             <p><strong>Target:</strong> ₹{target}</p>
#             <p><strong>Reason:</strong> {reason}</p>
#         </div>
#         """

#     return html


# # -----------------------------
# # 🌿 UI TEMPLATE
# # -----------------------------
# HTML_PAGE = """
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <title>AI Stock Assistant</title>
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">

#     <style>
#         body {
#             margin: 0;
#             font-family: 'Segoe UI', sans-serif;
#             background: linear-gradient(135deg, #0f2027, #203a43, #2c7744);
#             color: white;
#             display: flex;
#             justify-content: center;
#             align-items: center;
#             height: 100vh;
#         }

#         .container {
#             background: rgba(255, 255, 255, 0.05);
#             backdrop-filter: blur(12px);
#             border-radius: 16px;
#             padding: 40px;
#             width: 80%;
#             max-width: 900px;
#             min-height: 400px;
#             box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
#         }

#         h2 {
#             text-align: center;
#             color: #00ff9d;
#         }

#         form {
#             display: flex;
#             gap: 10px;
#             justify-content: center;
#             margin-top: 20px;
#         }

#         input {
#             width: 70%;
#             padding: 14px;
#             border-radius: 10px;
#             border: none;
#             outline: none;
#             font-size: 16px;
#         }

#         button {
#             padding: 14px 22px;
#             border: none;
#             border-radius: 10px;
#             background: #00c853;
#             color: white;
#             cursor: pointer;
#             transition: 0.3s;
#         }

#         button:hover {
#             background: #00e676;
#             transform: scale(1.05);
#         }

#         .response-box {
#             margin-top: 20px;
#             max-height: 400px;
#             overflow-y: auto;
#         }

#         /* CARD UI */
#         .card {
#             background: rgba(255,255,255,0.08);
#             padding: 15px;
#             border-radius: 12px;
#             margin-bottom: 15px;
#             border-left: 5px solid #00e676;
#             transition: 0.3s;
#         }

#         .card:hover {
#             transform: translateY(-5px);
#             box-shadow: 0 4px 20px rgba(0,255,150,0.2);
#         }

#         .card h3 {
#             margin: 0 0 10px;
#             color: #00ff9d;
#         }

#         .loading {
#             display: none;
#             text-align: center;
#             margin-top: 10px;
#             color: #a5ffb0;
#         }
#     </style>

#     <script>
#         function showLoader() {
#             document.getElementById("loading").style.display = "block";
#         }
#     </script>

# </head>

# <body>

# <div class="container">
#     <h2>Your Man in Finance</h2>

#     <form method="post" onsubmit="showLoader()">
#         <input type="text" name="query" placeholder="Ask about stocks, tax, SIP..." required>
#         <button type="submit">Ask</button>
#     </form>

#     <div id="loading" class="loading">
#         ⏳ Thinking...
#     </div>

#     {% if response %}
#         <div class="response-box">
#             {{ response | safe }}
#         </div>
#     {% endif %}
# </div>

# </body>
# </html>
# """


# # -----------------------------
# # 🚀 ROUTE
# # -----------------------------
# @app.route("/", methods=["GET", "POST"])
# def home():
#     response = None

#     if request.method == "POST":
#         query = request.form.get("query")
#         raw_response = run_agent_sync(query)

#         # ✅ Detect stock response → use cards
#         if "Recommendation" in raw_response:
#             response = format_stock_response(raw_response)
#         else:
#             response = markdown.markdown(raw_response)

#     return render_template_string(HTML_PAGE, response=response)


# # -----------------------------
# # ▶ RUN
# # -----------------------------
# if __name__ == "__main__":
#     app.run(debug=True)



# -----------------------------------------------------




# from flask import Flask, request, render_template_string
# from multi_agent import run_agent_sync

# app = Flask(__name__)

# # -----------------------------
# # ✅ FORMAT STOCK RESPONSE → CARDS
# # -----------------------------
# def format_stock_response(text):
#     stocks = text.strip().split("\n\n")
#     html = ""

#     for stock in stocks:
#         lines = stock.strip().split("\n")

#         name, rec, target, reason, risk = "", "", "", "", ""

#         for line in lines:
#             if "Stock Name" in line:
#                 name = line.split(":")[-1].strip()
#             elif "Recommendation" in line:
#                 rec = line.split(":")[-1].strip()
#             elif "Target" in line:
#                 target = line.split(":")[-1].strip()
#             elif "Reason" in line:
#                 reason = line.split(":")[-1].strip()
#             elif "Risks" in line:
#                 risk = line.split(":")[-1].strip()

#         if not name:
#             continue

#         color = "#00e676" if rec.lower() == "buy" else "#ff5252" if rec.lower() == "sell" else "#ffd600"

#         html += f"""
#         <div class="card">
#             <h3>{name}</h3>
#             <p><strong style="color:{color}">Recommendation:</strong> {rec}</p>
#             <p><strong>Target:</strong> ₹{target}</p>
#             <p><strong>Reason:</strong> {reason}</p>
#             <p><strong>Risks:</strong> {risk}</p>
#         </div>
#         """

#     return html


# # -----------------------------
# # 🌿 UI TEMPLATE
# # -----------------------------
# HTML_PAGE = """
# <!DOCTYPE html>
# <html>
# <head>
# <title>AI Stock Assistant</title>

# <style>
# body {
#     margin: 0;
#     font-family: 'Segoe UI';
#     background: linear-gradient(135deg, #0f2027, #203a43, #2c7744);
#     color: white;
#     display: flex;
#     justify-content: center;
#     align-items: center;
#     height: 100vh;
# }

# .container {
#     width: 85%;
#     max-width: 1000px;
#     padding: 40px;
#     border-radius: 16px;
#     backdrop-filter: blur(12px);
#     background: rgba(255,255,255,0.05);
# }

# h2 {
#     text-align: center;
#     color: #00ff9d;
# }

# form {
#     display: flex;
#     gap: 10px;
#     margin-top: 20px;
# }

# input {
#     flex: 1;
#     padding: 14px;
#     border-radius: 10px;
#     border: none;
# }

# button {
#     padding: 14px;
#     background: #00c853;
#     border: none;
#     border-radius: 10px;
#     color: white;
# }

# .response-box {
#     margin-top: 20px;
#     max-height: 450px;
#     overflow-y: auto;
# }

# .card {
#     background: rgba(255,255,255,0.08);
#     padding: 15px;
#     border-radius: 12px;
#     margin-bottom: 15px;
#     border-left: 5px solid #00e676;
# }

# .loading {
#     display: none;
#     text-align: center;
# }
# </style>

# <script>
# function showLoader(){
#     document.getElementById("loading").style.display="block";
# }
# </script>

# </head>

# <body>
# <div class="container">

# <h2>Your Man in Finance</h2>

# <form method="post" onsubmit="showLoader()">
#     <input type="text" name="query" placeholder="Ask anything..." required>
#     <button type="submit">Ask</button>
# </form>

# <div id="loading" class="loading">⏳ Thinking...</div>

# {% if response %}
# <div class="response-box">
#     {{ response | safe }}
# </div>
# {% endif %}

# </div>
# </body>
# </html>
# """


# # -----------------------------
# # 🚀 ROUTE
# # -----------------------------
# @app.route("/", methods=["GET", "POST"])
# def home():
#     response = None

#     if request.method == "POST":
#         query = request.form.get("query")
#         raw_response = run_agent_sync(query)

#         if "Stock Name:" in raw_response:
#             response = format_stock_response(raw_response)
#         else:
#             response = f"<pre>{raw_response}</pre>"

#     return render_template_string(HTML_PAGE, response=response)


# # -----------------------------
# # ▶ RUN
# # -----------------------------
# if __name__ == "__main__":
#     app.run(debug=True)


# --------------------------------------------------
# vers new ion


# # app.py
# import os
# import asyncio
# from flask import Flask, request, render_template_string
# from multi_agent import run_agent  # your async stock agent function

# app = Flask(__name__)

# # -----------------------------
# # HTML TEMPLATE
# # -----------------------------
# HTML_TEMPLATE = """
# <!DOCTYPE html>
# <html>
# <head>
#     <title>Indian Stock Recommender</title>
# </head>
# <body>
#     <h1>Indian Stock Recommender</h1>
#     <form method="POST">
#         <label for="query">Enter your query:</label><br>
#         <input type="text" id="query" name="query" size="60" placeholder="e.g. Give me 3 best Indian stocks"><br><br>
#         <input type="submit" value="Get Recommendations">
#     </form>
#     <hr>
#     {% if result %}
#         <h2>Result:</h2>
#         <pre>{{ result }}</pre>
#     {% endif %}
# </body>
# </html>
# """

# # -----------------------------
# # ROUTE
# # -----------------------------
# @app.route("/", methods=["GET", "POST"])
# def home():
#     result = None
#     query = None

#     if request.method == "POST":
#         query = request.form.get("query")
#         if query:
#             # Run async agent in sync Flask route
#             try:
#                 result = asyncio.run(run_agent(query))
#             except Exception as e:
#                 result = f"Error: {e}"
#         else:
#             result = "Please enter a query."

#     return render_template_string(HTML_TEMPLATE, result=result)

# # -----------------------------
# # RUN APP
# # -----------------------------
# if __name__ == "__main__":
#     app.run(debug=True)

# --------------------------------------------------------------------------------------------------------------






# from flask import Flask, request, render_template_string
# from multi_agent import run_agent_sync

# app = Flask(__name__)

# # -----------------------------
# # FORMAT STOCK RESPONSE → CARDS
# # -----------------------------
# def format_stock_response(text):

#     stocks = text.strip().split("\n\n")
#     html = ""

#     for stock in stocks:

#         lines = stock.strip().split("\n")

#         name=""
#         price=""
#         pe=""
#         cap=""
#         sector=""
#         rec=""
#         reason=""
#         risk=""

#         for line in lines:

#             if "Stock Name" in line:
#                 name=line.split(":")[-1].strip()

#             elif "Price" in line:
#                 price=line.split(":")[-1].strip()

#             elif "PE Ratio" in line:
#                 pe=line.split(":")[-1].strip()

#             elif "Market Cap" in line:
#                 cap=line.split(":")[-1].strip()

#             elif "Sector" in line:
#                 sector=line.split(":")[-1].strip()

#             elif "Recommendation" in line:
#                 rec=line.split(":")[-1].strip()

#             elif "Reason" in line:
#                 reason=line.split(":")[-1].strip()

#             elif "Risks" in line:
#                 risk=line.split(":")[-1].strip()

#         if not name:
#             continue

#         color = "#00e676" if rec.lower()=="buy" else "#ff5252" if rec.lower()=="sell" else "#ffd600"

#         html += f"""
#         <div class="card">

#             <h3>{name}</h3>

#             <p><b>Price:</b> ₹{price}</p>
#             <p><b>PE Ratio:</b> {pe}</p>
#             <p><b>Market Cap:</b> {cap}</p>
#             <p><b>Sector:</b> {sector}</p>

#             <p><b style="color:{color}">Recommendation:</b> {rec}</p>

#             <p><b>Reason:</b> {reason}</p>

#             <p><b>Risks:</b> {risk}</p>

#         </div>
#         """

#     return html


# # -----------------------------
# # UI TEMPLATE
# # -----------------------------
# HTML_PAGE = """
# <!DOCTYPE html>
# <html>

# <head>

# <title>AI Stock Assistant</title>

# <style>

# body{
# margin:0;
# font-family:'Segoe UI';
# background:linear-gradient(135deg,#0f2027,#203a43,#2c7744);
# color:white;
# display:flex;
# justify-content:center;
# align-items:center;
# height:100vh;
# }

# .container{
# width:85%;
# max-width:1000px;
# padding:40px;
# border-radius:16px;
# backdrop-filter:blur(12px);
# background:rgba(255,255,255,0.05);
# }

# h2{
# text-align:center;
# color:#00ff9d;
# }

# form{
# display:flex;
# gap:10px;
# margin-top:20px;
# }

# input{
# flex:1;
# padding:14px;
# border-radius:10px;
# border:none;
# }

# button{
# padding:14px;
# background:#00c853;
# border:none;
# border-radius:10px;
# color:white;
# cursor:pointer;
# }

# .response-box{
# margin-top:20px;
# max-height:450px;
# overflow-y:auto;
# }

# .card{
# background:rgba(255,255,255,0.08);
# padding:15px;
# border-radius:12px;
# margin-bottom:15px;
# border-left:5px solid #00e676;
# }

# .loading{
# display:none;
# text-align:center;
# margin-top:10px;
# }

# </style>

# <script>
# function showLoader(){
# document.getElementById("loading").style.display="block";
# }
# </script>

# </head>


# <body>

# <div class="container">

# <h2>Your Man in Finance</h2>

# <form method="post" onsubmit="showLoader()">

# <input type="text"
# name="query"
# placeholder="Ask something like: Give me 3 best Indian stocks"
# required>

# <button type="submit">Ask</button>

# </form>

# <div id="loading" class="loading">
# ⏳ Thinking...
# </div>

# {% if response %}

# <div class="response-box">
# {{response | safe}}
# </div>

# {% endif %}

# </div>

# </body>
# </html>
# """


# # -----------------------------
# # ROUTE
# # -----------------------------
# @app.route("/",methods=["GET","POST"])
# def home():

#     response=None

#     if request.method=="POST":

#         query=request.form.get("query")

#         raw_response=run_agent_sync(query)

#         if "Stock Name:" in raw_response:
#             response=format_stock_response(raw_response)
#         else:
#             response=f"<pre>{raw_response}</pre>"

#     return render_template_string(HTML_PAGE,response=response)


# # -----------------------------
# # RUN
# # -----------------------------
# if __name__=="__main__":
#     app.run(debug=True)




# from flask import Flask, request, render_template_string
# from multi_agent import run_agent_sync

# app = Flask(__name__)

# # -----------------------------
# # FORMAT STOCK RESPONSE → CARDS
# # -----------------------------
# def format_stock_response(text):

#     stocks = text.strip().split("\n\n")
#     html = ""

#     for stock in stocks:

#         lines = stock.strip().split("\n")

#         name=""
#         price=""
#         pe=""
#         cap=""
#         sector=""
#         rec=""
#         reason=""
#         risk=""

#         for line in lines:

#             if "Stock Name" in line:
#                 name=line.split(":")[-1].strip()

#             elif "Price" in line:
#                 price=line.split(":")[-1].strip()

#             elif "PE Ratio" in line:
#                 pe=line.split(":")[-1].strip()

#             elif "Market Cap" in line:
#                 cap=line.split(":")[-1].strip()

#             elif "Sector" in line:
#                 sector=line.split(":")[-1].strip()

#             elif "Recommendation" in line:
#                 rec=line.split(":")[-1].strip()

#             elif "Reason" in line:
#                 reason=line.split(":")[-1].strip()

#             elif "Risks" in line:
#                 risk=line.split(":")[-1].strip()

#         if not name:
#             continue

#         color = "#00e676" if rec.lower()=="buy" else "#ff5252" if rec.lower()=="sell" else "#ffd600"

#         html += f"""
#         <div class="card">

#             <h3>{name}</h3>

#             <p><b>Price:</b> ₹{price}</p>
#             <p><b>PE Ratio:</b> {pe}</p>
#             <p><b>Market Cap:</b> {cap}</p>
#             <p><b>Sector:</b> {sector}</p>

#             <p><b style="color:{color}">Recommendation:</b> {rec}</p>

#             <p><b>Reason:</b> {reason}</p>

#             <p><b>Risks:</b> {risk}</p>

#         </div>
#         """

#     return html


# # -----------------------------
# # FORMAT FINANCE ANSWER
# # -----------------------------
# def format_finance_answer(text):

#     html = f"""
#     <div class="card">
#         <div style="font-size:17px; line-height:1.6;">
#             {text.replace("•","<br>•").replace("\n","<br>")}
#         </div>
#     </div>
#     """

#     return html


# # -----------------------------
# # UI TEMPLATE
# # -----------------------------
# HTML_PAGE = """
# <!DOCTYPE html>
# <html>

# <head>

# <title>AI Stock Assistant</title>

# <style>

# body{
# margin:0;
# font-family:'Segoe UI';
# background:linear-gradient(135deg,#0f2027,#203a43,#2c7744);
# color:white;
# display:flex;
# justify-content:center;
# align-items:center;
# height:100vh;
# }

# .container{
# width:85%;
# max-width:1000px;
# padding:40px;
# border-radius:16px;
# backdrop-filter:blur(12px);
# background:rgba(255,255,255,0.05);
# }

# h2{
# text-align:center;
# color:#00ff9d;
# }

# form{
# display:flex;
# gap:10px;
# margin-top:20px;
# }

# input{
# flex:1;
# padding:14px;
# border-radius:10px;
# border:none;
# }

# button{
# padding:14px;
# background:#00c853;
# border:none;
# border-radius:10px;
# color:white;
# cursor:pointer;
# }

# .response-box{
# margin-top:20px;
# max-height:450px;
# overflow-y:auto;
# }

# .card{
# background:rgba(255,255,255,0.08);
# padding:15px;
# border-radius:12px;
# margin-bottom:15px;
# border-left:5px solid #00e676;
# }

# .loading{
# display:none;
# text-align:center;
# margin-top:10px;
# }

# </style>

# <script>
# function showLoader(){
# document.getElementById("loading").style.display="block";
# }
# </script>

# </head>


# <body>

# <div class="container">

# <h2>Your Man in Finance</h2>

# <form method="post" onsubmit="showLoader()">

# <input type="text"
# name="query"
# placeholder="Ask something like: Give me 3 best Indian stocks"
# required>

# <button type="submit">Ask</button>

# </form>

# <div id="loading" class="loading">
# ⏳ Thinking...
# </div>

# {% if response %}

# <div class="response-box">
# {{response | safe}}
# </div>

# {% endif %}

# </div>

# </body>
# </html>
# """


# # -----------------------------
# # ROUTE
# # -----------------------------
# @app.route("/",methods=["GET","POST"])
# def home():

#     response=None

#     if request.method=="POST":

#         query=request.form.get("query")

#         raw_response=run_agent_sync(query)

#         if "Stock Name:" in raw_response:
#             response=format_stock_response(raw_response)
#         else:
#             response=format_finance_answer(raw_response)

#     return render_template_string(HTML_PAGE,response=response)


# # -----------------------------
# # RUN
# # -----------------------------
# if __name__=="__main__":
#     app.run(debug=True)



# ----------------------------------------------------------------------------------------
# best version




# from flask import Flask, request, render_template_string
# from multi_agent import run_agent_sync
# import re

# app = Flask(__name__)

# # -----------------------------
# # FORMAT STOCK RESPONSE → CARDS
# # -----------------------------
# def format_stock_response(text):

#     stocks = text.strip().split("\n\n")
#     html = ""

#     for stock in stocks:

#         lines = stock.strip().split("\n")

#         name=""
#         price=""
#         pe=""
#         cap=""
#         sector=""
#         rec=""
#         reason=""
#         risk=""

#         for line in lines:

#             if "Stock Name" in line:
#                 name=line.split(":")[-1].strip()

#             elif "Price" in line:
#                 price=line.split(":")[-1].strip()

#             elif "PE Ratio" in line:
#                 pe=line.split(":")[-1].strip()

#             elif "Market Cap" in line:
#                 cap=line.split(":")[-1].strip()

#             elif "Sector" in line:
#                 sector=line.split(":")[-1].strip()

#             elif "Recommendation" in line:
#                 rec=line.split(":")[-1].strip()

#             elif "Reason" in line:
#                 reason=line.split(":")[-1].strip()

#             elif "Risks" in line:
#                 risk=line.split(":")[-1].strip()

#         if not name:
#             continue

#         color = "#00e676" if rec.lower()=="buy" else "#ff5252" if rec.lower()=="sell" else "#ffd600"

#         html += f"""
#         <div class="card">

#             <h3>{name}</h3>

#             <p><b>Price:</b> ₹{price}</p>
#             <p><b>PE Ratio:</b> {pe}</p>
#             <p><b>Market Cap:</b> {cap}</p>
#             <p><b>Sector:</b> {sector}</p>

#             <p><b style="color:{color}">Recommendation:</b> {rec}</p>

#             <p><b>Reason:</b> {reason}</p>

#             <p><b>Risks:</b> {risk}</p>

#         </div>
#         """

#     return html


# # -----------------------------
# # FORMAT FINANCE ANSWERS
# # -----------------------------
# def format_finance_answer(text):

#     # remove markdown **
#     text = text.replace("**", "")

#     # split sections by numbers like 1. 2. 3.
#     sections = re.split(r"\n?\d+\.\s", text)

#     html = ""

#     for sec in sections:
#         sec = sec.strip()
#         if not sec:
#             continue

#         # first line becomes heading
#         parts = sec.split("\n",1)

#         title = parts[0]
#         content = parts[1] if len(parts) > 1 else ""

#         html += f"""
#         <div class="finance-card">
#             <h3>{title}</h3>
#             <p>{content.replace('\n','<br>')}</p>
#         </div>
#         """

#     return html


# # -----------------------------
# # UI TEMPLATE
# # -----------------------------
# HTML_PAGE = """
# <!DOCTYPE html>
# <html>

# <head>

# <title>AI Stock Assistant</title>

# <style>

# body{
# margin:0;
# font-family:'Segoe UI';
# background:linear-gradient(135deg,#0f2027,#203a43,#2c7744);
# color:white;
# display:flex;
# justify-content:center;
# align-items:center;
# height:100vh;
# }

# .container{
# width:85%;
# max-width:1000px;
# padding:40px;
# border-radius:16px;
# backdrop-filter:blur(12px);
# background:rgba(255,255,255,0.05);
# }

# h2{
# text-align:center;
# color:#00ff9d;
# }

# form{
# display:flex;
# gap:10px;
# margin-top:20px;
# }

# input{
# flex:1;
# padding:14px;
# border-radius:10px;
# border:none;
# }

# button{
# padding:14px;
# background:#00c853;
# border:none;
# border-radius:10px;
# color:white;
# cursor:pointer;
# }

# .response-box{
# margin-top:20px;
# max-height:450px;
# overflow-y:auto;
# }

# .card{
# background:rgba(255,255,255,0.08);
# padding:15px;
# border-radius:12px;
# margin-bottom:15px;
# border-left:5px solid #00e676;
# }

# .finance-card{
# background:rgba(255,255,255,0.08);
# padding:18px;
# border-radius:12px;
# margin-bottom:15px;
# border-left:5px solid #00ff9d;
# font-size:16px;
# line-height:1.6;
# }

# .loading{
# display:none;
# text-align:center;
# margin-top:10px;
# }

# </style>

# <script>
# function showLoader(){
# document.getElementById("loading").style.display="block";
# }
# </script>

# </head>


# <body>

# <div class="container">

# <h2>Your Man in Finance</h2>

# <form method="post" onsubmit="showLoader()">

# <input type="text"
# name="query"
# placeholder="Ask something like: Give me 3 best Indian stocks"
# required>

# <button type="submit">Ask</button>

# </form>

# <div id="loading" class="loading">
# ⏳ Thinking...
# </div>

# {% if response %}

# <div class="response-box">
# {{response | safe}}
# </div>

# {% endif %}

# </div>

# </body>
# </html>
# """


# # -----------------------------
# # ROUTE
# # -----------------------------
# @app.route("/",methods=["GET","POST"])
# def home():

#     response=None

#     if request.method=="POST":

#         query=request.form.get("query")

#         raw_response=run_agent_sync(query)

#         if "Stock Name:" in raw_response:
#             response=format_stock_response(raw_response)

#         elif "I'm designed to answer" in raw_response:
#             response=f"<pre>{raw_response}</pre>"

#         else:
#             response=format_finance_answer(raw_response)

#     return render_template_string(HTML_PAGE,response=response)


# # -----------------------------
# # RUN
# # -----------------------------
# if __name__=="__main__":
#     app.run(debug=True)






from flask import Flask, request, render_template_string
from multi_agent import run_agent_sync
import re

app = Flask(__name__)

# -----------------------------
# FORMAT STOCK RESPONSE → CARDS
# -----------------------------
def format_stock_response(text):

    stocks = text.strip().split("\n\n")
    html = ""

    for stock in stocks:

        lines = stock.strip().split("\n")

        name=""
        price=""
        pe=""
        cap=""
        sector=""
        rec=""
        reason=""
        risk=""

        for line in lines:

            if "Stock Name" in line:
                name=line.split(":")[-1].strip()

            elif "Price" in line:
                price=line.split(":")[-1].strip()

            elif "PE Ratio" in line:
                pe=line.split(":")[-1].strip()

            elif "Market Cap" in line:
                cap=line.split(":")[-1].strip()

            elif "Sector" in line:
                sector=line.split(":")[-1].strip()

            elif "Recommendation" in line:
                rec=line.split(":")[-1].strip()

            elif "Reason" in line:
                reason=line.split(":")[-1].strip()

            elif "Risks" in line:
                risk=line.split(":")[-1].strip()

        if not name:
            continue

        color = "#00e676" if rec.lower()=="buy" else "#ff5252" if rec.lower()=="sell" else "#ffd600"

        html += f"""
        <div class="card">

            <h3>{name}</h3>

            <p><b>Price:</b> ₹{price}</p>
            <p><b>PE Ratio:</b> {pe}</p>
            <p><b>Market Cap:</b> {cap}</p>
            <p><b>Sector:</b> {sector}</p>

            <p><b style="color:{color}">Recommendation:</b> {rec}</p>

            <p><b>Reason:</b> {reason}</p>

            <p><b>Risks:</b> {risk}</p>

        </div>
        """

    return html


# -----------------------------
# FORMAT FINANCE ANSWERS
# -----------------------------
def format_finance_answer(text):

    # remove markdown formatting
    text = text.replace("**","")
    text = text.replace("---","")
    text = text.replace("###","")
    text = text.replace("##","")

    # split by numbered sections
    sections = re.split(r"\n?\d+\)\s|\n?\d+\.\s", text)

    html=""

    for sec in sections:

        sec=sec.strip()
        if not sec:
            continue

        parts=sec.split("\n",1)

        title=parts[0]
        content=parts[1] if len(parts)>1 else ""

        html+=f"""
        <div class="finance-card">
            <h3>{title}</h3>
            <p>{content.replace("\n","<br>")}</p>
        </div>
        """

    # fallback if formatting fails
    if html.strip()=="":
        html=f"""
        <div class="finance-card">
        {text.replace("\n","<br>")}
        </div>
        """

    return html


# -----------------------------
# UI TEMPLATE
# -----------------------------
HTML_PAGE = """
<!DOCTYPE html>
<html>

<head>

<title>AI Stock Assistant</title>

<style>

body{
margin:0;
font-family:'Segoe UI';
background:linear-gradient(135deg,#0f2027,#203a43,#2c7744);
color:white;
display:flex;
justify-content:center;
align-items:center;
height:100vh;
}

.container{
width:85%;
max-width:1000px;
padding:40px;
border-radius:16px;
backdrop-filter:blur(12px);
background:rgba(255,255,255,0.05);
}

h2{
text-align:center;
color:#00ff9d;
}

form{
display:flex;
gap:10px;
margin-top:20px;
}

input{
flex:1;
padding:14px;
border-radius:10px;
border:none;
}

button{
padding:14px;
background:#00c853;
border:none;
border-radius:10px;
color:white;
cursor:pointer;
}

.response-box{
margin-top:20px;
max-height:450px;
overflow-y:auto;
}

.card{
background:rgba(255,255,255,0.08);
padding:15px;
border-radius:12px;
margin-bottom:15px;
border-left:5px solid #00e676;
}

.finance-card{
background:rgba(255,255,255,0.08);
padding:18px;
border-radius:12px;
margin-bottom:15px;
border-left:5px solid #00ff9d;
font-size:16px;
line-height:1.6;
}

.loading{
display:none;
text-align:center;
margin-top:10px;
}

</style>

<script>
function showLoader(){
document.getElementById("loading").style.display="block";
}
</script>

</head>


<body>

<div class="container">

<h2>WealthAI</h2>

<form method="post" onsubmit="showLoader()">

<input type="text"
name="query"
placeholder="Ask something like: Give me 3 best Indian stocks"
required>

<button type="submit">Ask</button>

</form>

<div id="loading" class="loading">
⏳ Thinking...
</div>

{% if response %}

<div class="response-box">
{{response | safe}}
</div>

{% endif %}

</div>

</body>
</html>
"""


# -----------------------------
# ROUTE
# -----------------------------
@app.route("/",methods=["GET","POST"])
def home():

    response=None

    if request.method=="POST":

        query=request.form.get("query")

        raw_response=run_agent_sync(query)

        if "Stock Name:" in raw_response:

            response=format_stock_response(raw_response)

        elif "I'm designed to answer" in raw_response:

            response = """
            <div class="finance-card">

                <h3>Hey there!</h3>

                <p>Whether you're exploring stocks or learning the basics of investing, I’m here to help!</p>

                <p><b>Try asking things like:</b></p>

                <ul style="line-height:1.8; padding-left:20px;">
                    <li>Give me 3 good Indian stocks</li>
                    <li>How should I diversify my portfolio?</li>
                    <li>Explain PE ratio</li>
                    <li>What is SIP?</li>
                    <li>What is PF?</li>
                </ul>

                <p style="margin-top:10px;">
                Ask anything about finance, investing, or the stock market to get started.
                </p>

            </div>
            """

        else:

            response=format_finance_answer(raw_response)

    return render_template_string(HTML_PAGE,response=response)


# -----------------------------
# RUN
# -----------------------------
if __name__=="__main__":
    app.run(debug=True)