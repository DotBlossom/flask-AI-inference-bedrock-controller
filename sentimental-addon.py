
product_code = 1
results = ['a','b']


def request_preprocess(product_code, result):

    body = {
        "product_id": product_code,
        "shorts": {
            "youtube_url": result.get("shorts_url"),
            "youtube_thumbnail_url": result.get("thumbnail_url"),
            "shorts_id": result.get("shorts_id"),
        },
    }

    url = f"https://dotblossom.today/ai-api/metadata/product/shorts/{product_code}"

    headers = {"Content-type": "application/json"}

    try:
        response = requests.post(url, json=body, headers=headers, timeout=15)
        response.raise_for_status()
        print("데이터 전송 성공:", response.text)
    except requests.exceptions.RequestException as e:
        print("데이터 전송 실패:", e)



request_preprocess(product_code, results[0])
