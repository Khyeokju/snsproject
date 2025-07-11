from eunjeon import Mecab
import pandas as pd
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from itertools import combinations

# Mecab 객체 생성
mecab = Mecab()

# CSV 불러오기
df = pd.read_csv("sns_posts_cleaned.csv", encoding="utf-8-sig")

# ------------------------------------------
# STOPWORDS
# ------------------------------------------
stopwords = set([
    "제주도","제주특별자치도","서귀포","서귀포시","맛집", "제주", "고기", "추천", "메뉴", "식사",
    "제주시", "주문", "방문", "음식", "식감", "느낌",
    "국수", "국물", "소개", "정도", "이야기", "시간", "사진",
    "위치", "정보", "정리", "경험", "서비스", "친절", "가게",
    "손님", "인테리어", "분위기", "분들", "가족", "가격",
    "하나", "자리", "입안", "풍미", "반찬", "조합", "기본",
    "번호", "구성", "입맛", "리스트", "가능", "전화", "테이블",
    "만족", "소스", "조화", "김치", "장소", "비주얼", "한입",
    "생각", "재료", "매력", "덕분", "이곳", "색달", "여행",
    "자연", "풍경", "바다", "모습", "체험", "사람", "포토",
    "주변", "근처", "구경", "시작", "안내", "이용", "촬영","명소",
    "풍경", "여행지", "여행객", "방문기", "관광", "관광객", "방문후기",
    "드라이브", "산책길", "바닷가", "명소들", "다녀옴", "소감", "후기",
    "여정", "사진들", "영상", "스팟들", "인생샷", "뷰", "한적", "여유",
    "숙소", "숙박", "주차공간", "무료주차", "체험", "예약", "운영시간",
    "블로그", "포스팅", "작성", "게시글", "리뷰", "공유", "기록"
])


# ------------------------------------------
# 전체 명사 추출
# ------------------------------------------
all_nouns = []
for text in df["content_cleaned"]:
    all_nouns.extend(mecab.nouns(str(text)))

counter = Counter(all_nouns)

filtered_nouns = [
    (noun, count)
    for noun, count in counter.most_common(500)
    if noun not in stopwords and len(noun) > 1
]

# ------------------------------------------
# (1) 지명 추출
# ------------------------------------------
jeju_places = [
    "월정리", "협재", "성산일출봉", "한림", "애월", "이중섭거리",
    "서귀포", "오설록", "곽지", "동문시장", "표선", "비자림",
    "우도", "한라산", "중문", "섭지코지", "산방산", "용두암",
    "수국길", "올레길", "소천지", "색달", "보목", "모슬포",
    "김녕", "세화", "조천", "하도리", "협재해변", "곽지해수욕장",
    "구좌", "남원", "표선면", "법환", "신산리", "대정", "안덕", "화순",
    "송악산", "가파도", "마라도", "금능", "금능해수욕장",
    "함덕", "함덕해수욕장", "도두", "애월읍", "하귀",
    "용담", "외도", "노형", "이도", "건입동", "삼도",
    "연동", "효돈", "서홍동", "대천동", "대림동",
    "정방폭포", "천지연폭포"
]

place_keywords = jeju_places + [
    "월정리해변"
]


geo_counter = Counter()
for noun, count in filtered_nouns:
    if noun in jeju_places:
        geo_counter[noun] = count

print("▶ 제주 지명 언급 빈도:")
for word, cnt in geo_counter.most_common():
    print(f"{word}: {cnt}")

# ------------------------------------------
# (2) 상호명 N-gram 추출
# ------------------------------------------
texts = df["content_cleaned"].fillna("").tolist()

vectorizer = CountVectorizer(
    tokenizer=mecab.nouns,
    token_pattern=None,
    ngram_range=(2, 2),
    min_df=2
)

X = vectorizer.fit_transform(texts)
ngram_counts = zip(vectorizer.get_feature_names_out(), X.sum(axis=0).tolist()[0])
sorted_ngrams = sorted(ngram_counts, key=lambda x: x[1], reverse=True)

biz_keywords = ["식당", "카페", "펜션", "리조트", "호텔", "게스트하우스"]

biz_candidates = []
for phrase, count in sorted_ngrams:
    if any(keyword in phrase for keyword in biz_keywords):
        biz_candidates.append((phrase, count))

