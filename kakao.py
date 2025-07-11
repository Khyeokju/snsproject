import requests
import pandas as pd
import time

# -----------------------------
# 1. CSV 읽기
# -----------------------------

filtered_df = pd.read_csv("filtered_places.csv", encoding="utf-8-sig")
places = filtered_df["place_name"].tolist()

# -----------------------------
# 2. 카카오 API 세팅
# -----------------------------

REST_API_KEY = "bcc4ef0110cd80c42019817f19f534dd"

url = "https://dapi.kakao.com/v2/local/search/keyword.json"

headers = {
    "Authorization": f"KakaoAK {REST_API_KEY}"
}

# -----------------------------
# 3. 결과 담을 리스트
# -----------------------------

results = []

for place in places:
    params = {
        "query": place,
        "size": 1
    }
    
    res = requests.get(url, headers=headers, params=params)
    data = res.json()
    
    documents = data.get("documents", [])
    
    if documents:
        doc = documents[0]
        name = doc["place_name"]
        addr = doc["road_address_name"]
        lat = doc["y"]
        lon = doc["x"]
        category = doc.get("category_group_name", "")  # ← 추가
        print(f"{name}: lat={lat}, lon={lon}, category={category}")
    else:
        name = place
        addr = ""
        lat = "NA"
        lon = "NA"
        category = ""
        print(f"❌ {place}: 좌표 없음")
    
    if not category:
        # 카테고리 수동 매핑
        if any(x in name for x in ["포구"]):
            category = "항구"
        elif any(x in name for x in ["마을", "공원"]):
            category = "문화시설"
        elif any(x in name for x in ["시장"]):
            category = "시장"
        elif any(x in name for x in ["폭포", "숲","봉"]):
            category = "관광명소"
        else:
            category = "기타"

    results.append({
        "place_name": name,
        "address": addr,
        "latitude": lat,
        "longitude": lon,
        "category": category  
    })
    
    time.sleep(0.5)



# -----------------------------
# 4. DataFrame으로 저장
# -----------------------------

final_df = pd.DataFrame(results)
final_df.to_csv("place_coords_updated.csv", index=False, encoding="utf-8-sig")

print("\n✅ place_coords_updated.csv 저장 완료!")
