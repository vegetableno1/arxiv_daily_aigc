import os
import requests
import time
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 从环境变量中获取 OpenRouter API Key
# 在 GitHub Actions 中，这应该设置为 Secret
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# 可以选择一个合适的模型，例如免费或低成本的模型进行分类任务
# 查阅 OpenRouter 文档获取可用模型列表: https://openrouter.ai/docs#models
# 例如使用 'mistralai/mistral-7b-instruct:free'
MODEL_NAME = "google/gemini-2.0-flash-001"

def call_openrouter_api(prompt: str, max_tokens: int = 5) -> str | None:
    """调用 OpenRouter API 并返回模型的响应。

    Args:
        prompt (str): 发送给模型的提示。
        max_tokens (int): 限制模型响应的最大 token 数。

    Returns:
        str | None: 模型的响应文本，如果发生错误则返回 None。
    """
    if not OPENROUTER_API_KEY:
        logging.error("未设置 OPENROUTER_API_KEY 环境变量。无法调用 API。")
        return None

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens
    }

    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=data, timeout=30) # 设置超时
        response.raise_for_status()  # 如果请求失败 (状态码 >= 400)，则抛出 HTTPError

        result = response.json()
        ai_response = result['choices'][0]['message']['content'].strip()
        return ai_response

    except requests.exceptions.RequestException as e:
        logging.error(f"调用 OpenRouter API 时出错: {e}")
        return None
    except (KeyError, IndexError) as e:
        logging.error(f"解析 OpenRouter API 响应时出错: {e}")
        return None
    except Exception as e:
        logging.error(f"调用 OpenRouter API 时发生意外错误: {e}", exc_info=True)
        return None

def filter_papers_by_topic(papers: list, topic: str = "algorithmic trading, quantitative finance, or AI applied to financial markets") -> list:
    """使用 OpenRouter API 过滤论文列表，只保留与指定主题相关的论文。

    Args:
        papers (list): 包含论文信息的字典列表，每个字典应包含 'title' 和 'summary'。
        topic (str): 需要过滤的主题，默认为 "algorithmic trading, quantitative finance, or AI applied to financial markets"。

    Returns:
        list: 只包含与主题相关论文的字典列表。
    """
    if not OPENROUTER_API_KEY:
        logging.error("未设置 OPENROUTER_API_KEY 环境变量。无法进行过滤。")
        # 在没有 API Key 的情况下，可以选择返回原始列表或空列表
        # 这里返回原始列表，以便流程继续，但会跳过过滤
        return papers

    filtered_papers = []
    logging.info(f"开始使用 OpenRouter API 过滤 {len(papers)} 篇论文，主题: '{topic}'...")

    for i, paper in enumerate(papers):
        title = paper.get('title', 'N/A')
        summary = paper.get('summary', 'N/A')

        # 构建 Prompt
        prompt = f"""You are evaluating academic papers for a quantitative trading research team.

Determine if this paper has ANY relevance to: {topic}

Consider it relevant if the paper:
- Applies to algorithmic trading, quantitative finance, or financial markets
- Uses methodologies (AI/ML, statistical, mathematical) that could be applied to trading
- Deals with financial data, market analysis, or decision-making under uncertainty
- Explores time series prediction, pattern recognition, or optimization

Paper Title: {title}
Abstract: {summary}

Answer with ONLY 'yes' or 'no'."""

        # 调用封装好的 API 函数
        ai_response = call_openrouter_api(prompt, max_tokens=5)

        if ai_response is not None:
            logging.info(f"论文 {i+1}/{len(papers)}: '{title[:50]}...' - AI 回复: {ai_response}")
            if 'yes' in ai_response.lower():
                filtered_papers.append(paper)
            # OpenRouter 对免费模型的速率有限制，可以考虑在 call_openrouter_api 内部或外部添加延时
            # time.sleep(1) # 暂停 1 秒
        else:
            logging.warning(f"无法获取论文 '{title[:50]}...' 的 AI 回复，跳过此论文。")
            continue # 跳过出错的论文

    logging.info(f"过滤完成，找到 {len(filtered_papers)} 篇与 '{topic}' 相关的论文。")
    return filtered_papers


