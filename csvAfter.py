import pandas as pd
import re

def clean_text(text):
    if pd.isna(text):
        return ""
    
    # 전화번호 제거
    text = re.sub(r"\d{2,4}-\d{3,4}-\d{4}", "", text)

    # 영업시간 제거 (패턴 전체 포함)
    text = re.sub(r"\d{1,2}:\d{2}\s*~\s*\d{1,2}:\d{2}.*", "", text)

    # 거리 정보 제거
    text = re.sub(r"\d+m", "", text)

    # NAVER Corp. 제거
    text = re.sub(r"©.*$", "", text, flags=re.MULTILINE)

    # 예약, 위치, 재생, 접기/펴기 등
    text = re.sub(r"^(예약|위치|재생|접기/펴기)$", "", text, flags=re.MULTILINE)

    # 해시태그 블록 제거
    text = re.sub(r"(#[^\n]+\n*)+", "", text)

    # 숫자만 있는 줄 제거
    text = re.sub(r"^\d+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^[0-9\s:]+$", "", text, flags=re.MULTILINE)

    # 주소 제거
    text = re.sub(r"주소\s*:[^\n]+", "", text)

    # 연락처 제거
    text = re.sub(r"연락처\s*:[^\n]*", "", text)

    # 영업시간 제거
    text = re.sub(r"영업시간\s*:[^\n]+", "", text)

    # 메뉴 제거
    text = re.sub(r"메뉴\s*:[^\n]+", "", text)

    # 번호 + 점 제거
    text = re.sub(r"^\d+\.\s*", "", text, flags=re.MULTILINE)

    # 연속 공백 제거
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text

df = pd.read_csv("sns_posts.csv", encoding="utf-8-sig")

df["content_cleaned"] = df["content"].apply(clean_text)

df = df.drop(columns=["content"])

new_filename = "sns_posts_cleaned.csv"

df.to_csv(new_filename, index=False, encoding="utf-8-sig")
