import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from github import Github
import subprocess
import time

# === INSECURE HARDCODED CONFIG (DELETE AFTER TESTING!) ===
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

def load_current_urls():
    """Load URLs from GitHub repository"""
    g = Github(GH_TOKEN)
    repo = g.get_repo(REPO_NAME)
    try:
        file = repo.get_contents(URL_LIST_FILE)
        return set(file.decoded_content.decode().splitlines())
    except:
        # Create file if it doesn't exist
        repo.create_file(URL_LIST_FILE, "Initial URL list", "")
        return set()

def fetch_new_urls():
    """Scrape target website for URLs with improved filtering"""
    try:
        response = requests.get(TARGET_URL, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Improved URL collection with filtering
        base_url = requests.compat.urlparse(TARGET_URL).netloc
        links = set()
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Handle relative URLs
            if href.startswith('/'):
                href = f"https://{base_url}{href}"
            # Filter out non-HTTP links and junk
            if href.startswith(('http://', 'https://')) and not any(x in href for x in ['#', 'tel:', 'mailto:']):
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
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

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

def run_mtn_automation():
    """Run the MTN automation script as a subprocess"""
    try:
        # Assuming both scripts are in the same directory
        result = subprocess.run(['python', 'mtauto.py'], check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"MTN automation failed: {e}")
        return False
    except FileNotFoundError:
        print("MTN automation script not found")
        return False

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
        
        if send_email_notification(new_urls):
            # Only trigger MTN automation if email was sent successfully
            print("Triggering MTN automation...")
            time.sleep(2)  # Small delay before starting next script
            if run_mtn_automation():
                print("MTN automation completed successfully")
            else:
                print("MTN automation failed")
        
        update_github_urls(new_urls)
    else:
        print("No new URLs detected")

if __name__ == "__main__":
    main()
    print("\n=== TESTING COMPLETE - DELETE THIS SCRIPT IMMEDIATELY ===")
