import os
import requests
from datetime import datetime, timedelta, timezone


# APIキー（環境変数から取得）
API_KEY = os.environ["FOOTBALL_DATA_API_KEY"]
BASE_URL = "https://api.football-data.org/v4"

# 日本時間（UTC+9）のタイムゾーン
JST = timezone(timedelta(hours=9))

def get_team_matches(competition_code, team_name):
    """ 指定したリーグとチームの今週の試合を取得 """
    today = datetime.now().date()
    next_week = today + timedelta(days=7)

    url = f"{BASE_URL}/competitions/{competition_code}/matches?dateFrom={today}&dateTo={next_week}"
    headers = {"X-Auth-Token": API_KEY}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return f"エラー: APIリクエストに失敗しました（{response.status_code}）"

    data = response.json()
    matches = data.get("matches", [])

    if not matches:
        return f"今週の{team_name}の試合はありません。"

    schedule = []
    for match in matches:
        home_team = match.get("homeTeam", {}).get("name", "不明")
        away_team = match.get("awayTeam", {}).get("name", "不明")
        date_str = match.get("utcDate", "")

        try:
            match_datetime_utc = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            match_datetime_jst = match_datetime_utc.astimezone(JST)
            match_date = match_datetime_jst.strftime("%m月%d日")  
            match_time = match_datetime_jst.strftime("%H時%M分") 
        except ValueError:
            continue

        if team_name in home_team or team_name in away_team:
            schedule.append(f"{match_date} {match_time}キック\n{home_team} \nvs \n{away_team}")

    return "\n".join(schedule) if schedule else f"今週の{team_name}の試合はありません。"


def get_team_results(competition_code, team_name):
    """ 指定したリーグとチームの先週の試合結果を取得 """
    today = datetime.now().date()
    last_week_start = today - timedelta(days=7)
    last_week_end = today - timedelta(days=1)

    url = f"{BASE_URL}/competitions/{competition_code}/matches?dateFrom={last_week_start}&dateTo={last_week_end}"
    headers = {"X-Auth-Token": API_KEY}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return f"エラー: APIリクエストに失敗しました（{response.status_code}）"

    data = response.json()
    matches = data.get("matches", [])

    if not matches:
        return f"先週の{team_name}の試合はありません。"

    results = []
    for match in matches:
        home_team = match.get("homeTeam", {}).get("name", "不明")
        away_team = match.get("awayTeam", {}).get("name", "不明")
        date_str = match.get("utcDate", "")
        score = match.get("score", {})
        full_time_score = score.get("fullTime", {})
        home_score = full_time_score.get("home", "?")
        away_score = full_time_score.get("away", "?")
        
        try:
            match_datetime_utc = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            match_datetime_jst = match_datetime_utc.astimezone(JST)
            match_date = match_datetime_jst.strftime("%m月%d日")
        except ValueError:
            continue

        if team_name in home_team or team_name in away_team:
            result_text = f"{match_date}\n{home_team} \n{home_score} - {away_score} \n{away_team}\n"
            results.append(result_text)

    return "\n".join(results) if results else f"先週の{team_name}の試合はありません。"




if __name__ == "__main__":
    print("--- ブライトンの試合 ---")
    print(get_team_matches("PL", "Brighton"))
    print("\n--- レアル・ソシエダの試合 ---")
    print(get_team_matches("PD", "Real Sociedad"))
