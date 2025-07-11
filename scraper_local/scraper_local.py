from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from deep_translator import GoogleTranslator
from bs4 import BeautifulSoup
import time
import requests
import re
import csv
import os
from collections import Counter

# === Setup ===
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--lang=es')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--log-level=3')

# folders
os.makedirs("images", exist_ok=True)
os.makedirs("csv", exist_ok=True)
os.makedirs("translated_headers", exist_ok=True)

# Start driver
driver = webdriver.Chrome(options=chrome_options)
driver.get("https://elpais.com/opinion/")
time.sleep(4)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(2)

# === Collect article links ===
article_links, article_previews, article_authors = [], [], []
articles = driver.find_elements(By.CSS_SELECTOR, 'article')

for article in articles:
    try:
        link = article.find_element(By.CSS_SELECTOR, 'header h2 a').get_attribute('href')
        if link.startswith("https://elpais.com/opinion/") and link not in article_links:
            article_links.append(link)

            try:
                preview = article.find_element(By.CSS_SELECTOR, 'p.c_d').text.strip()
            except:
                preview = ""
            article_previews.append(preview)

            try:
                author_html = article.find_element(By.CSS_SELECTOR, 'div.c_a').get_attribute("innerHTML")
                soup_author = BeautifulSoup(author_html, 'html.parser')
                author = soup_author.get_text(separator="|").split("|")[0].strip()
            except:
                author = "Unknown Author"
            article_authors.append(author)

        if len(article_links) >= 5:
            break
    except Exception:
        continue

# === Scrape each article ===
titles, translated_titles, content_list, datetimes = [], [], [], []

print("\n==================== 📰 EL PAÍS OPINIÓN ARTICLES ====================\n")

for idx, link in enumerate(article_links):
    try:
        driver.get(link)
        time.sleep(2)

        title = driver.find_element(By.TAG_NAME, 'h1').text.strip()

        content_html = driver.find_element(By.TAG_NAME, 'article').get_attribute('innerHTML')
        soup = BeautifulSoup(content_html, 'html.parser')
        main_div = soup.find("div", class_="a_c clearfix", attrs={"data-dtm-region": "articulo_cuerpo"})
        if main_div:
            content = "\n\n".join(p.get_text(strip=True) for p in main_div.find_all("p") if p.text.strip())
        else:
            content = article_previews[idx] or "⚠️ Main article body not found."
        author = article_authors[idx]
        if author == "Unknown Author":
            try:
                author_tag = driver.find_element(By.CSS_SELECTOR, 'div.c_a').text.strip()
                author = author_tag.split("|")[0].strip()
            except:
                pass

        datetime_str = "Unknown Time"
        try:
            date_elements = driver.find_elements(By.CSS_SELECTOR, "div.a_md_f span a[data-date]")
            for de in date_elements:
                text = de.text.strip()
                if text:
                    datetime_str = text.replace("\xa0", " ")
                    break
        except:
            pass
        try:
            translated_title = GoogleTranslator(source='es', target='en').translate(title)
        except:
            translated_title = title
        titles.append(title)
        translated_titles.append(translated_title)
        content_list.append(content)
        datetimes.append(datetime_str)

        # Print to console
        print(f"📌 Article {idx + 1}")
        print("=" * 70)
        print(f"🔸 Title     : {title}")
        print(f"🔹 Translated: {translated_title}")
        print(f"👤 Author    : {author}")
        print(f"🕒 Published : {datetime_str}")
        print("-" * 70)
        print(f"{content[:1000]}...")
        print("=" * 70 + "\n")

        # Save image
        try:
            img_tag = driver.find_element(By.CSS_SELECTOR, "figure img")
            img_url = img_tag.get_attribute("src")
            if img_url:
                img_data = requests.get(img_url, timeout=10).content
                with open(f"images/article_{idx + 1}.jpg", "wb") as f:
                    f.write(img_data)
        except:
            print("❌ No image found for article", idx + 1)

    except Exception as e:
        print(f"⚠️ Error on article {idx + 1}: {e}")

# === Translated Headers ===
print("\n==================== 🌐 TRANSLATED HEADERS ====================\n")
for i, title in enumerate(translated_titles, 1):
    print(f"{i}. {title}")

# === Repeated Word Analysis ===
print("\n==================== 🔁 REPEATED WORDS IN ENGLISH TITLES ====================\n")
all_words = " ".join(translated_titles).lower()
word_list = re.findall(r'\b\w+\b', all_words)
word_counts = Counter(word_list)
repeated_words = {word: count for word, count in word_counts.items() if count > 1}

if repeated_words:
    for word, count in sorted(repeated_words.items(), key=lambda x: -x[1]):
        print(f"🔁 {word} : {count} times")
else:
    print("✅ No repeated words found.")

# === Save Articles to CSV ===
with open("csv/articles.csv", "w", newline='', encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Title", "Translated Title", "Author", "Published", "Content"])
    for i in range(len(titles)):
        writer.writerow([titles[i], translated_titles[i], article_authors[i], datetimes[i], content_list[i]])

# === Save Translated Titles + Repeated Word Counts ===
with open("translated_headers/translated_titles.csv", "w", newline='', encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Translated Titles"])
    for title in translated_titles:
        writer.writerow([title])
    writer.writerow([])
    writer.writerow(["Repeated Word", "Count"])
    for word, count in sorted(repeated_words.items(), key=lambda x: -x[1]):
        writer.writerow([word, count])

print("\n✅ All data saved:")
print("→ Articles: csv/articles.csv")
print("→ Images: images/")
print("→ Translated headers & repeated words: translated_headers/translated_titles.csv")

driver.quit()
