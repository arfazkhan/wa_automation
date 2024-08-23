# pylint: disable=no-member
# pylint: disable=missing-docstring
# pylint: disable=logging-fstring-interpolation
# pylint: disable=redefined-outer-name
# pylint: disable=self-assigning-variable
# pylint: disable=unspecified-encoding
# pylint: disable=broad-exception-caught
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import csv
import logging
import random
import threading
import os
import json
from time import sleep, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Rate limiter settings
RATE_LIMIT = 200  # 200 tokens per hour
TIME_WINDOW = 3600  # 1 hour
COOL_DOWN = 600  # 10 minutes

class RateLimiter:
    def __init__(self):
        self.tokens = RATE_LIMIT
        self.last_reset = time()
        self.lock = threading.Lock()
        logging.info(f'RateLimiter initialized with {self.tokens} tokens and last reset at {self.last_reset}')

    def get_token(self):
        with self.lock:
            current_time = time()
            elapsed_time = current_time - self.last_reset

            # Update tokens based on elapsed time
            self.tokens = min(RATE_LIMIT, self.tokens + (elapsed_time / TIME_WINDOW) * RATE_LIMIT)
            self.last_reset = current_time

            if self.tokens < 1:
                logging.info('Rate limit exceeded. Entering cooldown period.')
                sleep(COOL_DOWN)
                # After cooldown, reset tokens and update last_reset to the current time
                self.tokens = RATE_LIMIT
                self.last_reset = time()
                logging.info('Cooldown period ended. Tokens reset.')

            self.tokens -= 1
            logging.info(f'Token acquired. Remaining tokens: {self.tokens}')

# Setup logging
logging.basicConfig(filename='whatsapp_auto_reply.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize rate limiter
rate_limiter = RateLimiter()

# Define paths for cookies and contact files
cookies_file = 'whatsapp_cookies.json'
unread_contacts_file = 'unread_contacts.csv'

def save_cookies(driver):
    """Save cookies to a file."""
    cookies = driver.get_cookies()
    with open(cookies_file, 'w') as file:
        json.dump(cookies, file)
    logging.info('Cookies saved to file.')

def load_cookies(driver):
    """Load cookies from a file."""
    if os.path.exists(cookies_file):
        with open(cookies_file, 'r') as file:
            cookies = json.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
        logging.info('Cookies loaded from file.')
    else:
        logging.info('No cookies file found. Proceeding without loading cookies.')

def random_sleep(min_time=1, max_time=3):
    """Sleep for a random amount of time between min_time and max_time seconds."""
    sleep_time = random.uniform(min_time, max_time)
    logging.info(f"Sleeping for {sleep_time:.2f} seconds.")
    sleep(sleep_time)

# Setup WebDriver
logging.info('Initializing Chrome driver')
driver = webdriver.Chrome()
driver.get('https://web.whatsapp.com/')

# Load cookies to maintain session
load_cookies(driver)

# Refresh the page to apply cookies
driver.refresh()

# Wait for QR code scan if cookies are not available
if not os.path.exists(cookies_file):
    input('Enter anything after scanning QR code')
    save_cookies(driver)  # Save cookies after scanning QR code
    logging.info('QR code scanned and cookies saved.')

# Define the auto-reply message
auto_reply_message = "Hello! This is an automated reply from our WhatsApp Business account."

def find_unread_message_badge():
    """Find unread message badge elements."""
    try:
        # Find all badges indicating unread messages
        badges = driver.find_elements(By.XPATH, "//span[contains(@class, 'x1rg5ohu') and contains(@aria-label, 'unread message')]")
        if badges:
            logging.info(f"Found {len(badges)} unread message badges.")
        else:
            logging.info("No unread message badges found.")
        return badges
    except Exception as e:
        logging.error(f"Error finding unread message badges: {e}")
        return []

def get_contact_number_from_chat(chat):
    """Extract contact number from the specific chat element."""
    try:
        chat.click()
        random_sleep(1, 2)  # Random sleep to simulate human behavior

        # Extract the contact number
        contact_number_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//span[contains(@class, 'x1iyjqo2') and contains(@class, 'x6ikm8r') and contains(@class, 'x10wlt62')]")
            )
        )
        contact_number = contact_number_element.text
        logging.info(f"Contact number extracted: {contact_number}")

        return contact_number
    except Exception as e:
        logging.error(f"Error extracting contact number: {e}")
        return None

def reply_to_message():
    """Type the reply message and send it."""
    try:
        # Locate the message input field
        message_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@aria-label='Type a message']")
            )
        )
        message_box.click()
        message_box.send_keys(auto_reply_message)
        random_sleep(1, 2)  # Allow time for typing
        
        # Locate and click the send button
        send_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[@data-tab='11']")
            )
        )
        send_button.click()
        
        logging.info("Auto-reply sent.")
    except Exception as e:
        logging.error(f"Error while sending auto-reply: {e}")

def save_unread_contacts(contacts):
    """Save unread contact information to a CSV file."""
    with open(unread_contacts_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Contact Number'])
        for contact in contacts:
            writer.writerow([contact])
    logging.info(f"Unread contacts saved to '{unread_contacts_file}'.")

def main():
    """Main function to monitor and auto-reply to messages."""
    unread_contacts = []  # List to store unread contact info
    try:
        while True:
            unread_badges = find_unread_message_badge()
            if unread_badges:
                for badge in unread_badges:
                    badge.click()
                    random_sleep(1, 2)  # Random sleep to simulate human behavior

                    contact_number = get_contact_number_from_chat(driver)
                    if contact_number:
                        unread_contacts.append(contact_number)
                        reply_to_message()
                        random_sleep(1, 3)  # Random sleep between replying to different chats

                # Save unread contacts to CSV
                save_unread_contacts(unread_contacts)
            else:
                logging.info("No new unread messages.")
            
            random_sleep(5, 10)  # Random sleep before checking for new messages again

            # Simulate rate limiting
            rate_limiter.get_token()

    except KeyboardInterrupt:
        logging.info("Exiting...")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        driver.quit()
        logging.info("Closed WebDriver.")
        save_unread_contacts(unread_contacts)  # Save contacts on exit

if __name__ == "__main__":
    main()
