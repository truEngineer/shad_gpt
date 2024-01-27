import re
import json
import requests


with open('test_set_articles_jsonlines.json', 'r', encoding='utf-8') as fin:
    test_articles = [json.loads(s) for s in fin.readlines()]

yagpt_result = []
with open('test_set_summaries_jsonlines.json', 'r', encoding='utf-8') as file:
    json_data = re.sub(r"}\s*{", "},{", file.read())
    yagpt_result.extend(json.loads("[" + json_data + "]"))

print(f"articles: {len(yagpt_result)}\n")

json_id = 10
article = test_articles[json_id-1]['Text']
summary = yagpt_result[json_id-1]['summary']

full_input = f"Текст статьи:\n{article}\n\nКраткое содержание:\n{summary}"
resp = requests.post(
    url="https://node-api.datasphere.yandexcloud.net/classify",
    json={
        "Text": full_input,
    },
    headers={
        "Authorization": "Api-Key AQVNyVqBi-XoJ1cAo7VIxq6ztgXm3owqowtso5Qb",
        "x-node-alias": "datasphere.user.yagpt-seminar-hw",
    }
)

score = json.loads(resp.text)["Scores"][0]
print(f"{json_id}: {score}")
