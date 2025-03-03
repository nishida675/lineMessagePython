import requests
import os
from dotenv import load_dotenv

# .envファイルの読み込み
load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
print(NOTION_API_KEY)
print(DATABASE_ID)
NOTION_URL = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
NOTION_URL1= f"https://api.notion.com/v1/pages"

def fetch_notion_data():
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    # 修正: 空のJSONボディを明示的に送信
    response = requests.post(NOTION_URL, headers=headers, json={})
    print("レスポンス:", response.text)

    if response.status_code != 200:
        print(f"エラー: Notion APIリクエストに失敗しました（{response.status_code}）")
        print("レスポンス:", response.text)  # 追加: 詳細なエラーメッセージを表示
        return None

    return response.json()

def insert_user_to_notion(user_id):
    """ LINEのユーザーIDをNotion DBに追加 """
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "userId":{
               "rich_text": [{"text": {"content": user_id}}]
            }
        }
    }
    
    response = requests.post(NOTION_URL1,json=data, headers=headers)
    print("レスポンス:", response.text)
    return response

def get_user_from_notion():
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    response = requests.post(NOTION_URL, headers=headers, json={})  # Notion APIの仕様によりPOST
    data = response.json()
    
    if response.status_code != 200:
        print(f"エラー: Notion APIリクエストに失敗しました（{response.status_code}）")
        return None

    user_ids = []
    for page in data.get("results", []):
        rich_texts = page.get("properties", {}).get("userId", {}).get("rich_text", [])
        if rich_texts:
            user_id = rich_texts[0].get("text", {}).get("content", "")
            user_ids.append(user_id)
    
    return user_ids


# Notionデータの取得
notion_data = fetch_notion_data()
print(notion_data)