print("\n▶ N-gram 상호명 후보:")
for phrase, count in biz_candidates[:50]:
    print(f"{phrase}: {count}")

# ------------------------------------------
# (3) TF-IDF 상위 단어
# ------------------------------------------
vectorizer = TfidfVectorizer(
    tokenizer=mecab.nouns,
    token_pattern=None,
    min_df=2,
    max_df=0.8
)
X = vectorizer.fit_transform(texts)

scores = zip(vectorizer.get_feature_names_out(), X.sum(axis=0).tolist()[0])
sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)

tfidf_candidates = [
    (word, score)
    for word, score in sorted_scores
    if word not in stopwords and len(word) > 1
]

print("\n▶ TF-IDF 상위 단어 Top 50:")
for word, score in tfidf_candidates[:50]:
    print(f"{word}: {score:.3f}")

# ------------------------------------------
# (4) 동시 출현 분석
# ------------------------------------------
co_occurrence = Counter()

for text in df["content_cleaned"]:
    nouns = list(set(mecab.nouns(str(text))))
    for pair in combinations(nouns, 2):
        co_occurrence[tuple(sorted(pair))] += 1

# 예시 → 소천지와 같이 언급되는 단어
target = "소천지"
print(f"\n▶ '{target}'와 같이 언급된 단어:")
for pair, count in co_occurrence.most_common():
    if target in pair:
        print(pair, count)

# ------------------------------------------
# (5) 장소별 Top 키워드
# ------------------------------------------
target_place = "소천지"
texts_with_place = df[df["content_cleaned"].str.contains(target_place, na=False)]["content_cleaned"]

nouns = []
for text in texts_with_place:
    nouns.extend(mecab.nouns(str(text)))

place_counter = Counter(nouns)

print(f"\n▶ {target_place} 관련 Top 20 단어:")
for word, count in place_counter.most_common(20):
    print(f"{word}: {count}")

# ------------------------------------------
# (6) 정규표현식 + 키워드 매칭으로 장소명 추출
# ------------------------------------------

import re

# 후미에 붙는 장소명 패턴
suffixes = (
    r"(카페|식당|펜션|리조트|관광|공원|"
    r"해수욕장|해변|시장|전망대|폭포|휴양림|숲길|"
    r"박물관|미술관|체험장|마을|항구|숲|포구)"
)

# 미리 수집해둔 고유 장소 단어 사전 (확장 가능)
place_keywords = [
    # 기존
    "월정리", "협재", "성산일출봉", "한림", "애월", 
    "곽지", "표선", "비자림", "우도", "한라산", 
    "중문", "섭지코지", "산방산", "용두암", 
    "동문시장", "모슬포", "김녕", "세화", "조천", 
    "하도리", "올레길", "소천지", "보목", "색달",
    "협재해수욕장", "곽지해수욕장", "월정리해변",
    "노형", "이도", "건입동", "삼도", "연동", "효돈", "서홍동", 
    "대천동", "대림동", "하귀", "애월읍", "화북동",
    "송악산", "가파도", "마라도", "금능", "금능해수욕장", 
    "함덕", "함덕해수욕장", "도두", "외도", "용담", 
    "정방폭포", "천지연폭포", "한담해안산책로", "사계", 
    "법환", "신산리", "화순", "대정", "안덕", "표선면", "지귀도",
    "모슬포항", "화순항", "성산항", "제주항",
    "도깨비도로", "사려니숲길", "제주돌문화공원", "용머리해안", 
    "수월봉", "송당리", "수목원테마파크", "제주러브랜드", 
    "카멜리아힐", "휴애리", "오름", "오라동", 
    "방선문", "정물오름"
]

detected_places = set()

for text in df["content_cleaned"].dropna():
    text = str(text)
    
    # ① 정규표현식으로 뒷단어 추출
    regex_matches = re.findall(r"([가-힣a-zA-Z0-9]+)" + suffixes, text)
    for m in regex_matches:
        place_name = "".join(m)
        detected_places.add(place_name)
    
    # ② 고유 장소 키워드 매칭
    for keyword in place_keywords:
        if keyword in text:
            detected_places.add(keyword)

print("\n▶ 정규표현식+사전매칭으로 추출된 장소명:")
for place in sorted(detected_places):
    print(place)

