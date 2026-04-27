# New UI Preview - Quantitative Finance & AI Paper Tracker

## Page Header
```
╔══════════════════════════════════════════════════════════════════════╗
║                  Quantitative Finance & AI Daily Papers              ║
║                                                                      ║
║  Daily papers related to Algorithmic Trading, Quantitative Finance,  ║
║  and AI from q-fin.PM, q-fin.TR, cs.LG, cs.AI, and cs.CL            ║
║                                                                      ║
║  April 27, 2026                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

## Sample Paper Card (New Layout)

```
┌─────────────────────────────────────────────────────────────────────┐
│  Deep Reinforcement Learning for Portfolio Optimization            │
│                                                                      │
│  This paper applies deep reinforcement learning to portfolio        │
│  management, using price-volume data and achieving 15% annual       │
│  returns...                                                          │
│                                                                      │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                                      │
│  🔷 Methodology: Deep Reinforcement Learning (PPO)                 │
│                                                                      │
│  🔷 Data Sources: Price-volume data, transaction costs, market       │
│     microstructure                                                   │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 📈 ALPHA POTENTIAL                                           │   │
│  │                                                              │   │
│  │ Exploits temporal patterns in asset returns through          │   │
│  │ adaptive position sizing and risk-aware portfolio rebalancing│   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ★★★★★☆☆☆☆☆ Trading Relevance: (8/10)                             │
│                                                                      │
│  [DRL] [portfolio optimization] [risk management] [adaptive]       │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 中文摘要                                                      │   │
│  │                                                              │   │
│  │ 本文提出了一种基于深度强化学习的投资组合优化框架，通过自适应   │   │
│  │ 头寸调整和风险感知再平衡，在多个资产类别上实现了15%的年化收   │   │
│  │ 益，显著优于传统动量策略。                                      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  [📄 Read Paper (PDF)]                                              │
│                                                                      │
│  Authors: John Smith, Jane Doe                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Key UI Improvements

### Before (AIGC Version)
- Title and abstract only
- Generic star ratings
- TLDR summaries
- No context about trading applications

### After (Quant Finance Version)
- ✅ **Core Methodology** - What algorithm/approach
- ✅ **Data Sources** - What market data is used
- ✅ **Alpha Potential** (highlighted box) - Strategy logic
- ✅ **Trading Relevance Score** - Practical value
- ✅ **Visual Tags** - Quick topic identification
- ✅ **Chinese Summary** - Accessible to Chinese users

## Color Scheme
- **Primary (Teal):** #14b8a6 - Main highlights and links
- **Secondary (Cyan):** #67e8f9 - Accents
- **Alpha Box Background:** rgba(20, 184, 166, 0.1)
- **Alpha Box Border:** 3px solid #14b8a6
- **Tags:** Teal badges with rounded corners

## Data Flow

```
arXiv API (5 categories)
    ↓
Scraper Module
    ↓
LLM Filter (Senior Quant Researcher Persona)
    ↓
JSON Output with New Schema
    ↓
HTML Generator (Jinja2 Template)
    ↓
Daily HTML Report
```

## Example JSON Structure

```json
{
  "title": "Deep Reinforcement Learning for Portfolio Optimization",
  "summary": "This paper applies deep reinforcement learning...",
  "authors": ["John Smith", "Jane Doe"],
  "url": "https://arxiv.org/abs/2026.04027",
  "published_date": "2026-04-27T00:00:00Z",
  "relevance_score": 8,
  "core_methodology": "Deep Reinforcement Learning (PPO)",
  "data_sources": "Price-volume data, transaction costs",
  "alpha_potential": "Exploits temporal patterns in asset returns...",
  "tags": ["DRL", "portfolio optimization", "risk management"],
  "summary_cn": "本文提出了一种基于深度强化学习的投资组合优化框架..."
}
```

---
**Status:** Ready for deployment
