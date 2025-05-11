import time
import csv
import datetime
import pyperclip
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import sys

# ✅ Function to save data to CSV
def append_to_csv(data):
    with open("results.csv", "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(data)
    print(f"✅ {len(data)} results added to results.csv")

def get_google_links(keyword, num_links):
    from googlesearch import search
    results = []
    
    for link in search(keyword, num_results=num_links):  # ✅ Use `num_results` instead of `num`
        results.append([link, "Google", datetime.datetime.now().strftime("%Y-%m-%d"), keyword])
        print(f"🔗 {len(results)}: {link}")
    
    append_to_csv(results)


def parse_count(value):
    try:
        value = value.lower().replace(',', '')  # Remove commas
        if "k" in value:
            return int(float(value.replace('k', '')) * 1000)
        elif "m" in value:
            return int(float(value.replace('m', '')) * 1000000)
        else:
            return int(value)
    except:
        return 0

def parse_count(text):
    """Convert comment count text into an integer."""
    try:
        return int(text.replace(',', ''))
    except ValueError:
        return 0

def append_to_csv(data):
    """Append extracted data to a CSV file."""
    import csv
    with open("facebook_posts.csv", "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(data)

def get_facebook_links(keyword, NumberLinks):
    """Extract Facebook post links, caption, profile name, comment count, and full comments."""
    
    options = Options()
    options.add_argument(r'--user-data-dir=C:\Users\yasaa\AppData\Local\Google\Chrome\User Data')
    options.add_argument(r"--profile-directory=Profile 3")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    if "www.facebook.com" in keyword:
        search_url = keyword
    else:
        search_url = f"https://www.facebook.com/search/posts/?q={keyword.replace(' ', '%20')}"
    
    driver.get(search_url)
    time.sleep(5)

    temp_links = []
    scroll_pause_time = 3
    last_height = driver.execute_script("return document.body.scrollHeight")

    while len(temp_links) < NumberLinks:
        posts = driver.find_elements(By.XPATH, "//div[@aria-posinset]")

        for post in posts:
            try:
                # ✅ Get Profile Name
                profile_name = post.find_element(By.XPATH, ".//span[contains(@dir, 'auto')]").text.strip()
                
                # ✅ Click "Share" Button
                share_button = post.find_element(By.XPATH, ".//span[contains(text(), 'Share')]")
                ActionChains(driver).move_to_element(share_button).click().perform()
                time.sleep(2)

                # ✅ Click "Copy Link"
                copy_link = driver.find_element(By.XPATH, "//span[contains(text(), 'Copy link')]")
                copy_link.click()
                time.sleep(2)

                # ✅ Get Copied Link
                copied_link = pyperclip.paste()

                if copied_link.startswith("https://www.facebook.com"):
                    # ✅ Extract Comments Count
                    try:
                        comments_element = post.find_element(By.XPATH, ".//span[contains(text(), 'comment')]")
                        comments_text = comments_element.text.split()[0]
                        comments = parse_count(comments_text)
                    except:
                        comments = 0

                    # ✅ Click "Comments" Section and Scroll Down to Load More Comments
                    try:
                        comments_button = post.find_element(By.XPATH, ".//span[contains(text(), 'Comment')]")
                        comments_button.click()
                        time.sleep(2)

                        while True:
                            try:
                                more_comments_button = post.find_element(By.XPATH, ".//div[contains(text(), 'View more comments')]" )
                                driver.execute_script("arguments[0].scrollIntoView();", more_comments_button)
                                more_comments_button.click()
                                time.sleep(2)  # Allow time to load
                            except:
                                break  # No more comments to load
                    except:
                        pass

                    # ✅ Extract all visible comments
                    comment_texts = []
                    comment_elements = post.find_elements(By.XPATH, ".//div[@dir='auto']")
                    for comment in comment_elements:
                        text = comment.text.strip()
                        if text and text.lower() not in ["reply", "see more"]:
                            comment_texts.append(text)

                    all_comments = " || ".join(comment_texts)  # Separate comments with ||

                    # ✅ Extract Caption
                    try:
                        caption = post.find_element(By.XPATH, ".//div[@dir='auto']").text.strip()
                    except:
                        caption = ""

                    # ✅ Save Data
                    temp_links.append([
                        copied_link, "Facebook", datetime.datetime.now().strftime("%Y-%m-%d"), keyword, profile_name, caption, comments, all_comments
                    ])
                    print(f"🔗 {len(temp_links)}: {copied_link} | 👤 {profile_name} | 📝 {caption} | 💬 {comments} Comments | 📝 {len(comment_texts)} Extracted")

                if len(temp_links) >= NumberLinks:
                    break

            except Exception as e:
                print(f"⚠️ Error: {e}")
                continue

        # ✅ Scroll Down for More Posts
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    driver.quit()
    append_to_csv(temp_links)

    
# ✅ TikTok Search Function
def get_tiktok_links(keyword, num_links):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    search_url = f"https://www.tiktok.com/search?q={keyword.replace(' ', '%20')}"
    driver.get(search_url)
    time.sleep(5)

    results = []
    while len(results) < num_links:
        posts = driver.find_elements(By.XPATH, "//a[contains(@href, '/video/')]")

        for post in posts:
            link = post.get_attribute("href")
            if link and link not in results:
                results.append([link, "TikTok", datetime.datetime.now().strftime("%Y-%m-%d"), keyword])
                print(f"🔗 {len(results)}: {link}")

                if len(results) >= num_links:
                    break

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

    driver.quit()
    append_to_csv(results)

# ✅ Instagram Search Function
def get_instagram_links(keyword, num_links):
    options = Options()
    options.add_argument(r'--user-data-dir=C:\Users\yasaa\AppData\Local\Google\Chrome\User Data')
    options.add_argument(r"--profile-directory=Profile 3")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    search_url = f"https://www.instagram.com/explore/tags/{keyword.replace(' ', '')}/"
    driver.get(search_url)
    time.sleep(5)

    results = []
    while len(results) < num_links:
        posts = driver.find_elements(By.XPATH, "//a[contains(@href, '/p/')]")

        for post in posts:
            link = post.get_attribute("href")
            if link and link not in results:
                results.append([link, "Instagram", datetime.datetime.now().strftime("%Y-%m-%d"), keyword])
                print(f"🔗 {len(results)}: {link}")

                if len(results) >= num_links:
                    break

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

    driver.quit()
    append_to_csv(results)

# ✅ Main Execution
if __name__ == "__main__":
    try:
        # ✅ Ensure correct arguments are provided
        if len(sys.argv) != 4:
            print("❌ Usage: python project.py <keyword> <platform> <num_links>")
            sys.exit(1)

        keyword = sys.argv[1]
        platform = sys.argv[2].lower()
        num_links = int(sys.argv[3])

        # ✅ Run appropriate function based on platform
        if platform == "google":
            print(f"🔎 Extracting Google search results for: {keyword} ...")
            get_google_links(keyword, num_links)
        elif platform == "facebook":
            print(f"📘 Extracting Facebook search results for: {keyword} ...")
            get_facebook_links(keyword, num_links)
        elif platform == "tiktok":
            print(f"🎵 Extracting TikTok search results for: {keyword} ...")
            get_tiktok_links(keyword, num_links)
        elif platform == "instagram":
            print(f"📸 Extracting Instagram search results for: {keyword} ...")
            get_instagram_links(keyword, num_links)
        else:
            print("❌ Invalid platform selected!")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}")
