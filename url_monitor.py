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

# Websites to monitor with their corresponding tracking files
WEBSITES = {
    "BBC": {
        "url": "https://www.bbc.com",
        "tracking_file": "bbc_urls.txt"
    },
    "CNN": {
        "url": "https://www.cnn.com",
        "tracking_file": "cnn_urls.txt"
    },
    "Fox News": {
        "url": "https://www.foxnews.com",
        "tracking_file": "foxnews_urls.txt"
    },
    "Wall Street Journal": {
        "url": "https://www.wsj.com",
        "tracking_file": "wsj_urls.txt"
    },
    "New York Times": {
        "url": "https://www.nytimes.com",
        "tracking_file": "nytimes_urls.txt"
    },
    "Reuters": {
        "url": "https://www.reuters.com",
        "tracking_file": "reuters_urls.txt"
    }
}

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

def load_current_urls(tracking_file):
    """Load URLs from GitHub repository"""
    g = Github(GH_TOKEN)
    repo = g.get_repo(REPO_NAME)
    try:
        file = repo.get_contents(tracking_file)
        return set(file.decoded_content.decode().splitlines())
    except:
        # If file doesn't exist, create it
        repo.create_file(tracking_file, f"Initial URL list for {tracking_file}", "")
        return set()

def fetch_new_urls(target_url):
    """Scrape target website for URLs"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(target_url, timeout=10, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        base_url = requests.compat.urlparse(target_url).netloc
        links = set()
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('/'):
                href = f"https://{base_url}{href}"
            if href.startswith(('http://', 'https://')) and not any(x in href for x in ['#', 'tel:', 'mailto:']):
                # Normalize URL by removing query parameters and fragments
                href = requests.compat.urlparse(href)._replace(query='', fragment='').geturl()
                links.add(href)
        return links
    except Exception as e:
        print(f"Error fetching URLs from {target_url}: {e}")
        return set()

def send_email_notification(website_name, new_urls):
    """Send email notification"""
    subject = f"🚨 {len(new_urls)} New URLs detected on {website_name}"
    body = f"New URLs detected at {datetime.now()} on {website_name}:\n\n" + "\n".join(sorted(new_urls))
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = ", ".join(RECIPIENT_EMAILS)
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.send_message(msg)
        print(f"Email alert sent for {website_name}")
    except Exception as e:
        print(f"Failed to send email for {website_name}: {e}")

def update_github_urls(tracking_file, new_urls):
    """Update GitHub file with new URLs"""
    g = Github(GH_TOKEN)
    repo = g.get_repo(REPO_NAME)
    try:
        file = repo.get_contents(tracking_file)
        current_content = file.decoded_content.decode()
        updated_content = current_content + "\n" + "\n".join(sorted(new_urls))
        repo.update_file(tracking_file, f"Add {len(new_urls)} new URLs", updated_content, file.sha)
        print(f"GitHub URL list updated for {tracking_file}")
    except Exception as e:
        print(f"Failed to update GitHub for {tracking_file}: {e}")

def check_website(website_name, config):
    """Check a single website for new URLs"""
    print(f"\n=== Checking {website_name} at {datetime.now()} ===")
    
    current_urls = load_current_urls(config['tracking_file'])
    print(f"Currently tracking {len(current_urls)} URLs for {website_name}")
    
    fetched_urls = fetch_new_urls(config['url'])
    if not fetched_urls:
        print(f"No URLs fetched from {website_name}")
        return
    
    new_urls = fetched_urls - current_urls
    
    if new_urls:
        print(f"\nFound {len(new_urls)} NEW URLs for {website_name}:")
        for url in sorted(new_urls)[:5]:  # Print first 5 URLs to avoid clutter
            print(f"• {url}")
        if len(new_urls) > 5:
            print(f"• ...and {len(new_urls)-5} more")
        
        # Send notifications
        send_email_notification(website_name, new_urls)
        send_sms_notification(f"New URLs detected on {website_name}: {len(new_urls)} updates")
        update_github_urls(config['tracking_file'], new_urls)
    else:
        print(f"No new URLs detected for {website_name}")

def main():
    print(f"\n=== Starting website monitoring at {datetime.now()} ===")
    
    # Check each website in sequence
    for website_name, config in WEBSITES.items():
        try:
            check_website(website_name, config)
        except Exception as e:
            print(f"Error checking {website_name}: {str(e)}")
            continue
    
    print("\n=== Monitoring complete ===")

if __name__ == "__main__":
    # Install dependencies if not already present
    if not os.path.exists("/usr/bin/chromedriver"):
        os.system("sudo apt-get update")
        os.system("sudo apt-get install -y wget curl unzip")
        os.system("wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb")
        os.system("sudo dpkg -i google-chrome-stable_current_amd64.deb")
        os.system("sudo apt-get install -y -f")
    
    main()
