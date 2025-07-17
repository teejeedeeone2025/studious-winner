import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller
import time

def setup_chrome():
    # Auto-install ChromeDriver
    chromedriver_autoinstaller.install()
    
    # Configure Chrome options
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920x1080')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    return webdriver.Chrome(options=options)

def run_mtn_automation():
    driver = setup_chrome()
    
    try:
        # Navigate to MTN login page
        url = "https://auth.mtnonline.com/login?state=hKFo2SBCSjVFajhyM211MDdIX1VXdUdLSzlFeUJTb1o3LUVYU6FupWxvZ2luo3RpZNkgc0NDdzczeFNwbl8zTjN5bkpuY3pQVXM5Sk9rVHZ0TFajY2lk2SB0V05sSkJmcXY4QjVjOXJWcml5OUVhdkVaTjN6cjQ2NQ&client=tWNlJBfqv8B5c9rVriy9EavEZN3zr465&protocol=oauth2&redirect_uri=https%3A%2F%2Fshop.mtn.ng%2Fmtnng%2Feshop%2Fcallback%2F&scope=openid%20profile%20email&response_mode=query&response_type=code&nonce=252325dd4d7509175e0bbd50e6d7ee0d&code_challenge=Ke-Ktp4CWM3tX2R_jGmLvDXkltKCZQrNFqGYrSueOAI&code_challenge_method=S256&theme="
        driver.get(url)
        time.sleep(3)

        # Get body element for keyboard navigation
        body = driver.find_element(By.TAG_NAME, 'body')

        # Tab navigation to reach button
        for _ in range(7):
            body.send_keys(Keys.TAB)
            time.sleep(0.3)

        # Click the focused button
        button = driver.switch_to.active_element
        button.click()
        print("Button clicked successfully")
        time.sleep(0.3)

        # Navigate to phone input field
        body.send_keys(Keys.TAB)
        time.sleep(0.5)

        # Enter phone number
        input_field = driver.switch_to.active_element
        phone_number = "09060558418"  # Replace with your number
        input_field.send_keys(phone_number)
        time.sleep(1)

        # Submit form
        input_field.send_keys(Keys.ENTER)
        time.sleep(0.5)

        # Save screenshot
        screenshot_path = 'mtn_result.png'
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")

        # Verification pause
        time.sleep(5)
        
        return True

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return False

    finally:
        driver.quit()

if __name__ == "__main__":
    success = run_mtn_automation()
    if not success:
        exit(1)
