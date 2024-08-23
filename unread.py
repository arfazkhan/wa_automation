import logging
import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("whatsapp_auto_reply.log"),
        logging.StreamHandler()
    ]
)

# Set up Chrome options for Selenium
chrome_options = Options()
chrome_options.add_argument("--user-data-dir=./User_Data")  # Maintain session (avoid scanning QR repeatedly)

# Initialize WebDriver
service = Service('/path/to/chromedriver')  # Update this path to the location of your chromedriver
driver = webdriver.Chrome(service=service, options=chrome_options)

# Navigate to WhatsApp Web
driver.get('https://web.whatsapp.com')

# Wait for manual QR scan
logging.info("Scan QR code to log in to WhatsApp Web")
time.sleep(15)  # Adjust this as needed to allow for QR scan

# Constant auto-reply message
auto_reply_message = "Hello! This is an automated reply. For queries and ordering please contact or whatsapp us at +97142211158 ."

def random_sleep(min_time=1, max_time=3):
    """Sleep for a random amount of time between min_time and max_time seconds."""
    sleep_time = random.uniform(min_time, max_time)
    logging.info(f"Sleeping for {sleep_time:.2f} seconds.")
    time.sleep(sleep_time)

def click_unread_button():
    """Click the 'Unread' button to filter unread chats."""
    try:
        unread_button = driver.find_element(By.XPATH, "//button[@data-tab='4']")
        unread_button.click()
        logging.info("Clicked the 'Unread' button to filter chats.")
    except NoSuchElementException:
        logging.error("Unread button not found. Make sure the button's XPath is correct.")

def find_unread_chats():
    """Find unread chat elements."""
    try:
        # Locate unread contacts using the provided class name
        return driver.find_elements(By.XPATH, "//div[@class='_ak8l']")
    except NoSuchElementException:
        logging.error("No unread chats found or error in locating unread chats.")
        return []

def reply_to_message(chat):
    """Click on chat, type the reply message, and send it."""
    try:
        chat.click()
        random_sleep(1, 2)  # Random sleep to simulate human behavior
        message_box = driver.find_element(By.XPATH, "//div[@title='Type a message']")
        message_box.click()
        message_box.send_keys(auto_reply_message + Keys.ENTER)
        logging.info("Auto-reply sent to a chat.")
    except NoSuchElementException as e:
        logging.error(f"Error while replying to message: {e}")

def main():
    """Main function to monitor and auto-reply to messages."""
    try:
        while True:
            click_unread_button()  # Filter unread messages
            random_sleep(2, 4)  # Random sleep after clicking the 'Unread' button
            
            unread_chats = find_unread_chats()
            if unread_chats:
                logging.info(f"Found {len(unread_chats)} unread chats.")
                for chat in unread_chats:
                    reply_to_message(chat)
                    random_sleep(1, 3)  # Random sleep between replying to different chats
            else:
                logging.info("No new unread messages.")
            
            random_sleep(5, 10)  # Random sleep before checking for new messages again

    except KeyboardInterrupt:
        logging.info("Exiting...")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        driver.quit()
        logging.info("Closed WebDriver.")

if __name__ == "__main__":
    main()
