import json
import re
import requests

from bs4 import BeautifulSoup

OUTPUT_FILE = "answer.json"

def get_csn():
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
        return f"資料獲取失敗，{res.status_code}"
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
        return f"資料獲取失敗，{res.status_code}"
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
            return "答案獲取失敗"

def main():
    csn = get_csn()
    ans = get_ans(csn)
    data = {
        "answer": {
            str(ans[0]): str(ans[1])
        }
    }
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        print("寫入成功")

if __name__ in "__main__":
    main()