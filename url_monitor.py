import os
import smtplib
import time
import requests
import subprocess
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from bs4 import BeautifulSoup
from github import Github
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller

# ===== HARDCODED CONFIGURATION (DELETE AFTER TESTING) =====
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

# Target website
TARGET_URL = "https://bbc.com"

# MTN Automation settings
MTN_PHONE = "09060558418"
MTN_LOGIN_URL = "https://auth.mtnonline.com/login"

# ===== CORE FUNCTIONS =====
def install_chrome_driver():
    """Install and configure Chrome with ChromeDriver"""
    print("\n" + "="*50)
    print("CHROME ENVIRONMENT SETUP".center(50))
    print("="*50)
    
    try:
        # Check if Chrome is installed
        try:
            chrome_version = subprocess.check_output(['google-chrome', '--version']).decode().strip()
            print(f"✓ Chrome installed: {chrome_version}")
        except:
            print("Installing Chrome browser...")
            subprocess.run(['wget', 'https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb'], check=True)
            subprocess.run(['sudo', 'apt', 'install', './google-chrome-stable_current_amd64.deb', '-y'], check=True)
            chrome_version = subprocess.check_output(['google-chrome', '--version']).decode().strip()
            print(f"✓ Chrome installed: {chrome_version}")

        # Install ChromeDriver
        print("\nInstalling ChromeDriver...")
        chromedriver_path = chromedriver_autoinstaller.install()
        driver_version = subprocess.check_output([chromedriver_path, '--version']).decode().strip()
        print(f"✓ ChromeDriver installed: {driver_version}")
        print(f"Path: {chromedriver_path}")
        
        return chromedriver_path
        
    except Exception as e:
        print(f"\n⚠️ Setup failed: {str(e)}")
        return None

def setup_chrome_browser():
    """Configure headless Chrome browser"""
    print("\nInitializing Chrome browser...")
    try:
        chromedriver_path = install_chrome_driver()
        if not chromedriver_path:
            return None

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920x1080')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        
        # Verify browser works
        driver.get("about:blank")
        print("✓ Chrome ready for automation")
        return driver
        
    except Exception as e:
        print(f"⚠️ Browser initialization failed: {str(e)}")
        return None

def load_current_urls():
    """Load URLs from GitHub repository"""
    print("\nLoading existing URLs...")
    try:
        g = Github(GH_TOKEN)
        repo = g.get_repo(REPO_NAME)
        file = repo.get_contents(URL_LIST_FILE)
        urls = set(file.decoded_content.decode().splitlines())
        print(f"Loaded {len(urls)} URLs from repository")
        return urls
    except Exception as e:
        print(f"Creating new URL list ({str(e)})")
        g = Github(GH_TOKEN)
        repo = g.get_repo(REPO_NAME)
        repo.create_file(URL_LIST_FILE, "Initial URL list", "")
        return set()

