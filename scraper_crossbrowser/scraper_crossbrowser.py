import os 
import csv
import re
import time
import threading
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from deep_translator import GoogleTranslator
from collections import Counter

BROWSERSTACK_USERNAME = "your_USERNAME"
BROWSERSTACK_ACCESS_KEY = "your_ACCESS_KEY"

CAPABILITIES = [
    {
        "os": "Windows",
        "osVersion": "10",
        "browserName": "Chrome",
        "browserVersion": "latest",
        "name": "Chrome-Windows",
    },
    {
        "os": "OS X",
        "osVersion": "Ventura",
        "browserName": "Safari",
        "browserVersion": "latest",
        "name": "Safari-Mac",
    },
    {
        "os": "Windows",
        "osVersion": "11",
        "browserName": "Edge",
        "browserVersion": "latest",
        "name": "Edge-Windows",
    },
    {
        "os": "OS X",
        "osVersion": "Monterey",
        "browserName": "Firefox",
        "browserVersion": "latest",
        "name": "Firefox-Mac",
    },
    {
        "deviceName": "Samsung Galaxy S23",
        "realMobile": "true",
        "osVersion": "13.0",
        "browserName": "Chrome",
        "name": "Galaxy-S23",
    }
]

def run_browserstack_test(cap, index):
    from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver

    bstack_options = {
        "userName": BROWSERSTACK_USERNAME,
        "accessKey": BROWSERSTACK_ACCESS_KEY,
        "sessionName": cap.get("name", f"Thread-{index}"),
    }

    if "deviceName" in cap:
        bstack_options.update({
            "deviceName": cap["deviceName"],
            "realMobile": cap["realMobile"],
            "osVersion": cap["osVersion"]
        })
    else:
        bstack_options.update({
            "os": cap["os"],
            "osVersion": cap["osVersion"]
        })

    caps = {
        "bstack:options": bstack_options,
        "browserName": cap.get("browserName"),
        "browserVersion": cap.get("browserVersion")
    }

    try:
        options = webdriver.ChromeOptions()
        for key in caps:
            options.set_capability(key, caps[key])

        driver = webdriver.Remote(
            command_executor="https://hub.browserstack.com/wd/hub",
            options=options
        )

        driver.get("https://elpais.com/opinion/")
        time.sleep(5)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        article_links, article_previews, article_authors = [], [], []

        articles = driver.find_elements(By.CSS_SELECTOR, 'article')
        for article in articles:
            try:
                header_link = article.find_element(By.CSS_SELECTOR, 'header h2 a')
                href = header_link.get_attribute('href')
                if href and href.startswith("https://elpais.com/opinion/") and href not in article_links:
                    article_links.append(href)

                    try:
                        preview = article.find_element(By.CSS_SELECTOR, 'p.c_d').text.strip()
                    except:
                        preview = ""
                    article_previews.append(preview)

                    try:
                        author_div = article.find_element(By.CSS_SELECTOR, 'div.c_a')
                        author_html = author_div.get_attribute("innerHTML")
                        soup_author = BeautifulSoup(author_html, 'html.parser')
                        author = soup_author.get_text(separator="|").split("|")[0].strip()
                    except:
                        author = "Unknown Author"
                    article_authors.append(author)

                if len(article_links) >= 5:
                    break
            except Exception:
                continue

        titles, translated_titles, content_list, datetimes, final_authors = [], [], [], [], []

        print(f"\n==================== 🧪 Thread {index} ====================\n")
        os.makedirs(f"images/thread{index}", exist_ok=True)
        os.makedirs("csv", exist_ok=True)
        os.makedirs("translated_headers", exist_ok=True)

        for idx, link in enumerate(article_links):
            try:
                driver.get(link)
                time.sleep(3)

                try:
                    title = driver.find_element(By.TAG_NAME, 'h1').text.strip()
                except:
                    title = f"Untitled Article {idx+1}"

                try:
                    content_html = driver.find_element(By.TAG_NAME, 'article').get_attribute('innerHTML')
                    soup = BeautifulSoup(content_html, 'html.parser')
                    main_div = soup.find("div", class_="a_c clearfix", attrs={"data-dtm-region": "articulo_cuerpo"})
                    if main_div:
                        content = "\n\n".join(p.get_text(strip=True) for p in main_div.find_all("p") if p.text.strip())
                    else:
                        content = article_previews[idx] or "⚠️ Main content not found."
                except:
                    content = article_previews[idx] or "⚠️ Content missing."

                author = article_authors[idx]
                datetime_str = "Unknown Time"
                try:
                    time_sections = driver.find_elements(By.CSS_SELECTOR, "div.a_md_f span a[data-date]")
                    for ts in time_sections:
                        dt_raw = ts.text.strip()
                        if dt_raw:
                            datetime_str = dt_raw.replace("\xa0", " ")
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
                final_authors.append(author)

                print(f"📌 Article {idx + 1}\n{'='*70}\n🔸 Title: {title}\n🔹 Translated: {translated_title}\n👤 Author: {author}\n🕒 Published: {datetime_str}\n{'-'*70}\n{content[:800]}...\n{'='*70}\n")

                try:
                    img_tag = driver.find_element(By.CSS_SELECTOR, "figure img")
                    img_url = img_tag.get_attribute("src")
                    if img_url:
                        img_data = requests.get(img_url, timeout=10).content
                        with open(f"images/thread{index}/article_{idx + 1}.jpg", "wb") as f:
                            f.write(img_data)
                except:
                    print("❌ Image not found or failed to download.\n")

            except Exception as e:
                print(f"⚠️ Skipping article {idx+1} due to error: {e}\n")
                continue

        with open(f"csv/articles_thread{index}.csv", "w", newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Title", "Translated Title", "Author", "Published", "Content"])
            for i in range(len(titles)):
                writer.writerow([titles[i], translated_titles[i], final_authors[i], datetimes[i], content_list[i]])

        print("\n==================== 🌐 TRANSLATED HEADERS ====================\n")
        for i, title in enumerate(translated_titles, 1):
            print(f"{i}. {title}")

        print("\n==================== 🔁 REPEATED WORDS IN ENGLISH TITLES ====================\n")
        all_words = " ".join(translated_titles).lower()
        words = re.findall(r'\b\w+\b', all_words)
        counts = Counter(words)
        repeated = {word: count for word, count in counts.items() if count > 1}

        if repeated:
            for word, count in sorted(repeated.items(), key=lambda x: -x[1]):
                print(f"🔁 {word} : {count} times")
        else:
            print("✅ No repeated words found.")

        with open(f"translated_headers/translated_headers_thread{index}.csv", "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Translated Title"])
            for t in translated_titles:
                writer.writerow([t])
            writer.writerow([])
            writer.writerow(["Repeated Word", "Count"])
            for word, count in sorted(repeated.items(), key=lambda x: -x[1]):
                writer.writerow([word, count])

        driver.execute_script('browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed","reason": "Scraped and saved articles successfully"}}')
        print(f"✅ Thread {index} completed. Data saved to CSV and images/ folder.")

    except Exception as e:
        try:
            driver.execute_script('browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed","reason": "Script crashed or failed"}}')
        except:
            pass
        print(f"[Thread {index}] ❌ Unexpected error: {e}")

    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    threads = []
    for idx, cap in enumerate(CAPABILITIES):
        t = threading.Thread(target=run_browserstack_test, args=(cap, idx+1))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print("\n🎉 All BrowserStack tests completed.")
