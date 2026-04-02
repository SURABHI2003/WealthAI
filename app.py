from flask import Flask, request, render_template_string
from multi_agent import run_agent_sync
import re
import os

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

    if not text:
        return "<div class='finance-card'>No response generated.</div>"

    text = text.replace("**","")
    text = text.replace("---","")
    text = text.replace("###","")
    text = text.replace("##","")

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
@app.route("/", methods=["GET","POST"])
def home():

    response=None

    if request.method=="POST":

        query=request.form.get("query")

        try:
            raw_response=run_agent_sync(query)
        except Exception as e:
            raw_response=f"Error running agent: {str(e)}"

        if raw_response and "Stock Name:" in raw_response:

            response=format_stock_response(raw_response)

        elif raw_response and "I'm designed to answer" in raw_response:

            response = """
            <div class="finance-card">
                <h3>Hey there!</h3>
                <p>Ask anything about finance, investing, or the stock market.</p>
            </div>
            """

        else:

            response=format_finance_answer(raw_response)

    return render_template_string(HTML_PAGE,response=response)


# -----------------------------
# RUN SERVER
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0", port=port)