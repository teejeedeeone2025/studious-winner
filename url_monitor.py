import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# Configuration - WARNING: Never commit this to version control!
URL_LIST_FILE = 'url_list.txt'
TARGET_URL = 'https://bbc.com'  # Replace with your target website

# Email settings - REMOVE BEFORE COMMITTING TO GIT
SENDER_EMAIL = "dahmadu071@gmail.com"
RECIPIENT_EMAILS = ["teejeedeeone@gmail.com"]
EMAIL_PASSWORD = "oase wivf hvqn lyhr"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def load_current_urls():
    """Load the currently known URLs from file"""
    if not os.path.exists(URL_LIST_FILE):
        return set()
    
    with open(URL_LIST_FILE, 'r') as f:
        return set(line.strip() for line in f if line.strip())

def fetch_new_urls():
    """Fetch URLs from the target website"""
    try:
        response = requests.get(TARGET_URL, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        # Adjust this selector based on your target website's structure
        links = [a['href'] for a in soup.find_all('a', href=True)]
        return set(links)
    except Exception as e:
        print(f"Error fetching URLs: {e}")
        return set()

def send_email_notification(new_urls):
    """Send email notification about new URLs"""
    subject = f"New URLs detected on {TARGET_URL}"
    body = f"The following new URLs were detected:\n\n" + "\n".join(new_urls)
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = ", ".join(RECIPIENT_EMAILS)
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.send_message(msg)
        print("Email notification sent successfully")
    except Exception as e:
        print(f"Error sending email: {e}")

def update_url_list(new_urls):
    """Create a new file with updated URLs"""
    current_urls = load_current_urls()
    updated_urls = current_urls.union(new_urls)
    
    with open('updated_url_list.txt', 'w') as f:
        for url in sorted(updated_urls):
            f.write(f"{url}\n")
    
    print("Updated URL list file created")

def main():
    print(f"Checking for new URLs at {datetime.now()}")
    
    current_urls = load_current_urls()
    fetched_urls = fetch_new_urls()
    
    if not fetched_urls:
        print("No URLs fetched from target website")
        return
    
    new_urls = fetched_urls - current_urls
    
    if new_urls:
        print(f"Found {len(new_urls)} new URLs:")
        for url in new_urls:
            print(f"- {url}")
        
        send_email_notification(new_urls)
        update_url_list(new_urls)
    else:
        print("No new URLs found")

if __name__ == "__main__":
    main()
