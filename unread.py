# pylint: disable=no-member
# pylint: disable=missing-docstring
# pylint: disable=logging-fstring-interpolation
# pylint: disable=redefined-outer-name
# pylint: disable=self-assigning-variable
# pylint: disable=unspecified-encoding
# pylint: disable=broad-exception-caught
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import logging
import random
import threading
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

def random_sleep(min_time=1, max_time=3):
    """Sleep for a random amount of time between min_time and max_time seconds."""
    sleep_time = random.uniform(min_time, max_time)
    logging.info(f"Sleeping for {sleep_time:.2f} seconds.")
    sleep(sleep_time)

# Setup WebDriver
logging.info('Initializing Chrome driver')
driver = webdriver.Chrome()
driver.get('https://web.whatsapp.com/')

# Wait for QR code scan
input('Enter anything after scanning QR code')
logging.info('QR code scanned')

# Define the auto-reply message
auto_reply_message = "Hello! This is an automated reply from our WhatsApp Business account."

# ... (keep the existing imports and rate limiter code)

def is_unread_button_active():
    """Check if the 'Unread' button is active."""
    try:
        unread_button = driver.find_element(By.XPATH, "//button[@data-tab='4']")
        return 'x1qr81dd' in unread_button.get_attribute('class')
    except Exception as e:
        logging.error(f"Error checking 'Unread' button status: {e}")
        return False

def click_unread_button():
    """Click the 'Unread' button to filter unread chats if it's not already active."""
    if not is_unread_button_active():
        try:
            unread_button = driver.find_element(By.XPATH, "//button[@data-tab='4']")
            unread_button.click()
            logging.info("Clicked the 'Unread' button to filter chats.")
            random_sleep(1, 2)  # Wait for the filter to apply
        except Exception as e:
            logging.error(f"Error clicking the 'Unread' button: {e}")

def find_unread_chats():
    """Find unread chat elements, excluding those with the specified icon."""
    try:
        all_chats = driver.find_elements(By.XPATH, "//div[contains(@class, '_ak8l')]")
        unread_chats = []
        for chat in all_chats:
            unread_badge = chat.find_elements(By.XPATH, ".//span[contains(@class, 'x1rg5ohu') and @aria-label]")
            chat_icon = chat.find_elements(By.XPATH, ".//span[@data-icon='chats-filled']")
            if unread_badge and not chat_icon:
                unread_chats.append(chat)
        return unread_chats
    except Exception as e:
        logging.error(f"Error finding unread chats: {e}")
        return []

def reply_to_message(chat):
    """Click on chat, type the reply message, and send it."""
    try:
        chat.click()
        random_sleep(1, 2)  # Random sleep to simulate human behavior
        
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

def main():
    """Main function to monitor and auto-reply to messages."""
    try:
        click_unread_button()  # Initial click to filter unread messages
        while True:
            if not is_unread_button_active():
                click_unread_button()  # Reactivate the filter if it's not active
            
            unread_chats = find_unread_chats()
            if unread_chats:
                logging.info(f"Found {len(unread_chats)} unread chats.")
                for chat in unread_chats:
                    reply_to_message(chat)
                    random_sleep(1, 3)  # Random sleep between replying to different chats
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

if __name__ == "__main__":
    main()