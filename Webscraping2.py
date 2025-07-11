from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time, re, json

# 광고성 키워드 리스트
ad_keywords = [
    "협찬", "AD", "지원받음", "홍보",
    "포스팅 비용", "체험단", "제공받음",
    "내돈내산", "광고"
]

# 수집할 검색어 리스트
search_keywords = ["제주 맛집", "제주 카페"]

# Selenium 옵션 설정
options = webdriver.ChromeOptions()
options.add_argument("start-maximized")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

all_data = []

for keyword in search_keywords:
    print(f"\n========= 검색어: {keyword} =========")

    driver.get("https://www.naver.com")

    # 검색창 입력
    search_box = driver.find_element(By.ID, "query")
    search_box.clear()
    search_box.send_keys(keyword)
    search_box.send_keys(Keys.RETURN)

    # 블로그 탭 클릭
    wait.until(EC.presence_of_element_located((By.LINK_TEXT, "블로그")))
    driver.find_element(By.LINK_TEXT, "블로그").click()


    time.sleep(2)

    # 스크롤 다운
    SCROLL_PAUSE_SEC = 2
    last_height = driver.execute_script("return document.body.scrollHeight")

    for i in range(50):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_SEC)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    titles_elems = driver.find_elements(By.CSS_SELECTOR, "a.title_link")
    summary_elems = driver.find_elements(By.CSS_SELECTOR, "a.dsc_link")

    title_texts = []
    summary_texts = []
    blog_urls = []

    for elem in titles_elems:
        title_texts.append(elem.text)
        url = elem.get_attribute("href")
        if url and "blog.naver.com" in url:
            blog_urls.append(url)

    for elem in summary_elems:
        summary_texts.append(elem.text)

    while len(summary_texts) < len(title_texts):
        summary_texts.append("")

    for i, url in enumerate(blog_urls):
        if len(all_data) >= 200:
            break

        title = title_texts[i]
        summary = summary_texts[i]

        driver.get(url)
        time.sleep(2)

        try:
            driver.switch_to.frame("mainFrame")

            # 스마트에디터
            try:
                content_elem = driver.find_element(By.CSS_SELECTOR, "div.se-main-container")
                content = content_elem.text
            except:
                content = ""

            # 구형 에디터
            if not content:
                try:
                    content_elem = driver.find_element(By.CSS_SELECTOR, "div#postViewArea")
                    content = content_elem.text
                except:
                    content = ""

            is_ad = any(word in content for word in ad_keywords) \
                    or any(word in title for word in ad_keywords) \
                    or any(word in summary for word in ad_keywords)

            is_too_short = len(content) < 300

            if not is_ad and not is_too_short:
                hashtags = re.findall(r"#\S+", content)

                all_data.append({
                    "search_keyword": keyword,
                    "title": title,
                    "summary": summary,
                    "content": content,
                    "hashtags": json.dumps(hashtags, ensure_ascii=False),
                    "url": url
                })
                print(f"[수집] {title} - {url}")
            else:
                print(f"[제외] 광고 or 짧음 - {title}")

            driver.switch_to.default_content()

        except Exception as e:
            print(f"Error in {url}: {e}")
            driver.switch_to.default_content()
            continue

driver.quit()

# 저장
df = pd.DataFrame(all_data)
df.to_csv("sns_posts2.csv", index=False, encoding="utf-8-sig")
print("\n크롤링 완료. sns_posts.csv2 저장완료")
