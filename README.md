# 🗺️ 제주 핫플레이스 분석 프로젝트

> **제주도 네이버 블로그 데이터 기반 장소 분석 & 시각화 프로젝트**  
> 네이버 블로그 글에서 언급된 장소들을 분석하고
> Folium 지도 위에 **카테고리별 밀집도**를 표시

---

## 📚 프로젝트 개요

- 여행 정보가 넘쳐나는 제주도에서  
  **어디가 '진짜' 인기 있는 곳일지**를 분석해보기 위해 시작
- 네이버 블로그 게시글을 수집·분석하여
  - **지명, 상호명, 명사 빈도** 추출
  - 지명별 언급 빈도
  - 카테고리별 장소 분포
- 지도를 통해 **카테고리별 밀집 지역**을 직관적으로 표현

---

## ⚙️ 사용 기술

| 분야           | 스택 / 라이브러리                                |
|----------------|-------------------------------------------------|
| 데이터 수집     | Python, Selenium 등                              |
| 형태소 분석     | Python eunjeon (Mecab)                           |
| 텍스트 분석     | pandas, scikit-learn (TfidfVectorizer, CountVectorizer) |
| 공간 데이터 처리 | GeoPandas, shapely                              |
| 지도 시각화     | Folium, Choropleth                               |
| 카카오 API 사용 | Kakao Local API                                 |

---

## 🔎 주요 기능

### 🔹 텍스트 분석

- 명사 추출
- TF-IDF 키워드 추출
- 상호명 N-gram 추출
- 동시출현 키워드 분석

### 🔹 장소 좌표 수집

- **카카오 Local API**로 좌표 검색
- 장소별 카테고리 자동 분류 (카페, 음식점, 관광명소 등)

### 🔹 지도 시각화

- **Folium 지도**
    - 카테고리별 **마커 표시**
    - 카테고리별/제주도 권역별 **밀집도 Choropleth**
- **권역 단위 색상 표현**
    - 제주시
    - 제주시 동부
    - 제주시 서부
    - 서귀포시
    - 서귀포시 동부
    - 서귀포시 서부
- 마커 클릭 시 상세 정보 확인 가능

---


---

## ✅ 설치 & 실행 방법

1. **가상환경 설치**

    ```bash
    python -m venv venv
    source venv/bin/activate   # macOS / Linux
    cd venv\Scripts\activate      # Windows
    ```

2. **필요 라이브러리 설치**

    ```bash
    pip install -r requirements.txt
    ```

3. **카카오 API Key 설정**

    `.env`

    ```python
    KAKAO_REST_API_KEY = "your_api_key_here"
    ```

4. **웹스크래핑 실행**
    ```bash
    python Webscraping.py
    python Webscraping2.py
    ```
5. **데이터 정제**
    ```bash
    python csvAfter.py
    python csvAfter2.py
    ```
6. **데이터 병합**
    ```bash
    python merge.py
    ``` 
7. **텍스트 분석 실행**
    ```bash
    python NLP.py
    ```
8. **카카오 API 사용**
    ```bash
    python kakao.py
    ```
9. **지도 시각화 실행**
    ```bash
    python place.py
    ```
10. **`hotplace_map.html`** 열어서 결과 확인

---

## 💡 개선 아이디어

- SNS(인스타그램) 게시글, 댓글·사진 태그 추가 분석
- OCR을 이용한 광고성 게시글 추가 필터링
- 시계열 트렌드 분석
- 다른 지역 확대 적용 (부산, 서울 등)
- 웹 대시보드 구현

---

### 🌟 미리보기

# 관광명소 분포
> <img width="948" height="854" alt="image" src="https://github.com/user-attachments/assets/30c87d77-b966-4b8f-af76-7f4fd8b976c6" />

# 문화시설 분포
<img width="951" height="856" alt="image" src="https://github.com/user-attachments/assets/d6af22f5-cc3f-46bb-a0e7-7ddbf6d9990d" />

# 카페 분포
<img width="949" height="857" alt="image" src="https://github.com/user-attachments/assets/658f2261-97cd-4948-9868-eaa146061eaf" />

## 🔍 인사이트 요약

### 1. 카테고리별 공간 분포의 차이

- **카페**
  - 제주시 서부·북부(애월, 한림), 서귀포시 동부 해안가에 밀집
  - 동부, 남부는 상대적으로 적음 → 해안 관광 수요 영향

- **관광명소**
  - 섬 전역 분포
  - 동부와 서부 해안 지역이 특히 높음

- **문화시설**
  - 주로 제주시 도심권(노형, 이도동 등)에 집중
  - 서귀포 지역은 상대적으로 적음

---

### 2. 권역별 상권·관광 특성

- **제주시 동부**
  - 관광명소 비중이 높음 

- **제주시 서부**
  - 카페 밀집 지역
  - 해안 경관 관광과 연계된 상권 활성화

- **서귀포시**
  - 관광명소 고르게 분포
  - 문화시설은 제주시보다 적음 → 생활형 시설 차이

---

### 3. 활용 가능성

- SNS 언급량 기반 → 인지도·관심도 파악 가능
- 투자·창업 시 저밀도 지역은 블루오션 가능성
- 관광 마케팅, 정책 수립에 활용

