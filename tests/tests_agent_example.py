"""阶段四：LLM Agent 与工具链的本地演示脚本。

该脚本串联：
- PPT 解析 (ppt_parser.parse_ppt)
- 向量检索 (vector_store.index_ppt_file / query_similar_slides)
- Wikipedia 外部知识 (external_knowledge.search_wikipedia)
- Agent 扩展逻辑 (llm_agent.expand_slide_with_tools)

在未配置 DEEPSEEK_API_KEY 时，会输出占位内容，
但整体数据流与真实部署时一致，可用于演示“推理链路”。
"""

from __future__ import annotations

from pathlib import Path

from core.ppt_parser import parse_ppt
from core.vector_store import index_ppt_file
from core.llm_agent import expand_slide_with_tools, AgentConfig


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    ppt_path = base_dir / "examples" / "sample.pptx"

    if not ppt_path.exists():
        raise FileNotFoundError(
            f"示例 PPT 不存在: {ppt_path}，请在 examples/ 下放置 sample.pptx 后再运行本示例。"
        )

    print("[info] 使用 PPT:", ppt_path)

    # 1. 解析 PPT 并写入向量库（如已写入，可多次调用，不影响演示）
    slides = parse_ppt(ppt_path)
    print(f"[info] 解析得到 {len(slides)} 页 slide，将写入向量库用于内部检索……")
    index_ppt_file(ppt_path, ppt_id="sample")

    # 2. 选取第一页作为示例，调用 Agent 进行扩展
    slide = slides[0]
    print(f"[info] 选取示例页面: index={slide.index}, title={slide.title!r}")

    cfg = AgentConfig(use_wikipedia=True, top_k_slides=3, top_k_wiki=2)
    expanded = expand_slide_with_tools(slide, config=cfg)

    print("\n===== Agent 扩展结果 (示例) =====\n")
    print(expanded)


if __name__ == "__main__":
    main()
