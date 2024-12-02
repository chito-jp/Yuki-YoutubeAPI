import json
import time
import requests

# JSONが正しいかどうかを確認する関数
def is_json(json_str):
    try:
        json.loads(json_str)
        return True
    except json.JSONDecodeError:
        return False

# JSONファイルからデータをロードする関数
def load_json_data(filename: str):
    with open(filename, "r") as file:
        data = json.load(file)
    return data

# apis.jsonからAPIリストを取得
apis = load_json_data("apis.json")

# APIリクエストを送信する関数
def api_request(url: str) -> str:
    start_time = time.time()
    for api in apis:
        if time.time() - start_time >= max_time - 1:
            break
        try:
            res = requests.get(api + url, timeout=max_api_wait_time)
            if res.status_code == 200 and is_json(res.text):
                print(f"成功API : {api}")
                return res.text  # レスポンスのテキストを返す
            else:
                print(f"取得エラー : {api}")
        except Exception as e:
            print(f"APIエラー : {api}, エラー内容: {str(e)}")
    raise TimeoutError("APIがタイムアウトしました")

# 動画情報を取得する関数
def get_video(video_id: str) -> dict:
    # APIリクエストを送信し、レスポンスを辞書に変換
    t = json.loads(api_request(f"/api/v1/videos/{video_id}"))
    
    # 関連動画を整理
    related_videos = [
        {
            "id": i["videoId"],
            "title": i["title"],
            "authorId": i["authorId"],
            "author": i["author"],
            "viewCount": i["viewCount"]
        }
        for i in t["recommendedVideos"]
    ]

    # 結果を辞書形式で返す
    return {
        "related_videos": related_videos,
        "stream_urls": list(reversed([i["url"] for i in t["formatStreams"]]))[:2],  # 逆順で2つのストリームURLを取得
        "description": t["descriptionHtml"].replace("\n", "<br>"),  # 説明文に改行を追加
        "title": t["title"],  # 動画タイトル
        "author_id": t["authorId"],  # 作者ID
        "author_name": t["author"],  # 作者名
        "author_thumbnail": t["authorThumbnails"][-1]["url"],  # 最後のサムネイルURL
        "view_count": t["viewCount"]  # 動画の再生回数
    }

# FastAPIのセットアップ
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI()

# テンプレートの設定
templates = Jinja2Templates(directory="templates")

# APIリクエストの最大待機時間
max_api_wait_time = 5
max_time = 15

# `/test`エンドポイントでAPIデータを返す
@app.get("/test", response_class=JSONResponse)
def get_apis():
    data = load_json_data("apis.json")
    return JSONResponse(content=data)

# ホームページを表示するエンドポイント
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("dummy.html", {"request": request})

# 動画情報を取得するエンドポイント
@app.get("/api/video/{video_id}", response_class=JSONResponse)
def api_get_video(video_id: str):
    # get_videoで動画情報を取得
    video_data = get_video(video_id)
    return JSONResponse(content=video_data)
