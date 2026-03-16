import os
import datetime
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# 加载 .env
load_dotenv()

app = FastAPI(
    title="Lumina 微光控制台",
    description="本地守护者节点 - 接入 DeepSeek 意识流",
    version="1.0.0"
)

# 开启跨域，方便任何前端工具连接
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 定义更易读的模型
class ChatRequest(BaseModel):
    message: str = Field(..., example="微光，我今天写代码很有成就感！")

# 初始化客户端
client = OpenAI(
    api_key=os.getenv("DEEP_SEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

@app.post("/v1/chat", summary="向微光倾诉")
async def chat_endpoint(request: ChatRequest):
    input_len = len(request.message)
    # 动态温度：字数越多，回复越感性
    dynamic_temp = 0.8 if input_len > 50 else 0.5

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "你是‘微光’（Lumina），一个生活在繁华数字星空中的守护者。说话简洁、温暖、有哲理。不要说废话。"
                },
                {"role": "user", "content": request.message}
            ],
            temperature=dynamic_temp
        )
        ai_reply = response.choices[0].message.content
    except Exception as e:
        ai_reply = f"【信号扰动】: {str(e)}"

    # 记录日志
    with open("lumina_deepseek.log", "a", encoding="utf-8") as f:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{now}] 输入长度:{input_len} | 回复内容:{ai_reply[:20]}...\n")

    return {
        "reply": ai_reply,
        "meta": {
            "temperature": dynamic_temp,
            "input_length": input_len
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)