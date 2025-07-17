import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from github import Github
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller
import time

# === CONFIGURATION (REMEMBER TO DELETE AFTER TESTING) ===
# Email settings
SENDER_EMAIL = "dahmadu071@gmail.com"
RECIPIENT_EMAILS = ["teejeedeeone@gmail.com"]
EMAIL_PASSWORD = "oase wivf hvqn lyhr"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# GitHub settings
GH_TOKEN = "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"
REPO_NAME = "teejeedeeone2025/studious-winner"
URL_LIST_FILE = "url_list.txt"

# SMS settings
PHONE_NUMBER = "09060558418"  # Your MTN Nigeria number
TARGET_URL = "https://bbc.com"

def setup_chrome():
    """Configure Chrome for SMS sending"""
    chromedriver_autoinstaller.install()
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=options)

def send_sms_notification(message):
    """Send SMS via MTN Nigeria website"""
    driver = setup_chrome()
    try:
        # Navigate to MTN login page
        url = "https://auth.mtnonline.com/login"
        driver.get(url)
        time.sleep(3)

        # Tab navigation to reach button
        body = driver.find_element(By.TAG_NAME, 'body')
        for _ in range(7):
            body.send_keys(Keys.TAB)
            time.sleep(0.3)

        # Click the focused button
        button = driver.switch_to.active_element
        button.click()
        time.sleep(0.3)

        # Navigate to phone input field and enter number
        body.send_keys(Keys.TAB)
        time.sleep(0.5)
        input_field = driver.switch_to.active_element
        input_field.send_keys(PHONE_NUMBER)
        time.sleep(1)

        # Submit form (this would normally send SMS)
        input_field.send_keys(Keys.ENTER)
        time.sleep(2)
        
        print("SMS notification attempted (simulated)")
        return True

    except Exception as e:
        print(f"SMS sending failed: {str(e)}")
        return False
    finally:
        driver.quit()

def load_current_urls():
    """Load URLs from GitHub repository"""
    g = Github(GH_TOKEN)
    repo = g.get_repo(REPO_NAME)
    try:
        file = repo.get_contents(URL_LIST_FILE)
        return set(file.decoded_content.decode().splitlines())
    except:
        repo.create_file(URL_LIST_FILE, "Initial URL list", "")
        return set()

def fetch_new_urls():
    """Scrape target website for URLs"""
    try:
        response = requests.get(TARGET_URL, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        base_url = requests.compat.urlparse(TARGET_URL).netloc
        links = set()
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('/'):
                href = f"https://{base_url}{href}"
            if href.startswith(('http://', 'https://')):
                links.add(href)
        return links
    except Exception as e:
        print(f"Error fetching URLs: {e}")
        return set()

def send_email_notification(new_urls):
    """Send formatted email alert"""
    subject = f"🚨 {len(new_urls)} New URLs detected on {TARGET_URL}"
    body = f"New URLs detected at {datetime.now()}:\n\n" + "\n".join(sorted(new_urls))
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = ", ".join(RECIPIENT_EMAILS)
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.send_message(msg)
        print("Email alert sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")

def update_github_urls(new_urls):
    """Update GitHub file with new URLs"""
    g = Github(GH_TOKEN)
    repo = g.get_repo(REPO_NAME)
    
    try:
        file = repo.get_contents(URL_LIST_FILE)
        current_content = file.decoded_content.decode()
        updated_content = current_content + "\n" + "\n".join(sorted(new_urls))
        repo.update_file(URL_LIST_FILE, f"Add {len(new_urls)} new URLs", updated_content, file.sha)
        print("GitHub URL list updated")
    except Exception as e:
        print(f"Failed to update GitHub: {e}")

def main():
    print(f"\n=== Checking {TARGET_URL} at {datetime.now()} ===")
    
    current_urls = load_current_urls()
    print(f"Currently tracking {len(current_urls)} URLs")
    
    fetched_urls = fetch_new_urls()
    if not fetched_urls:
        print("No URLs fetched from target website")
        return
    
    new_urls = fetched_urls - current_urls
    
    if new_urls:
        print(f"\nFound {len(new_urls)} NEW URLs:")
        for url in sorted(new_urls):
            print(f"• {url}")
        
        # Send both notifications
        send_email_notification(new_urls)
        send_sms_notification(f"New URLs detected on {TARGET_URL}: {len(new_urls)} updates")
        update_github_urls(new_urls)
    else:
        print("No new URLs detected")

if __name__ == "__main__":
    main()
    print("\n=== REMEMBER TO DELETE THIS SCRIPT AFTER TESTING ===")