rating_prompt_template = """
# Role Setting
You are a Senior Quantitative Researcher with expertise in algorithmic trading, quantitative finance, and AI applied to financial markets. You are skilled at quickly evaluating the practical value of research papers for real-world trading strategies.

# Task
Based on the following paper's title and abstract, evaluate its relevance and potential for quantitative trading and financial applications. Return null if the paper is completely irrelevant to algorithmic trading, quantitative finance, or AI applied to markets.

# Input
Paper Title: %s
Paper Abstract: %s

# Research Focus Areas
Quantitative Finance: momentum strategies, dual momentum, barbell strategies, factor investing, arbitrage, portfolio optimization, market microstructure
AI/ML Applications: LLMs, agents, RAG (Retrieval-Augmented Generation), Graph Neural Networks (GNN), Reinforcement Learning, Transformers applied to financial data

# Output Requirements
Output should always be in JSON format, strictly compliant with RFC8259.
Return null if the paper is completely irrelevant to quantitative finance or AI in trading.
Otherwise, output the evaluation in the following JSON format:
{
  "relevance_score": <Integer 1-10 indicating practical value for real-world trading>,
  "core_methodology": "<String: The core algorithm or method, e.g., GNN, Transformer, Dual Momentum, RAG, Reinforcement Learning, Statistical Arbitrage>",
  "data_sources": "<String: Data used in the paper, e.g., LOB data, earnings reports, price-volume data, alternative data, news sentiment, multi-modal data>",
  "alpha_potential": "<String: 1-sentence summary of the alpha source or strategy logic>",
  "tags": ["<Array of 2-4 string tags, e.g., 'momentum', 'GNN', 'alternative data', 'portfolio optimization'>"],
  "title_cn": "<String: Chinese translation of the paper title>",
  "summary_cn": "<String: A high-quality Chinese summary under 100 words focusing on practical trading applications>"
}

# Scoring Guidelines
- Relevance Score (1-10): Focus on practical applicability to real-world trading and quantitative finance
  * 9-10: Directly applicable trading strategy with clear alpha potential
  * 7-8: Strong methodology with clear path to trading applications
  * 5-6: Relevant but theoretical or requires significant adaptation
  * 3-4: Tangentially related to finance/trading
  * 1-2: Minimal practical relevance
  * Return null if completely unrelated to quantitative finance or AI in trading

- Core Methodology: Identify the main algorithmic approach (e.g., GNN for relational data, Transformer for sequence modeling, Dual Momentum for trend following, RAG for knowledge-enhanced decisions)

- Data Sources: Specify what market or alternative data is used (e.g., limit order book data, options flow, earnings call transcripts, satellite imagery, social media sentiment)

- Alpha Potential: Concisely explain the market inefficiency or signal source being exploited

- Tags: Include 2-4 relevant keywords covering methodology, data type, and application area

- Title Translation: Translate the paper title into professional, concise Chinese

- Chinese Summary: Provide a high-quality Chinese translation in under 100 words, focusing on practical trading applications and methodologies
"""


