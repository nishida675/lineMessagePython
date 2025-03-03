import os
from dotenv import load_dotenv
from fastapi import FastAPI, BackgroundTasks, Header, HTTPException, Request
from pydantic import BaseModel, Field
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextSendMessage

import soccer
import notion
import scheduler

app = FastAPI()

# 環境変数を読み込む
load_dotenv()

# LINE Messaging APIの準備
line_bot_api = LineBotApi(os.environ["CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["CHANNEL_SECRET"])


@app.get("/")
def api_root():
    return {"message": "こんにちは"}


@app.post("/callback")
async def callback(
    request: Request,
    background_tasks: BackgroundTasks,
    x_line_signature=Header(None)
):
    body = await request.body()
    try:
        background_tasks.add_task(
            handler.handle, body.decode("utf-8"), x_line_signature
        )
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    return "ok"


# LINEのメッセージイベントを処理
@handler.add(MessageEvent)
def handle_message(event):
    user_message = event.message.text.strip()  # ユーザーのメッセージ

    # 条件によって返信を変える
    if user_message == "天気":
        reply_text = "今日の天気は晴れです"
    elif user_message == "時間":
        from datetime import datetime
        reply_text = f"現在の時刻は {datetime.now().strftime('%H:%M:%S')} です"
    # "試合日程" というメッセージが送られた場合
    elif user_message == "試合日程":
        schedule1 = soccer.get_team_matches("PL", "Brighton")
        schedule2 = soccer.get_team_matches("PD", "Real Sociedad")
        reply_text = f"{schedule1}\n{schedule2}"
    elif user_message == "試合結果":
        score1 = soccer.get_team_results("PL", "Brighton")
        score2 = soccer.get_team_results("PD", "Real Sociedad")
        reply_text = f"{score1}\n{score2}"
    elif user_message == "DBテスト":
        text = notion.fetch_notion_data()
        reply_text = f"{text}"
    elif user_message == "登録":
        user_id = event.source.user_id
        text = notion.insert_user_to_notion(user_id)
        reply_text = f"{text}"
    elif user_message == "ユーザーID":
        user_id = notion.get_user_from_notion()
        reply_text = f"ユーザーIDは {user_id} です"
    else:
        reply_text = "こんにちは"

    # LINEに返信を送る
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))



# FastAPIの起動（ローカル環境用）
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
