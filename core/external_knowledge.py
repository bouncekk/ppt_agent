"""外部知识工具：目前只实现 Wikipedia 搜索。

后续如需扩展 Arxiv 等学术资源，可以在本文件中继续增加工具函数，
保持 Agent 通过统一的工具接口访问外部知识。"""

from __future__ import annotations

from typing import List

import requests

WIKIPEDIA_API_URL = "https://zh.wikipedia.org/w/api.php"


def search_wikipedia(query: str, max_results: int = 3) -> List[str]:
    """使用 Wikipedia 的公开 API 搜索条目并返回简介片段列表。

    当前使用 zh.wikipedia.org 的简体中文站点，不需要 API Key。
    返回的每个字符串可以直接拼接进 LLM 提示词，作为外部背景知识。
    """

    if not query.strip():
        return []

    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": max_results,
        "utf8": 1,
    }

    try:
        resp = requests.get(WIKIPEDIA_API_URL, params=params, timeout=10)
        resp.raise_for_status()
    except Exception:
        # 外部请求失败时，Agent 仍应能工作，只是缺少扩展知识
        return []

    data = resp.json()
    results = []
    for item in data.get("query", {}).get("search", []):
        title = item.get("title", "")
        snippet = item.get("snippet", "")
        # Wikipedia 返回的 snippet 含有 HTML，高亮标签简单去掉
        snippet_clean = (
            snippet.replace("<span class=\"searchmatch\">", "")
            .replace("</span>", "")
            .replace("<", " ")
            .replace(">", " ")
        )
        results.append(f"【{title}】{snippet_clean}")

    return results
