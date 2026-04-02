# WealthAI 💰🤖

**WealthAI** is an AI-powered financial analysis platform that uses a **multi-agent architecture** to analyze stock data and generate intelligent investment insights.

The system combines financial data processing, AI agents, and a web interface to help users explore market trends and make informed investment decisions.

---

# 🚀 Features

### 📊 Stock Market Analysis
- Analyze stock trends and historical data
- Generate AI-based financial insights
- Assist with investment research

### 🤖 Multi-Agent AI System
The platform uses multiple AI agents that collaborate to process financial queries and produce structured insights.

Agents handle tasks such as:
- Data retrieval
- Financial analysis
- Recommendation generation
- Response synthesis

### 🌐 Web Application
- Interactive interface for users
- HTML template-based frontend

### 🔐 Secure Configuration
- Sensitive credentials stored in `.env`
- Environment variables excluded from Git

---

# 🧠 System Architecture

The application follows a **multi-agent pipeline** for financial analysis.

```
User Request
      ↓
Flask App (app.py)
      ↓
Multi-Agent System (multi_agent.py)
      ├── Data Agent
      ├── Analysis Agent
      ├── Recommendation Agent
      └── Response Generator
      ↓
HTML Templates
      ↓
User Interface
```

---

# 📂 Project Structure

```
WealthAI/
│
├── templates/          # HTML templates for the web interface
├── app.py              # Main application entry point
├── multi_agent.py      # Multi-agent AI system logic
├── .gitignore          # Git ignore rules
└── README.md
```

### Ignored Files

The following files are intentionally excluded from the repository:

```
.env
__pycache__/
```

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone https://github.com/SURABHI2003/WealthAI.git
cd WealthAI
```

---

## 2. Create a virtual environment

```bash
python -m venv venv
```

### Activate environment

Windows

```bash
venv\Scripts\activate
```

Mac/Linux

```bash
source venv/bin/activate
```

---

## 3. Install dependencies

If a requirements file exists:

```bash
pip install -r requirements.txt
```

Otherwise install dependencies manually.

---

## 4. Configure environment variables

Create a `.env` file in the root directory.

Example:

```
API_KEY=your_api_key
MODEL_NAME=your_model
```

⚠️ **Important:**  
The `.env` file is excluded from Git to protect sensitive credentials.

---

# ▶️ Running the Application

Start the application:

```bash
python app.py
```

Then open the web interface in your browser.

---

# 🛠 Tech Stack

- Python
- Flask
- Multi-Agent AI Architecture
- Financial Data APIs
- HTML / CSS

---

# 📊 Use Cases

- AI financial assistant
- Stock market analysis
- Investment research
- Financial data exploration

---

# 🔒 Security

Sensitive information such as API keys and credentials are stored in `.env` files and excluded from version control via `.gitignore`.

---

# 🤝 Contributing

Contributions are welcome.

Steps:

1. Fork the repository  
2. Create a feature branch  
3. Commit your changes  
4. Open a pull request

---

# 👩‍💻 Author

**Surabhi Shreya**

GitHub:  
https://github.com/SURABHI2003

---

⭐ If you found this project useful, consider starring the repository!
