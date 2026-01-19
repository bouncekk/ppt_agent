from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from core.ppt_parser import Slide, parse_ppt
from core.vector_store import index_ppt_file, query_similar_slides
from core.llm_agent import AgentConfig, expand_slide_with_tools


# 以项目根目录 ppt_agent 为基准
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


app = FastAPI(title="PPT Agent Backend", version="0.1.0")


# 简单的内存存储：ppt_id -> List[Slide]
PPT_SLIDES: Dict[str, List[Slide]] = {}


class SlideOut(BaseModel):
    index: int
    title: str
    bullets: List[str]
    notes: Optional[str] = None


class UploadResponse(BaseModel):
    ppt_id: str
    filename: str
    num_slides: int


class SearchHit(BaseModel):
    ppt_id: str
    slide_index: int
    title: str
    score: float
    snippet: str


class ExpandResponse(BaseModel):
    ppt_id: str
    slide_index: int
    title: str
    expanded_markdown: str


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """后端健康检查接口。"""

    return {"status": "ok"}


@app.post("/upload", response_model=UploadResponse)
async def upload_ppt(file: UploadFile = File(...)) -> UploadResponse:
    """上传 PPT 文件，解析并写入向量库。

    返回生成的 ppt_id 以及解析到的页数。
    """

    if not file.filename.lower().endswith(".pptx"):
        raise HTTPException(status_code=400, detail="仅支持 .pptx 文件")

    ppt_id = uuid4().hex
    dest_path = UPLOAD_DIR / f"{ppt_id}.pptx"

    content = await file.read()
    dest_path.write_bytes(content)

    # 解析 PPT 并写入向量库
    slides = parse_ppt(dest_path)
    PPT_SLIDES[ppt_id] = slides
    index_ppt_file(dest_path, ppt_id=ppt_id)

    return UploadResponse(ppt_id=ppt_id, filename=file.filename, num_slides=len(slides))


@app.get("/slides", response_model=List[SlideOut])
async def list_slides(ppt_id: str = Query(..., description="上传返回的 PPT 标识")) -> List[SlideOut]:
    """列出某个 PPT 的所有页面结构。"""

    slides = PPT_SLIDES.get(ppt_id)
    if slides is None:
        raise HTTPException(status_code=404, detail="ppt_id 未找到，请先上传 PPT")

    return [
        SlideOut(index=s.index, title=s.title, bullets=s.bullets, notes=s.notes)
        for s in slides
    ]


@app.get("/search", response_model=List[SearchHit])
async def search_slides(
    ppt_id: str = Query(..., description="目标 PPT 标识"),
    q: str = Query(..., description="查询语句，如某个知识点关键词"),
    top_k: int = Query(5, ge=1, le=20, description="返回的最大结果数"),
) -> List[SearchHit]:
    """在指定 PPT 内进行语义检索，返回最相关的若干页面。"""

    if not q.strip():
        raise HTTPException(status_code=400, detail="查询语句不能为空")

    # 初步检索更多结果，再按 ppt_id 过滤
    raw = query_similar_slides(q, n_results=top_k * 3)
    ids_batch = raw.get("ids", [[]])[0]
    metas_batch = raw.get("metadatas", [[]])[0]
    docs_batch = raw.get("documents", [[]])[0]
    dists_batch = raw.get("distances", [[]])[0]

    hits: List[SearchHit] = []
    for sid, meta, doc, dist in zip(ids_batch, metas_batch, docs_batch, dists_batch):
        if not isinstance(meta, dict):
            continue
        if meta.get("ppt_id") != ppt_id:
            continue
        hits.append(
            SearchHit(
                ppt_id=ppt_id,
                slide_index=int(meta.get("slide_index", 0)),
                title=str(meta.get("title", "")),
                score=float(dist),
                snippet=doc[:300],
            )
        )
        if len(hits) >= top_k:
            break

    return hits


@app.get("/expand", response_model=ExpandResponse)
async def expand_slide(
    ppt_id: str = Query(..., description="目标 PPT 标识"),
    slide_index: int = Query(..., ge=1, description="要扩展的页面索引（从 1 开始）"),
    use_wikipedia: bool = Query(True, description="是否启用 Wikipedia 外部知识"),
) -> ExpandResponse:
    """为指定 PPT 的某一页生成扩展讲解（调用 Agent + Checklayer）。"""

    slides = PPT_SLIDES.get(ppt_id)
    if slides is None:
        raise HTTPException(status_code=404, detail="ppt_id 未找到，请先上传 PPT")

    slide_map = {s.index: s for s in slides}
    slide = slide_map.get(slide_index)
    if slide is None:
        raise HTTPException(status_code=404, detail="指定的 slide_index 不存在")

    cfg = AgentConfig(use_wikipedia=use_wikipedia, top_k_slides=5, top_k_wiki=3)
    expanded = expand_slide_with_tools(slide, config=cfg)

    return ExpandResponse(
        ppt_id=ppt_id,
        slide_index=slide.index,
        title=slide.title,
        expanded_markdown=expanded,
    )
