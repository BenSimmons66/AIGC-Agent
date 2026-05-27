import os
import json
import requests
import time
from openai import OpenAI
from dotenv import load_dotenv
from ddgs import DDGS

# ================= 初始化 =================
load_dotenv()
zhipu_api_key = os.getenv("ZHIPU_API_KEY")

local_llm = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio",
)

# ================= 工具函数 =================
def call_zhipu_image_generation(prompt: str, save_name: str) -> str:
    """调用智谱AI的文生图API,并保存图片到本地。"""
    print(f" 正在生成图片：{prompt}...")
    url = "https://open.bigmodel.cn/api/paas/v4/images/generations"
    headers = {
        "Authorization": f"Bearer {zhipu_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "cogview-3-flash",
        "prompt": prompt,
        "size": "1024x1024",
        "n": 1
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code != 200:
            return f"生成失败: {response.text}"
        img_url = response.json()["data"][0]["url"]
        img_data = requests.get(img_url, timeout=30).content
        os.makedirs("generated_images", exist_ok=True)
        save_path = os.path.join("generated_images", save_name)
        with open(save_path, "wb") as f:
            f.write(img_data)
        print(f" 图片已保存: {save_path}")
        return f"图片已保存到 {save_path}"
    except Exception as e:
        return f"生成图片时出错: {e}"

def web_search(query: str, max_results: int = 5) -> str:
    """使用 DuckDuckGo (ddgs) 进行免费网络搜索。"""
    print(f"🔍 正在使用 DuckDuckGo 搜索：{query}")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            if not results:
                return "未找到相关信息。"

            formatted = []
            for r in results[:max_results]:
                title = r.get('title', '无标题')
                body = r.get('body', '')[:200]
                href = r.get('href', '#')
                title = title.replace('\n', ' ').strip()
                body = body.replace('\n', ' ')
                formatted.append(f"• [{title}]({href})\n  {body}\n")

            search_result = "搜索结果：\n\n" + "\n".join(formatted)
            if len(search_result) > 3000:
                search_result = search_result[:3000] + "...(结果已截断)"
            return search_result
    except Exception as e:
        return f"DuckDuckGo 搜索时出错: {str(e)}"

# ================= 工具定义 =================
tools = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "从互联网上搜索最新信息。当你不确定实时信息、新闻、流行趋势或自己知识范围外的事情时，可以使用此工具。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "要搜索的关键词，应该简洁明了。"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_image",
            "description": "根据文字描述生成一张图片，并保存到本地。",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "对图片内容的详细描述"},
                    "save_name": {"type": "string", "description": "保存的文件名，比如 'my_image.png'"}
                },
                "required": ["prompt", "save_name"]
            }
        }
    }
]

# ================= 智能体核心 =================
def run_agent_with_history(user_input: str, history_messages: list) -> tuple[str, list]:
    """
    参数：
        user_input: 用户本轮输入
        history_messages: 之前的对话历史(OpenAI格式的messages列表)
    返回：
        final_answer: 智能体最终回答文本
        updated_history: 更新后的完整对话历史
    """
    print(f"\n[智能体] 收到用户输入: {user_input}")
    messages = history_messages.copy()
    messages.append({"role": "user", "content": user_input})

    for round_num in range(5):
        print(f"[智能体] 第 {round_num+1} 轮推理...")
        try:
            response = local_llm.chat.completions.create(
                model="qwen2.5-7b-instruct-1m",  
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
        except Exception as e:
            error_msg = f"本地 LLM 调用失败: {e}"
            print(error_msg)
            return error_msg, messages

        msg = response.choices[0].message
        messages.append(msg)

        if not msg.tool_calls:
            full_content = msg.content or ""
            messages.append({"role": "assistant", "content": full_content})
            print(f"[智能体] 最终回答: {full_content[:100]}...")
            return full_content, messages

        # 执行工具调用
        for tool_call in msg.tool_calls:
            func_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            print(f"🔧 调用工具: {func_name}，参数: {args}")

            if func_name == "web_search":
                result = web_search(args["query"])
            elif func_name == "generate_image":
                result = call_zhipu_image_generation(args["prompt"], args["save_name"])
            else:
                result = "未知工具调用"

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })
            print(f" 工具返回: {result[:150]}...")

        time.sleep(0.5)

    final = "任务未完全完成，请简化需求或稍后再试。"
    messages.append({"role": "assistant", "content": final})
    return final, messages