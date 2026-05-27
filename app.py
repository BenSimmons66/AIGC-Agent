import sys
import json
from flask import Flask, request, jsonify, render_template_string
from agent import run_agent_with_history

sys.stdout.reconfigure(line_buffering=True)

app = Flask(__name__)

# 存储对话历史
sessions = {}

# 聊天界面 HTML
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AIGC 智能体助手</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 30px auto; padding: 20px; }
        #chat { border: 1px solid #ccc; height: 400px; overflow-y: scroll; padding: 10px; background: #f9f9f9; margin-bottom: 10px; }
        .user { text-align: right; color: blue; margin: 8px; }
        .bot { text-align: left; color: green; margin: 8px; }
        #input-area { display: flex; gap: 10px; }
        #message { flex: 1; padding: 10px; font-size: 16px; }
        #send { padding: 10px 20px; font-size: 16px; cursor: pointer; }
    </style>
</head>
<body>
    <h2>🤖 AIGC 智能体助手</h2>
    <p>本地 LLM + 百度免费搜索 + 文生图 | 多轮对话记忆</p>
    <div id="chat"></div>
    <div id="input-area">
        <input type="text" id="message" placeholder="例如:搜索今天AI新闻" autocomplete="off">
        <button id="send">发送</button>
    </div>
    <script>
        const chatDiv = document.getElementById('chat');
        const msgInput = document.getElementById('message');
        const sendBtn = document.getElementById('send');

        function appendMessage(role, text) {
            const div = document.createElement('div');
            div.className = role;
            div.innerText = (role === 'user' ? ' ' : '智能体: ') + text;
            chatDiv.appendChild(div);
            chatDiv.scrollTop = chatDiv.scrollHeight;
        }

        async function send() {
            const text = msgInput.value.trim();
            if (!text) return;
            appendMessage('user', text);
            msgInput.value = '';
            const loading = document.createElement('div');
            loading.className = 'bot';
            loading.innerText = '智能体: 思考中...';
            chatDiv.appendChild(loading);
            try {
                const resp = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await resp.json();
                loading.remove();
                appendMessage('bot', data.reply);
            } catch (err) {
                loading.remove();
                appendMessage('bot', '错误: ' + err);
            }
        }

        sendBtn.onclick = send;
        msgInput.onkeypress = (e) => { if (e.key === 'Enter') send(); };
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    print("[Flask] 首页被访问")
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    print("\n" + "="*50)
    print("[Flask] 收到 /chat 请求")
    data = request.get_json()
    user_input = data.get('message', '')
    print(f"[Flask] 用户输入: {user_input}")

    session_id = request.remote_addr
    if session_id not in sessions:
        sessions[session_id] = []
        print(f"[Flask] 新会话: {session_id}")
    history = sessions[session_id]

    try:
        print("[Flask] 调用智能体...")
        reply, updated_history = run_agent_with_history(user_input, history)
        sessions[session_id] = updated_history
        print(f"[Flask] 智能体回复长度: {len(reply)} 字符")
        print("="*50)
        return jsonify({'reply': reply})
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[Flask] 错误: {e}")
        return jsonify({'reply': f'内部错误: {str(e)}'}), 500

if __name__ == '__main__':
    print("启动 Flask 服务...")
    print("访问 http://127.0.0.1:7860")
    app.run(host='127.0.0.1', port=7860, debug=True, use_reloader=False)