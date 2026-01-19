"""阶段三：向量化存储与语义检索的本地跑通示例。

该脚本假定：
- 已经在 examples/ 目录下准备好 sample.pptx；
- parse_ppt 能够正确解析 PPT 为 Slide 列表；
- 已安装 chromadb（本地向量库）；

运行方式（在项目根目录 ppt_agent/ 下）：

    python tests_vector_store_example.py

运行后将：
- 使用 ppt_parser.parse_ppt 解析 examples/sample.pptx；
- 调用 vector_store.index_ppt_file 将 Slide 列表写入本地 Chroma；
- 针对一个示例查询语句（如 "云计算"）做一次语义检索，并打印检索到的切片信息。
"""

from __future__ import annotations

from pathlib import Path

from core.ppt_parser import parse_ppt
from core.vector_store import index_ppt_file, query_similar_slides


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    ppt_path = base_dir / "examples" / "sample.pptx"

    if not ppt_path.exists():
        raise FileNotFoundError(
            f"示例 PPT 不存在: {ppt_path}，请在 examples/ 下放置 sample.pptx 后再运行本示例。"
        )

    print("[info] 使用 PPT:", ppt_path)

    # 1. 解析 PPT
    slides = parse_ppt(ppt_path)
    print(f"[info] 解析得到 {len(slides)} 页 slide，将写入向量库……")

    # 2. 写入 Chroma 本地向量库
    index_ppt_file(ppt_path, ppt_id="sample")
    print("[ok] 已将解析结果写入本地 Chroma 向量库 (collection=ppt_slides)。")

    # 3. 进行一次示例查询
    query_text = "云计算"
    print(f"[info] 示例查询语句: {query_text!r}")
    results = query_similar_slides(query_text, n_results=5)

    ids = results.get("ids", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    print("[info] 检索结果（按相似度排序）：")
    for sid, meta, dist in zip(ids, metadatas, distances):
        title = meta.get("title") if isinstance(meta, dict) else None
        slide_index = meta.get("slide_index") if isinstance(meta, dict) else None
        print(f"  - id={sid}, slide_index={slide_index}, title={title}, distance={dist}")


if __name__ == "__main__":
    main()
