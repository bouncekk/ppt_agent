| 模块     | 选型                         | 说明       |
| ------ | -------------------------- | -------- |
| 后端框架   | FastAPI                    | 异步 + 服务化 |
| LLM    | DeepSeek 云 API             | 可替换      |
| 向量库    | Chroma                     | 本地、轻量    |
| PPT 解析 | Unstructured + python-pptx | 稳妥       |
| 外部知识   | Wikipedia / Arxiv          | 权威       |
| 部署     | Docker + docker-compose    | 云原生      |
| 协作     | GitHub + Actions           | 工程化      |


架构图：
```
[ Frontend ]
     |
     v
[ Backend API (FastAPI) ]
     |
     |-- 文档解析模块 (PPT Parser)
     |
     |-- Embedding Service
     |       |
     |       v
     |   [ Vector DB (Chroma) ]
     |
     |-- LLM Agent
     |       |
     |       v
     |   [ LLM API (DeepSeek) ]
     |
     |-- External Knowledge Tool
             |
             v
        [ Wikipedia / Arxiv ]
```

- **技术选型表**：
  明确了后端框架（FastAPI）、LLM 提供方（DeepSeek 云 API）、向量库（Chroma）、PPT 解析组件（Unstructured + python-pptx）、外部知识源（Wikipedia / Arxiv）、部署方案（Docker + docker-compose）以及协作方式（GitHub + Actions）。

- **系统架构图（初版）**：
  已给出“前端 → FastAPI 后端 → 解析模块 / 向量库 / LLM Agent / 外部知识工具”的整体调用关系，体现出：
  - 各核心能力（解析、Embedding、检索、推理、外部知识）解耦为独立模块；
  - 向量库作为语义检索的核心数据服务；
  - LLM Agent 与外部知识工具之间通过工具调用的方式进行集成。

- **数据流向说明**：
  - 用户上传 PPT（或提供链接）到 Frontend；
  - Frontend 调用 Backend API，将 PPT 交给文档解析模块，抽取出页面、标题、要点等结构化数据；
  - Embedding Service 对解析后的切片生成向量并写入 Chroma 向量库；
  - 当用户选择某一页或发起扩展请求时，后端基于向量检索召回相关内容，交由 LLM Agent 结合 DeepSeek LLM 生成扩展讲解，并按页面返回给前端展示；
  - 如需延伸阅读，Agent 通过 External Knowledge Tool 调用 Wikipedia / Arxiv，补充相关参考资料。

- **代码仓库与协作流程初始化**：
  - 在 GitHub 创建项目仓库，约定基本分支策略（如 `main` + `dev`），并配置基础的 `.gitignore`；
  - 预留 GitHub Actions 工作流入口（如 CI 占位文件），后续可以逐步完善自动测试与构建；
  - README 草稿：包含项目简介、技术选型表引用、架构图链接以及环境准备的初步说明。



