import os

os.system("sudo apt-get update")
os.system("sudo apt-get install -y wget curl unzip")
os.system("wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb")
os.system("sudo dpkg -i google-chrome-stable_current_amd64.deb")
os.system("sudo apt-get install -y -f")
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



import os

# === Configuration from Environment Variables ===
def get_required_env(name):
    """Get required environment variable or fail clearly"""
    value = os.environ.get(name)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}. "
                         "Please set it in GitHub Secrets.")
    return value

# Email settings
SENDER_EMAIL = get_required_env("SENDER_EMAIL")
RECIPIENT_EMAILS = get_required_env("RECIPIENT_EMAILS").split(",")
EMAIL_PASSWORD = get_required_env("EMAIL_PASSWORD")
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))

# GitHub settings
GH_TOKEN = get_required_env("GH_TOKEN")
REPO_NAME = get_required_env("REPO_NAME")

# SMS settings
SMS_PHONE_NUMBER = get_required_env("SMS_PHONE_NUMBER")

# === Rest of your existing code below ===
# (All your existing functions and logic remain exactly the same)





URL_LIST_FILE = "url_list.txt"

# Target website
TARGET_URL = "https://bbc.com"

# SMS settings

SMS_LOGIN_URL = "https://auth.mtnonline.com/login?state=hKFo2SBCSjVFajhyM211MDdIX1VXdUdLSzlFeUJTb1o3LUVYU6FupWxvZ2luo3RpZNkgc0NDdzczeFNwbl8zTjN5bkpuY3pQVXM5Sk9rVHZ0TFajY2lk2SB0V05sSkJmcXY4QjVjOXJWcml5OUVhdkVaTjN6cjQ2NQ&client=tWNlJBfqv8B5c9rVriy9EavEZN3zr465&protocol=oauth2&redirect_uri=https%3A%2F%2Fshop.mtn.ng%2Fmtnng%2Feshop%2Fcallback%2F&scope=openid%20profile%20email&response_mode=query&response_type=code&nonce=252325dd4d7509175e0bbd50e6d7ee0d&code_challenge=Ke-Ktp4CWM3tX2R_jGmLvDXkltKCZQrNFqGYrSueOAI&code_challenge_method=S256&theme="

def setup_chrome_driver():
    """Configure headless Chrome for SMS notifications"""
    chromedriver_autoinstaller.install()
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920x1080')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    return webdriver.Chrome(options=options)

def send_sms_notification(message):
    """Send SMS notification via MTN website"""
    driver = setup_chrome_driver()
    try:
        driver.get(SMS_LOGIN_URL)
        time.sleep(3)
        
        # Use keyboard navigation to reach the button
        body = driver.find_element(By.TAG_NAME, 'body')
        for _ in range(7):
            body.send_keys(Keys.TAB)
            time.sleep(0.3)
        
        # Click the button
        button = driver.switch_to.active_element
        button.click()
        time.sleep(0.3)
        
        # Navigate to phone input and enter number
        body.send_keys(Keys.TAB)
        time.sleep(0.5)
        input_field = driver.switch_to.active_element
        input_field.send_keys(SMS_PHONE_NUMBER)
        time.sleep(1)
        
        # Submit the form (this would normally trigger an SMS)
        input_field.send_keys(Keys.ENTER)
        time.sleep(2)
        
        print("SMS notification triggered")
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
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        base_url = requests.compat.urlparse(TARGET_URL).netloc
        links = set()
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('/'):
                href = f"https://{base_url}{href}"
            if href.startswith(('http://', 'https://')) and not any(x in href for x in ['#', 'tel:', 'mailto:']):
                links.add(href)
        return links
    except Exception as e:
        print(f"Error fetching URLs: {e}")
        return set()

def send_email_notification(new_urls):
    """Send email notification"""
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
    print("\n=== TESTING COMPLETE - DELETE THIS SCRIPT IMMEDIATELY ===")
