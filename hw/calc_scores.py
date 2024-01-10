import re
import json
import asyncio
import aiohttp


async def fetch(s, data_sample):
    async with s.post(
        url="https://node-api.datasphere.yandexcloud.net/classify",
        json={
            "Text": f"Текст статьи:\n{data_sample['article']}\n\nКраткое содержание:\n{data_sample['summary']}",
        },
        headers={
            "Authorization": "Api-Key AQVNyVqBi-XoJ1cAo7VIxq6ztgXm3owqowtso5Qb",
            "x-node-alias": "datasphere.user.yagpt-seminar-hw",
        },
        timeout=3) as resp:  # RESPONSE TIMEOUT
        if resp.status != 200:
            resp.raise_for_status()
        # result = await resp.text()
        score = json.loads(await resp.text())['Scores'][0]  # '{"Scores":[0.608398]}'
        print(f"> {data_sample['id']}: {score}")
        return data_sample['id'], score


async def fetch_all(session, data):
    tasks = []
    for data_sample in data:
        task = asyncio.create_task(fetch(session, data_sample))
        tasks.append(task)
        await asyncio.sleep(0.05)  # DoS TIMEOUT (to avoid error 503)
        # service temporarily unavailable generally means you are either sending too many requests,
        # or (more likely) you are being rate limited to prevent spamming/DOSing
    result = await asyncio.gather(*tasks)
    return result


async def main(data):
    async with aiohttp.ClientSession(timeout=200) as session:  # TOTAL TIMEOUT
        scores_list = await fetch_all(session, data)  # [(1, 0.608398), (2, 0.601563),, ...]
        return scores_list


if __name__ == '__main__':
    with open('test_set_articles_jsonlines.json', 'r') as f:
        test_articles = [json.loads(s) for s in f.readlines()]
    yagpt_result = []
    with open('test_set_summaries_jsonlines.json', 'r', encoding='utf-8') as f:
        json_data = re.sub(r"}\s*{", "},{", f.read())
        yagpt_result.extend(json.loads("[" + json_data + "]"))
    
    print(f"articles: {len(yagpt_result)}\n")
    data = [{'article': article['Text'], 'id': result['id'], 'summary': result['summary']}
            for article, result in zip(test_articles, yagpt_result)]
    scores = asyncio.run(main(data))
    print(sum([item[1] for item in scores]) / len(test_articles))
  
