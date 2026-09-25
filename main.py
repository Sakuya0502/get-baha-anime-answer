import json
import re
import requests
import time
import datetime
import subprocess

from bs4 import BeautifulSoup

OUTPUT_FILE = "answer.json"

def get_csn():
    #FB的資料太難爬，只好借用巴哈上有人上傳的資料
    base_url = "https://api.gamer.com.tw/home/v2/creation_list.php"
    #感謝X洨妹(https://home.gamer.com.tw/profile/index.php?owner=blackxblue)於巴哈提供的資料
    main_url = "https://home.gamer.com.tw/profile/index_creation.php?owner=blackxblue&folder=370818"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36",
        "Referer": str(main_url),
    }
    params = {"owner": "blackxblue", "folder": 370818}
    res = requests.get(base_url, headers=headers, params=params)
    if res.status_code != 200:
        return None
    else:
        data = res.json()
        csn = data["data"]["list"][0]["csn"]
        return csn
    
def get_ans(csn_id):
    base_url = f"https://home.gamer.com.tw/artwork.php?sn={str(csn_id)}"
    headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36",
    }
    res = requests.get(base_url, headers=headers)
    res.encoding = "utf-8"
    if res.status_code != 200:
        return None
    else:
        soup = BeautifulSoup(res.text, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()
        article = soup.find("div", id="article_content")
        text = article.get_text(separator="\n", strip=True)
        options = dict(re.findall(r"^(\d+)[\.、]\s*(.+)$", text, flags=re.MULTILINE))
        ans = re.search(r"(?:A|Ans|答案)\s*[:：]\s*(\d+)", text, flags=re.IGNORECASE)
        if ans:
            ans_num = ans.group(1)
            ans_text = options.get(ans_num, "答案獲取失敗")
            return ans_num, ans_text
        else:
            return None

#推送到Github
def git_push(file_path="answer.json", commit_msg=None):
    try:
        status = subprocess.run(["git", "status", "--porcelain", file_path],
            capture_output=True,
            text=True,
            check=True
        )
        if not status.stdout.strip():
            print(f"[ {time.strftime('%Y-%m-%d %H:%M:%S')} ] 答案未變更，略過Push")
            return
        print(f"[ {time.strftime('%Y-%m-%d %H:%M:%S')} ] 檢測到新答案，準備開始推送")
        subprocess.run(["git", "add", file_path], check=True)
        subprocess.run(
            ["git", "commit", "-m", commit_msg or "Auto-update answer.json"],
            check=True,
        )
        subprocess.run(["git", "pull", "--rebase"], check=True)
        subprocess.run(["git", "push"], check=True)
        print(f"[ {time.strftime('%Y-%m-%d %H:%M:%S')} ] 推送成功")
    except subprocess.CalledProcessError as e:
        print(f"[ {time.strftime('%Y-%m-%d %H:%M:%S')} ] 推送失敗，失敗原因:{str(e)}")

#將資料寫入json
def write_json():
    csn = get_csn()
    if not csn:
        print("資料獲取失敗")
    ans = get_ans(csn)
    if not ans:
        print("資料獲取失敗")
    data = {
        "answer": {
            str(ans[0]): str(ans[1])
        }
    }
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    git_push(commit_msg=f"[ {time.strftime('%Y-%m-%d %H:%M:%S')} ] 答案已更新")

#時間校正(每5分鐘運行一次)   
def timer():
    now = datetime.datetime.now()
    second_past = (now.minute % 5) * 60 + now.second
    sleep_time = 300 - second_past
    sleep_time += 1
    target_time = now + datetime.timedelta(seconds=sleep_time)
    if sleep_time > 0:
        time_string = target_time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"距離下個準點 ({str(time_string)}) 還剩下 ({int(sleep_time)}) 秒，等待loop開始...")
        time.sleep(sleep_time)

def main_loop():
    TOTAL_RUN_TIME = 55 * 60
    startime = time.time()
    print("[ 立即開始爬蟲 ]")
    write_json()
    while (time.time() - startime) < TOTAL_RUN_TIME:
        timer()
        print(f"\n[ {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ] 獲取資料中...")
        write_json()
        time.sleep(2)
    

if __name__ in "__main__":
    main_loop()