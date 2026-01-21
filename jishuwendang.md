## 《智能体云原⽣开发》期末⼤作业 —— PPT内容扩展智能体

分工：       
**10235501442尹中成**：架构设计、LLMAgent设计、后端接口实现、实验文档。占比50%。       
**10235501407周雍佳**：docker容器化实现、前端搭建、实验文档、演示视频。占比50%。      

具体实现流程/分工：


项目结构：


项目介绍：



### 一、技术选型
| 模块     | 选型                         |
| ------ | -------------------------- | 
| 后端框架   | FastAPI                    |
| LLM    | DeepSeek 云 API（deepseek-ai/DeepSeek-V3.2-Exp模型）          | 
| 向量库    | Chroma                     | 
| PPT 解析 | python-pptx | 
| 外部知识   | Wikipedia        | 
| 部署     | Docker + docker-compose    | 
| 协作     | GitHub + Actions           | 


**架构图**：
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
     |   [ Checklayer ]
     |       |
     |       v
     |   [ LLM API (DeepSeek) ]
     |
     |-- External Knowledge Tool
             |
             v
        [ Wikipedia / Arxiv ]
```


## 技术原理： 
对 Embedding 的解释

嵌入模型用于将 PPT 中的文本内容映射到向量空间，使语义相近的知识点在向量空间中距离更近，从而支持基于语义的相关性检索。

对 Vector DB 的解释

向量数据库用于存储嵌入向量，并支持高效的相似度搜索，作为系统的长期语义记忆层，为智能体提供上下文支持。Vector DB 的角色是：防止 LLM 胡说

- **系统架构图说明**：
- PPT 页面
  ↓
文档解析（结构化）
  ↓
Embedding
  ↓
Vector DB（长期记忆）
  ↓
基于当前页做语义检索
  ↓
将【检索结果 + 当前页】交给 LLM
  ↓
生成补充说明

  已给出“前端 → FastAPI 后端 → 解析模块 / 向量库 / LLM Agent + Checklayer / 外部知识工具”的整体调用关系，体现出：
  - 各核心能力解耦为独立模块；
  - 向量库作为语义检索的核心数据服务；
  - LLM Agent 通过 Checklayer 对生成结果进行一致性与事实性检查，并与外部知识工具之间通过工具调用的方式进行集成。

- **数据流向说明**：
  - 用户上传 PPT（或提供链接）到 Frontend；
  - Frontend 调用 Backend API，将 PPT 交给文档解析模块，抽取出页面、标题、要点等结构化数据；
  - Embedding Service 对解析后的切片生成向量并写入 Chroma 向量库；
  - 当用户选择某一页或发起扩展请求时，后端基于向量检索召回相关内容，交由 LLM Agent 结合 DeepSeek LLM 生成扩展讲解；
  - 生成结果先经过 Checklayer，对逻辑一致性、与检索结果/外部资料的匹配度进行校验与修正；
  - 通过 Checklayer 后的内容按页面返回给前端展示；
  - 如需延伸阅读或事实校验，Agent 通过 External Knowledge Tool 调用 Wikipedia / Arxiv，补充相关参考资料。

- **云原⽣组件**（如Docker、K8S、Redis,Serverless、微服务等）：




## LLM Agent 设计

### 工具链与模块划分

- **PPT 解析工具（`ppt_parser.py`）**：
  - 提供 `Slide` 数据结构（index、title、bullets、notes）。
  - `parse_ppt(path)`：基于 `python-pptx` 将 `.pptx` 解析为 `List[Slide]`。
  - `parse_ppt_to_json_file`：用于生成“PPT → JSON”的结构化输出样例。

- **Embedding / 检索工具（`vector_store.py`）**：
  - 封装本地 Chroma 向量库（`PersistentClient`，存储于 `chroma_db/`）。
  - `slide_to_document(slide)`：将单页 `Slide` 拼接为用于向量化的文本。
  - `index_ppt_file(ppt_path, ppt_id)`：解析并写入向量库，形成内部检索索引。
  - `query_similar_slides(query_text, n_results)`：基于语义相似度返回相关页 ids、documents 与 metadatas。

- **外部知识工具（`external_knowledge.py`）**：
  - `search_wikipedia(query, max_results)`：调用 Wikipedia 公开 API，返回若干条“【条目】摘要”文本片段，作为延伸阅读与事实补充；
  - 目前仅接入 Wikipedia，接口已预留，后续可扩展接入 Arxiv 等学术源。

- **LLM Agent 与 Checklayer（`llm_agent.py`）**：
  - `AgentConfig`：
    - `use_wikipedia`：是否启用外部知识检索；
    - `top_k_slides`：内部向量检索召回的相关页数量；
    - `top_k_wiki`：Wikipedia 外部知识召回的片段数量。
  - `build_slide_context_from_retrieval(slide, top_k)`：
    - 基于当前页标题在 Chroma 中做一次语义检索，
    - 将召回的相关页 index、title 与正文拼接为“内部上下文块”。
  - `expand_slide_with_tools(slide, config)`：
    - 调用内部检索与 `search_wikipedia`，组装上下文；
    - 基于 Prompt 模板构造请求，最终通过 `call_llm` 访问 DeepSeek LLM；
    - 作为“PPT 单页 → 扩展讲解”的统一入口。
  - `call_llm(prompt)`：
    - 使用 `langchain_openai.ChatOpenAI` 客户端，通过硅基流动的 OpenAI 兼容接口调用 `deepseek-ai/DeepSeek-V3.2-Exp`；
    - API Key、Base URL、模型名均通过环境变量 `SILICONFLOW_API_KEY`、`SILICONFLOW_BASE_URL`、`DEEPSEEK_MODEL` 配置，避免硬编码密钥；
    - 在网络不可达或配置异常时回退为“占位输出”，保证链路可演示。

### Prompt 模板与 Checklayer 设计

`build_prompt_for_slide_expansion` 将当前页 `Slide`、内部检索结果与 Wikipedia 片段组合为一个结构化 Prompt，核心结构如下：

- **输入信息块**：
  - 【当前 PPT 页面】：包含 index、title、bullets、notes；
  - 【PPT 内部相关页面（检索得到）】：由向量检索返回的相关页内容；
  - 【Wikipedia 外部知识片段】：由 `search_wikipedia` 返回的条目摘要。

- **输出目标**：
  - 要求 LLM 生成“扩展讲解笔记”，分为 4 个部分：
    1. 背景说明；
    2. 知识点详细解释（可含公式/关键步骤）；
    3. 示例（代码或生活类比）；
    4. 延伸阅读建议；
  - 输出格式为中文 Markdown，小标题分段。

- **Checklayer（提示词层面的两阶段设计）**：
  - 在 Prompt 开头显式要求模型先执行两步检查：
    1. **Self-consistency 检查**：对即将输出的要点、公式和示例代码进行自我审查，避免前后矛盾、逻辑不一致或同一段内容被多次重复；
    2. **事实与上下文校验**：对照“内部相关页面”和“Wikipedia 片段”，检查关键结论是否明显违背上下文，对不确定内容标注“可能/待查证”，避免给出确定性的错误结论。

- **风格与安全约束**：
  - 强调与原 PPT 标题和要点保持语义一致，不偏题；
  - 如不确定某个细节，要求使用“可能”等措辞，而不是直接编造结论；
  - 明确要求“示例代码只给出一份，保持简洁，不要多次重复相同训练/预测语句或完全相同代码块”；
  - 要求优先参考检索结果与 Wikipedia 片段，避免产生明显“离谱”的内容。

通过上述工具链与 Prompt 设计，LLM Agent 在回答时能够同时利用：
- PPT 内部结构化内容与语义检索结果；
- Wikipedia 外部知识补充；
- 提示词级 Checklayer 对一致性与事实性的约束，

从而为每一页 PPT 生成更完整、可解释、可追溯的数据扩展讲解。

## docker？