# ------------------------------------------
# (7) 후처리 필터링
# ------------------------------------------

# 제외할 패턴 키워드들 (단독어만 제외)
generic_keywords = set([
    "명소", "숨은명소", "사진명소", "포토명소", 
    "일몰명소", "자연명소", "오름공원", "어린이공원",
    "특급호텔", "로컬식당", "지질공원",
    "제주도가볼만한식당", "제주도로컬식당",
    "제주도숨은명소", "제주숨은명소",
    "맛집", "여행지", "풍경", "관광지", "스팟",
    "코스", "뷰맛집", "포인트", "데이트코스",
    "사진스팟", "감성스팟", "인생샷", "출사지",
    "휴게소", "시장", "마켓", "쇼핑몰",
    "공영주차장", "주차장", "교차로", "로터리",
    "삼거리", "사거리", "교회", "사찰", 
    "성당", "암자", "묘지", "무덤", "탑동", "거리", "로드", "길목",
    "웨딩홀", "펜션", "관광"
    "호텔", "리조트", "펜션", "게스트하우스",
    "마트", "편의점", "농협",
    "행사장", "페스티벌", "법환"
])

filtered_places = []
for place in sorted(detected_places):
    # (1) 너무 긴 단어 제외
    if len(place) > 20:
        continue
    # (2) 완전 일치할 때만 제외
    if place in generic_keywords:
        continue
    # (3) 한 글자인 것은 제외
    if len(place) == 1:
        continue
    filtered_places.append(place)

print("\n▶ 필터링 후 최종 장소명:")
for place in filtered_places:
    print(place)

filtered_df = pd.DataFrame(filtered_places, columns=["place_name"])
filtered_df.to_csv("filtered_places.csv", index=False, encoding="utf-8-sig")

print("\n필터링된 장소명이 filtered_places.csv로 저장완료")


# ------------------------------------------
# (8) 워드클라우드 시각화
# ------------------------------------------

from wordcloud import WordCloud
import matplotlib.pyplot as plt

word_freq = {noun: count for noun, count in filtered_nouns}

# 워드클라우드 생성
wc = WordCloud(
    font_path="C:\\Windows\\Fonts\\malgun.ttf", 
    width=1200,
    height=600,
    background_color="white"
)

wc.generate_from_frequencies(word_freq)

# 워드클라우드 시각화
plt.figure(figsize=(15, 8))
plt.imshow(wc, interpolation="bilinear")
plt.axis("off")
plt.title("Jeju SNS WordCloud", fontsize=20)
plt.show()

# 파일로 저장
wc.to_file("wordcloud_jeju.png")
print("\n워드클라우드 이미지 wordcloud_jeju.png로 저장완료")

# ------------------------------------------
# (9) 모든 분석 결과를 CSV로 저장 
# ------------------------------------------

import pandas as pd

# geo_places
geo_places_str = ", ".join(f"{place}:{count}" for place, count in geo_counter.most_common())

# ngram_places
ngram_places_str = ", ".join(f"{phrase}:{count}" for phrase, count in biz_candidates[:50])

# tfidf_top50
tfidf_str = ", ".join(f"{word}:{score:.3f}" for word, score in tfidf_candidates[:50])

# cooccurrence_pairs (소천지 기준)
cooccurrence_pairs = []
for pair, count in co_occurrence.most_common():
    if target in pair:
        cooccurrence_pairs.append(f"{pair}:{count}")
cooccurrence_str = ", ".join(cooccurrence_pairs)

# place_keywords
place_keywords_str = ", ".join(f"{word}:{count}" for word, count in place_counter.most_common(20))

# filtered_places
filtered_places_str = ", ".join(filtered_places)

# DataFrame 행 단위 생성
data = [
    ["geo_places", geo_places_str],
    ["ngram_places", ngram_places_str],
    ["tfidf_top50", tfidf_str],
    ["cooccurrence_pairs", cooccurrence_str],
    ["place_keywords", place_keywords_str],
    ["filtered_places", filtered_places_str]
   
]

result_df = pd.DataFrame(data, columns=["category", "result"])

# CSV 저장
result_df.to_csv("jeju_analysis_summary.csv", index=False, encoding="utf-8-sig")

print("\n모든 분석 결과 jeju_analysis_summary.csv 로 저장완료")
