# 🤖 AIGC 智能体助手（本地LLM + 联网搜索 + 文生图）

> 一个基于本地大模型（LM Studio）的对话式智能体，支持工具调用（Function Calling），实现联网搜索和文生图，提供简洁的Web聊天界面。

## 📌 项目特点

- **完全本地化**：大模型运行在本地（LM Studio），无需联网，隐私安全，零成本。
- **智能工具调用**：模型自主决定调用搜索或画图工具，支持多轮对话记忆。
- **免费搜索**：集成 DuckDuckGo 搜索，无需 API Key。
- **文生图能力**：接入智谱 CogView-3-Flash API，一句话生成图片并保存本地。
- **Web 界面**：基于 Flask，开箱即用，支持多会话历史。
- **工程完整**：包含错误处理、日志打印、会话管理。

## 🛠️ 技术栈

| 模块 | 技术 |
|------|------|
| 大模型 | LM Studio + Qwen2.5-7B-Instruct（可替换其他） |
| 搜索 | `ddgs` (DuckDuckGo) |
| 文生图 | 智谱 AI `cogview-3-flash` |
| Web框架 | Flask |
| 工具调用 | OpenAI Function Calling 兼容接口 |
| 环境管理 | `python-dotenv` |

## 🚀 快速开始

### 1. 环境要求
- Python 3.10 或更高版本
- 安装 [LM Studio](https://lmstudio.ai/) 并下载一个支持 Function Calling 的模型（如 Qwen2.5-7B-Instruct）
- 智谱 AI API Key（[获取地址](https://open.bigmodel.cn/)）

### 2. 克隆项目
git clone https://github.com/BenSimmons66/AIGC-Agent.git
cd AIGC-Agent

3. 安装依赖
pip install -r requirements.txt
4. 配置环境变量
复制 .env.example 为 .env（或直接创建），写入：
ZHIPU_API_KEY=你的智谱API密钥

5. 启动 LM Studio
打开 LM Studio → 加载你的模型（例如 qwen2.5-7b-instruct-1m）

点击左侧 <> (Developer) → 启动 Local Inference Server

确认端口为 1234，访问 http://localhost:1234/v1/models 测试

6. 运行 Web 服务
bash
python app.py
打开浏览器访问 http://127.0.0.1:7860 即可使用。

🎮 使用示例
在输入框输入：

搜索今天的人工智能新闻

生成一张赛博朋克风格的城市夜景，保存为 cyberpunk.png

智能体会自动调用相应工具，并将结果展示在聊天框中。

📁 项目结构
text
.
├── app.py                 # Flask Web 界面
├── agent.py               # 智能体核心逻辑（工具调用、搜索、生图）
├── requirements.txt       # 依赖列表
├── .env.example           # 环境变量示例（需复制为.env）
├── .gitignore
└── README.md
🔧 可能的问题与解决
问题	解决方案
搜索时出错 DuckDuckGo 搜索时出错	可能是网络无法访问 DuckDuckGo，可尝试更换搜索引擎（如百度爬虫或 Brave API）。
LM Studio 连接失败	检查是否启动了 Local Inference Server，端口是否为 1234。
模型不调用工具	确认模型支持 Function Calling（推荐 Qwen 系列），或调整 System Prompt。
📝 后续优化方向
支持流式输出（SSE）

加入本地 OpenSerp 搜索服务

对话历史持久化（SQLite）

打包为 Docker 镜像

📄 许可证
MIT