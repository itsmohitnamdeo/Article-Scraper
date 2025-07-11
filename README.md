# Article Scraper 📰

This project scrapes opinion articles from [elpais.com/opinion](https://elpais.com/opinion/), extracts metadata and content, and runs cross-browser automation tests using [BrowserStack](https://www.browserstack.com/).

---

## 💻 Project Structure

### 1. **Local Scraper (`scraper_local.py`)**
- Uses Selenium with headless Chrome.
- Scrapes latest 5 opinion articles.
- Extracts:
  - Title
  - Translated title (Spanish → English)
  - Author
  - Published date and time
  - Content
  - Article image (if present)
- Saves:
  - CSV file with scraped data (`csv/articles.csv`)
  - Translated headers with repeated word frequency analysis (`translated_headers/translated_titles.csv`)
  - Images (`images/`)

### 2. **BrowserStack Scraper (`scraper_crossbrowser.py`)**
- Launches 5 parallel threads using different environments:
  - Chrome on Windows
  - Safari on macOS
  - Edge on Windows
  - Firefox on macOS
  - Chrome on Samsung Galaxy S23 (real mobile)
- Each thread:
  - Scrapes and saves articles into its own CSV (`csv/articles_threadX.csv`)
  - Saves translated titles and word counts (`translated_headers/translated_headers_threadX.csv`)
  - Downloads images to `images/threadX/`

---

### 📚 Used

- `selenium` – for web browser automation and scraping dynamic content.
- `beautifulsoup4` – for parsing and extracting HTML content.
- `deep-translator` – used to translate article headers from Spanish to English (`GoogleTranslator`).
- `requests` – for downloading article images.
- `threading` – for running parallel browser automation across multiple environments.

---

## ⚙️ Setup Instructions

- Clone the repository:

```bash
git clone https://github.com/itsmohitnamdeo/Article-Scraper.git
```

### 🧩 Requirements
```bash
pip install -r requirements.txt
```

**requirements.txt**
```
selenium
bs4
deep-translator
requests
```

### 🔐 BrowserStack Configuration
Set the following environment variables in your terminal or `.env`:
```bash
export BROWSERSTACK_USERNAME="your_USERNAME"
export BROWSERSTACK_ACCESS_KEY="your_ACCESS_KEY"
```

---

## 🚀 Usage

### Run Local Script
```bash
python scraper_local.py
```

### Run BrowserStack Script
```bash
python scraper_browserstack.py
```

---

## 🗂 Output

- **CSV Files** in `/csv`
- **Translated Headers** in `/translated_headers`
- **Images** in `/images/threadX/`

---

## 📊 Extra Features

- Translated headers printed in console.
- Repeated words in English titles (frequency count).
- Logs article metadata of content.
- Handles missing data gracefully.

---

## Contact

If you have any questions, suggestions, or need assistance related to the CSV-File-Utility-Tool, feel free to reach out to Me.

- MailId - namdeomohit198@gmail.com
- Mob No. - 9131552292
- Portfolio : https://itsmohitnamdeo.github.io
- Linkedin : https://www.linkedin.com/in/mohit-namdeo
