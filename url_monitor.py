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
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller

# === INSECURE HARDCODED CONFIG (DELETE AFTER TESTING!) ===
# [Previous config values remain exactly the same...]

def install_chrome_driver():
    """Ensure Chrome and ChromeDriver are properly installed"""
    print("Setting up Chrome environment...")
    
    try:
        # 1. Install Chrome browser if missing
        try:
            subprocess.run(['google-chrome', '--version'], check=True, capture_output=True)
            print("✓ Chrome already installed")
        except:
            print("Installing Chrome browser...")
            subprocess.run(['wget', 'https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb'], check=True)
            subprocess.run(['sudo', 'apt', 'install', './google-chrome-stable_current_amd64.deb', '-y'], check=True)
            print("✓ Chrome installed")

        # 2. Auto-install ChromeDriver
        print("Installing ChromeDriver...")
        chromedriver_path = chromedriver_autoinstaller.install()
        print(f"✓ ChromeDriver installed at: {chromedriver_path}")
        
        # 3. Verify installation
        result = subprocess.run([chromedriver_path, '--version'], capture_output=True, text=True)
        print(f"ChromeDriver version: {result.stdout.strip()}")
        
        return chromedriver_path
        
    except Exception as e:
        print(f"Failed to setup Chrome: {e}")
        return None

def setup_chrome():
    """Configure headless Chrome with proper installation checks"""
    # First ensure Chrome environment is ready
    driver_path = install_chrome_driver()
    if not driver_path:
        raise RuntimeError("Chrome setup failed")
    
    # Configure options
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920x1080')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Initialize driver with explicit path
    service = Service(executable_path=driver_path)
    return webdriver.Chrome(service=service, options=options)

# [Rest of your functions remain exactly the same...]

def main():
    print(f"\n=== Starting monitoring at {datetime.now()} ===")
    
    # First-time Chrome setup feedback
    print("\n[1/3] Setting up browser environment...")
    try:
        # Test Chrome setup
        test_driver = setup_chrome()
        test_driver.quit()
        print("✓ Browser ready")
    except Exception as e:
        print(f"✗ Browser setup failed: {e}")
        return
    
    # URL Monitoring
    print("\n[2/3] Checking for URL changes...")
    current_urls = load_current_urls()
    fetched_urls = fetch_new_urls()
    
    if not fetched_urls:
        print("No URLs fetched")
        return
    
    new_urls = fetched_urls - current_urls
    
    if new_urls:
        print(f"Found {len(new_urls)} new URLs")
        update_github_urls(new_urls)
        
        # MTN Automation
        print("\n[3/3] Running MTN automation...")
        mtn_screenshot = run_mtn_automation()
        
        # Send combined email
        send_email_with_attachment(new_urls, mtn_screenshot)
        
        # Clean up
        if mtn_screenshot and os.path.exists(mtn_screenshot):
            os.remove(mtn_screenshot)
    else:
        print("No new URLs found")

if __name__ == "__main__":
    main()
    print("\n=== TESTING COMPLETE - DELETE THIS SCRIPT IMMEDIATELY ===")
