# PPT 内容扩展智能体

## 一、项目简介

本项目面向考前复习场景：针对只有 PPT 标题、缺乏背景与细节的课件，构建一个可以自动扩展知识点的智能体系统。
用户上传 PPT 后，系统会解析 PPT 的层级结构，并基于向量检索与大模型，对每一页内容生成更完整的讲解、推导与延伸阅读建议。

## 二、核心功能

- 解析 PPT 文档的层级结构（目录、主标题、子标题、正文、图片说明等）
- 针对每个页面 / 知识点，自动调用 LLM 补充原理说明、公式推导或代码示例
- 通过向量检索 + 外部权威资源（Wikipedia / Arxiv 等），提供多维延伸阅读
- 以 Web 界面或 API 形式对外提供服务

## 三、技术选型概览

详见 `docs/jishuwendang.md` 或下表（节选）：

- 后端框架：FastAPI（异步、易于服务化）
- LLM：DeepSeek 云 API（可按需替换为其他云端模型）
- 向量库：Chroma（本地、轻量）
- 文档解析：Unstructured + python-pptx
- 外部知识源：Wikipedia / Arxiv
- 部署方式：Docker + docker-compose
- 协作与 CI：GitHub + GitHub Actions

## 四、系统架构（概览）

整体架构如下：

- 前端 / 客户端：负责文件上传与扩展内容展示
- 后端 API（FastAPI）：
  - 文档解析模块（PPT Parser）
  - Embedding Service + Chroma 向量库
  - LLM Agent（封装 DeepSeek LLM 调用）
  - External Knowledge Tool（访问 Wikipedia / Arxiv）

数据流向简要说明：

1. 用户上传 PPT 或提供链接；
2. 后端解析 PPT，提取每页标题、要点、备注等结构化信息；
3. 对各页面 / 切片生成向量，写入 Chroma 向量库；
4. 用户选择页面或发起“扩展讲解”请求时，后端基于向量检索召回相关内容；
5. LLM Agent 结合检索结果与外部知识源，生成扩展讲解并返回前端展示。

## 五、开发与运行（占位）

> 本节为占位内容，后续在功能实现后补充具体命令。

### 环境准备

```bash
# 创建虚拟环境（示例）
python -m venv venv
source venv/bin/activate  # Windows 使用: venv\Scripts\activate

pip install -r requirements.txt

本地运行：
# TODO: 在实现 FastAPI 后补充实际启动命令，例如：
# uvicorn app.main:app --reload

# 开发调试
python -m uvicorn backend.api:app --reload --host 127.0.0.1 --port 8000
# 稳定运行
python -m uvicorn backend.api:app --host 127.0.0.1 --port 8000

Docker运行  
# TODO: 在编写 Dockerfile 和 docker-compose.yml 后补充示例命令
# docker build -t ppt-agent .
# docker run -p 8000:8000 ppt-agent

# 必须在同一个终端窗口设置：
$env:SILICONFLOW_API_KEY="你的key"
$env:SILICONFLOW_BASE_URL="https://api.siliconflow.cn/v1"
$env:DEEPSEEK_MODEL="deepseek-ai/DeepSeek-V3.2-Exp"

# 之后构建并启动容器
docker compose up -d --build

```

### 打开网页
1. 打开导航页：
http://localhost:8000/ui/index.html

2. 测试健康检查：
http://localhost:8000/health