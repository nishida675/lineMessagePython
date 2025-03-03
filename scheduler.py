from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from linebot import LineBotApi
from linebot.models import TextSendMessage
import os
from dotenv import load_dotenv
import notion
import soccer
import pytz

# 環境変数の読み込み
load_dotenv()

# LINE Messaging API の設定
line_bot_api = LineBotApi(os.environ["CHANNEL_ACCESS_TOKEN"])

# スケジューラーの設定
scheduler = BackgroundScheduler()

# LINEのユーザーID（Notionなどから取得）
USER_IDS = notion.get_user_from_notion()

timezone = pytz.timezone('Asia/Tokyo') 

# 定期メッセージ送信の関数
def send_daily_message():
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = f"お知らせ: 現在の時刻は {now} です！"
    
    # USER_IDS が None または 空リスト の場合、処理をスキップ
    if not USER_IDS:
        print("送信先ユーザーがいません")
        return
    
    for user_id in USER_IDS:
        try:
            line_bot_api.push_message(user_id, TextSendMessage(text=message))
            print(f"送信成功: {user_id} -> {message}")
        except Exception as e:
            print(f"送信エラー: {user_id} -> {e}")

    
def send_soccer_message():
    schedule1 = soccer.get_team_matches("PL", "Brighton")
    schedule2 = soccer.get_team_matches("PD", "Real Sociedad")
    score1 = soccer.get_team_results("PL", "Brighton")
    score2 = soccer.get_team_results("PD", "Real Sociedad")
    message = f"試合予定\n{schedule1}\n{schedule2}\n\n試合結果\n{score1}\n{score2}"
    
    # 各ユーザーにメッセージを送信
    for user_id in USER_IDS:
        try:
            line_bot_api.push_message(user_id, TextSendMessage(text=message))
            print(f"送信成功: {user_id} -> {message}")
        except Exception as e:
            print(f"送信エラー: {user_id} -> {e}")

# 毎日 2:10 にメッセージを送信
scheduler.add_job(send_soccer_message, 'cron', day_of_week='mon', hour=8, minute=0, timezone=timezone)

# スケジューラーを開始
scheduler.start()
