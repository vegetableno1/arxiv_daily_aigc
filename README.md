# Arxiv Daily AIGC-Quant

> **Forked from [onion-liu/arxiv_daily_aigc](https://github.com/onion-liu/arxiv_daily_aigc)**

This is an automated project designed to fetch the latest papers from **Quantitative Finance (q-fin)** and **AI/ML (cs.LG, cs.AI, cs.CL)** fields on arXiv daily, use AI (via OpenRouter API) to filter papers related to **algorithmic trading, quantitative finance, and AI applied to financial markets**, and provide **Alpha potential scoring** for each paper. The system generates structured JSON data and bilingual (English/Chinese) HTML reports, then automatically deploys the results to GitHub Pages via GitHub Actions.

## 🎯 Key Features

1.  **Smart Topic Filtering**: Fetches papers from multiple arXiv categories (q-fin.PM, q-fin.TR, cs.LG, cs.AI, cs.CL) and uses LLM to filter for **quantitative trading relevance**
2.  **Alpha Potential Scoring**: Each paper is evaluated on:
    *   **Relevance Score** (1-10): Practical value for real-world trading
    *   **Core Methodology**: Main algorithmic approach (GNN, Transformer, RL, etc.)
    *   **Data Sources**: Market data types used (LOB, options flow, sentiment, etc.)
    *   **Alpha Potential**: The market inefficiency or signal source being exploited
    *   **Tags**: Methodology, data type, and application keywords
3.  **Bilingual Reports**: Full Chinese translation of paper titles and summaries for better accessibility
4.  **Automated Workflow**: Daily scheduled fetching, filtering, scoring, and deployment via GitHub Actions
5.  **Modern UI**: Beautiful, responsive interface built with TailwindCSS and Framer Motion

## 📊 What Makes This Different

Unlike the original [arxiv_daily_aigc](https://github.com/onion-liu/arxiv_daily_aigc) which focused on Computer Vision (AIGC), this fork specializes in:

- **Quantitative Finance Focus**: Papers specifically selected for algorithmic trading and quant finance applications
- **Practical Scoring**: Alpha potential assessment to help you quickly identify actionable research
- **Bilingual Interface**: Full Chinese translation for quantitative researchers in Chinese-speaking regions
- **Trading-Oriented Metrics**: Emphasis on core methodology, data sources, and alpha potential rather than just academic relevance

## 🛠 Tech Stack

*   **Backend**: Python 3.x (`arxiv`, `requests`, `jinja2`)
*   **AI/ML**: OpenRouter API (Google Gemini 2.0 Flash)
*   **Frontend**: HTML5, TailwindCSS, JavaScript, Framer Motion
*   **Automation**: GitHub Actions
*   **Deployment**: GitHub Pages

## 📦 Installation

1.  **Clone Repository**:
    ```bash
    git clone https://github.com/vegetableno1/arxiv_daily_aigc.git
    cd arxiv_daily_aigc
    ```

2.  **Create and Activate Virtual Environment**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # macOS/Linux
    # or .venv\Scripts\activate  # Windows
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure API Key**: This project requires an **OpenRouter API Key** for AI filtering and scoring.
    *   Get your key at [openrouter.ai](https://openrouter.ai/)
    *   Set it as environment variable: `export OPENROUTER_API_KEY='your_key_here'`
    *   In GitHub Actions, add it as a Secret named `OPENROUTER_API_KEY`

## 🚀 Usage

### Local Run

```bash
# Ensure the OPENROUTER_API_KEY environment variable is set
export OPENROUTER_API_KEY='your_openrouter_api_key'

# Run the main script
python src/main.py
```

After successful execution:
*   JSON data: `daily_json/YYYY-MM-DD.json`
*   HTML report: `daily_html/YYYY_MM_DD.html`
*   Main page updated: `index.html`

### GitHub Actions Automation

The `.github/workflows/daily_arxiv.yml` workflow:
*   **Scheduled Trigger**: Runs daily at 04:00 UTC (12:00 Beijing Time)
*   **Manual Trigger**: Can be triggered manually from the Actions tab

## 🌐 View Results

Visit the GitHub Pages site: **[arxiv_daily_aigc](https://vegetableno1.github.io/arxiv_daily_aigc/)**

## 📁 File Structure

```
.
├── .github/workflows/
│   └── daily_arxiv.yml       # GitHub Actions workflow
├── src/
│   ├── main.py               # Main execution script
│   ├── scraper.py            # ArXiv scraper module
│   ├── filter.py             # AI filtering & scoring module
│   └── html_generator.py     # HTML generator module
├── templates/
│   └── paper_template.html   # Jinja2 template for reports
├── daily_json/               # Daily JSON data
├── daily_html/               # Daily HTML reports
├── index.html                # Main entry page
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🎨 Scoring System

Each paper is evaluated on multiple dimensions:

- **Trading Relevance (1-10)**: Practical applicability to real-world trading
- **Core Methodology**: Algorithmic approach (GNN, Transformer, DRL, Statistical Arbitrage, etc.)
- **Data Sources**: Market/alternative data used (LOB data, options flow, sentiment, etc.)
- **Alpha Potential**: Market inefficiency or signal source being exploited
- **Tags**: Keywords for methodology, data type, and application area

## 🙏 Acknowledgements

- **Original Project**: [onion-liu/arxiv_daily_aigc](https://github.com/onion-liu/arxiv_daily_aigc) - Forked and modified for quantitative finance focus
- **Initial Inspiration**: [fortunechen](https://github.com/fortunechen)
- **AI Assistance**: Code generated with assistance from Claude/Cursor

## 📝 License

This project maintains the same license as the original [arxiv_daily_aigc](https://github.com/onion-liu/arxiv_daily_aigc) repository.

---

**Made with ❤️ for the Quantitative Finance Community**