def scrape_website_urls():
    """Extract URLs from target website"""
    print(f"\nScraping {TARGET_URL}...")
    try:
        response = requests.get(TARGET_URL, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        base_domain = requests.compat.urlparse(TARGET_URL).netloc
        
        found_urls = set()
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Convert relative URLs to absolute
            if href.startswith('/'):
                href = f"https://{base_domain}{href}"
            
            # Filter valid URLs
            if href.startswith(('http://', 'https://')):
                found_urls.add(href)
        
        print(f"Found {len(found_urls)} URLs on page")
        return found_urls
        
    except Exception as e:
        print(f"⚠️ Scraping failed: {str(e)}")
        return set()

def run_mtn_automation(driver):
    """Perform MTN login automation"""
    print("\nRunning MTN automation...")
    try:
        driver.get(MTN_LOGIN_URL)
        time.sleep(3)
        
        # Navigate through login form
        body = driver.find_element(By.TAG_NAME, 'body')
        for _ in range(7):
            body.send_keys(Keys.TAB)
            time.sleep(0.3)
        
        # Click continue button
        driver.switch_to.active_element.click()
        time.sleep(0.5)
        
        # Enter phone number
        body.send_keys(Keys.TAB)
        phone_field = driver.switch_to.active_element
        phone_field.send_keys(MTN_PHONE)
        time.sleep(1)
        phone_field.send_keys(Keys.ENTER)
        time.sleep(3)
        
        # Capture screenshot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = f"mtn_result_{timestamp}.png"
        driver.save_screenshot(screenshot_path)
        print(f"✓ Screenshot saved: {screenshot_path}")
        
        return screenshot_path
        
    except Exception as e:
        print(f"⚠️ MTN automation failed: {str(e)}")
        return None

def send_alert_email(new_urls, attachment_path=None):
    """Send notification email with attachments"""
    print("\nPreparing email notification...")
    try:
        msg = MIMEMultipart()
        msg['Subject'] = f"🚨 {len(new_urls)} New URLs Detected"
        msg['From'] = SENDER_EMAIL
        msg['To'] = ", ".join(RECIPIENT_EMAILS)
        
        # Email body
        body_text = f"""
        New URLs detected at {datetime.now()}:
        
        {chr(10).join(sorted(new_urls))}
        
        ---
        Automated Monitoring System
        """
        msg.attach(MIMEText(body_text))
        
        # Attach screenshot if available
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, 'rb') as f:
                img = MIMEImage(f.read())
                img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_path))
                msg.attach(img)
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.send_message(msg)
        
        print("✓ Email notification sent")
        return True
        
    except Exception as e:
        print(f"⚠️ Failed to send email: {str(e)}")
        return False

def update_url_list(new_urls):
    """Update GitHub repository with new URLs"""
    print("\nUpdating URL list...")
    try:
        g = Github(GH_TOKEN)
        repo = g.get_repo(REPO_NAME)
        file = repo.get_contents(URL_LIST_FILE)
        
        # Merge and sort URLs
        existing_urls = set(file.decoded_content.decode().splitlines())
        updated_urls = sorted(existing_urls.union(new_urls))
        
        # Commit changes
        repo.update_file(
            path=URL_LIST_FILE,
            message=f"Add {len(new_urls)} new URLs",
            content="\n".join(updated_urls),
            sha=file.sha
        )
        
        print(f"✓ Repository updated with {len(new_urls)} new URLs")
        return True
        
    except Exception as e:
        print(f"⚠️ Failed to update repository: {str(e)}")
        return False

def main():
    print("\n" + "="*50)
    print(f"URL MONITORING STARTED: {datetime.now()}".center(50))
    print("="*50)
    
    # Initialize browser
    driver = setup_chrome_browser()
    if not driver:
        return
    
    try:
        # Load existing URLs
        known_urls = load_current_urls()
        
        # Scrape target website
        current_urls = scrape_website_urls()
        if not current_urls:
            return
        
        # Find new URLs
        new_urls = current_urls - known_urls
        if not new_urls:
            print("\nNo new URLs detected")
            return
        
        # Process new URLs
        print(f"\nDiscovered {len(new_urls)} new URLs:")
        for url in sorted(new_urls)[:5]:  # Show sample
            print(f"• {url}")
        if len(new_urls) > 5:
            print(f"• ...and {len(new_urls)-5} more")
        
        # Update repository
        update_url_list(new_urls)
        
        # Run MTN automation
        screenshot_path = run_mtn_automation(driver)
        
        # Send notification
        send_alert_email(new_urls, screenshot_path)
        
        # Clean up
        if screenshot_path and os.path.exists(screenshot_path):
            os.remove(screenshot_path)
            
    finally:
        driver.quit()
        print("\n" + "="*50)
        print("MONITORING COMPLETE".center(50))
        print("="*50)
        print("\n🚨 SECURITY REMINDER: DELETE THIS SCRIPT IMMEDIATELY")

if __name__ == "__main__":
    main()