def rate_papers(papers: list) -> list:
    """使用 OpenRouter API 对论文进行评分，返回一个包含评分的字典列表。
    Args:
        papers (list): 包含论文信息的字典列表，每个字典应包含 'title' 和'summary'。
    Returns:
        list: 包含论文评分的字典列表，每个字典包含 'title', 'summary', 和量化相关的评分字段。
              对于完全不相关的论文，会被跳过。
    """
    if not OPENROUTER_API_KEY:
        logging.error("未设置 OPENROUTER_API_KEY 环境变量。无法进行评分。")
        # 在没有 API Key 的情况下，可以选择返回原始列表或空列表
        # 这里返回原始列表，以便流程继续，但会跳过评分
        return papers

    logging.info(f"开始使用 OpenRouter API 对 {len(papers)} 篇论文进行评分...")
    for i, paper in enumerate(papers):
        title = paper.get('title', 'N/A')
        summary = paper.get('summary', 'N/A')
        # 构建 Prompt
        prompt = rating_prompt_template % (title, summary)

        # 添加重试逻辑 (最多尝试 2 次)
        success = False
        for attempt in range(2):
            # 调用封装好的 API 函数
            ai_response = call_openrouter_api(prompt, max_tokens=1000)

            if ai_response is not None:
                # 检查是否是有效的 JSON 响应
                try:
                    # 尝试解析 JSON 响应
                    # 1. 去掉字符串中的非 JSON 内容 (如果存在)
                    if '```json' in ai_response:
                        ai_response = ai_response.split('```json')[1].split('```')[0]
                    # 2. json加载
                    rating_data = json.loads(ai_response)

                    # Check if the paper was marked as irrelevant (null response)
                    if rating_data is None or (isinstance(rating_data, dict) and not rating_data):
                        logging.info(f"论文 {i+1}/{len(papers)} (尝试 {attempt+1}): '{title[:50]}...' - 标记为不相关，跳过")
                        success = True
                        # Mark this paper for removal
                        papers[i]['_skip'] = True
                        break # 成功获取并解析，跳出重试循环

                    logging.info(f"论文 {i+1}/{len(papers)} (尝试 {attempt+1}): '{title[:50]}...' - AI Rating: {rating_data}")
                    papers[i].update(rating_data)
                    success = True
                    break # 成功获取并解析，跳出重试循环
                except json.JSONDecodeError:
                    logging.warning(f"论文 {i+1}/{len(papers)} (尝试 {attempt+1}): '{title[:50]}...' - AI 回复不是有效的 JSON: {ai_response[:100]}...")
                    # JSON 解析失败，继续重试 (如果还有尝试次数)
                except Exception as e:
                    logging.error(f"论文 {i+1}/{len(papers)} (尝试 {attempt+1}): '{title[:50]}...' - 解析响应时发生意外错误: {e}", exc_info=True)
                    # 其他解析错误，继续重试 (如果还有尝试次数)
            else:
                logging.warning(f"论文 {i+1}/{len(papers)} (尝试 {attempt+1}): 无法获取论文 '{title[:50]}...' 的 AI Rating (API 返回 None)。")
                # API 调用失败，继续重试 (如果还有尝试次数)

            # 如果不是最后一次尝试，则等待后重试
            if attempt < 1:
                logging.info(f"论文 {i+1}/{len(papers)}: 重试...")

        # 如果两次尝试都失败了
        if not success:
            logging.error(f"论文 {i+1}/{len(papers)}: 两次尝试均未能成功获取和解析 '{title[:50]}...' 的评分，跳过此论文。")
            continue # 跳过出错的论文

    # Filter out papers marked as irrelevant or that failed to rate
    filtered_papers = [paper for paper in papers if not paper.get('_skip', False)]

    logging.info(f"评分完成。保留 {len(filtered_papers)} 篇相关论文。")
    return filtered_papers


# 可以在这里添加一些测试代码
if __name__ == '__main__':
    # 确保设置了 OPENROUTER_API_KEY 环境变量才能运行测试
    if OPENROUTER_API_KEY:
        test_papers = [
            {
                'title': 'Deep Reinforcement Learning for Portfolio Optimization',
                'summary': 'This paper applies deep reinforcement learning to portfolio management, using price-volume data and achieving 15% annual returns...'
            },
            {
                'title': 'Graph Neural Networks for Limit Order Book Modeling',
                'summary': 'We propose a GNN architecture to model limit order book dynamics, achieving state-of-the-art results on high-frequency trading prediction tasks.'
            },
            {
                'title': 'Climate Change Effects on Crop Yields in Sub-Saharan Africa',
                'summary': 'This study examines the impact of climate change on agricultural productivity using satellite imagery and weather data.'
            }
        ]
        logging.info("\n--- 开始测试 filter_papers_by_topic --- ")
        filtered = filter_papers_by_topic(test_papers)
        rated = rate_papers(filtered)

        logging.info("\n--- 过滤后的论文 --- ")
        for paper in filtered:
            logging.info(f"- {paper['title']}\t{paper.get('overall_priority_score', None)}")
        logging.info("--- 测试结束 ---")
    else:
        logging.warning("请设置 OPENROUTER_API_KEY 环境变量以运行测试。")
