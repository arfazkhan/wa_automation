from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import csv
import random
import logging

# Configuration
CONTACTS_FILE = 'contacts.csv'
LOG_FILE = 'whatsapp_selenium.log'
PROMOTIONAL_MESSAGE = "This is a test message."
WHATSAPP_WEB_URL = 'https://web.whatsapp.com/'

# Set up logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def send_whatsapp_message(driver, phone_number, message):
    try:
        driver.get(f"https://web.whatsapp.com/send?phone={phone_number}&text={message}")
        time.sleep(10)  # Wait for WhatsApp Web to load

        # Send the message by pressing Enter
        driver.find_element_by_css_selector("div[data-tab='10']").send_keys(Keys.ENTER)
        logging.info(f"Message sent to {phone_number}")
        time.sleep(random.randint(5, 15))  # Random delay
    except Exception as e:
        logging.error(f"Failed to send message to {phone_number}: {str(e)}")

def load_contacts(file_path):
    try:
        with open(file_path, 'r') as csvfile:
            return [row['phone'] for row in csv.DictReader(csvfile)]
    except Exception as e:
        logging.error(f"Error loading contacts: {str(e)}")
        return []

def process_contacts():
    contacts = load_contacts(CONTACTS_FILE)
    if not contacts:
        logging.error("No contacts loaded. Exiting.")
        return

    driver = webdriver.Chrome()  # or `webdriver.Firefox()` if you're using Firefox
    driver.get(WHATSAPP_WEB_URL)

    input("Scan the QR code and press Enter to continue...")

    for phone_number in contacts[:20]:  # Process only the first 20 contacts
        send_whatsapp_message(driver, phone_number, PROMOTIONAL_MESSAGE)

    driver.quit()
    logging.info("Finished processing contacts.")

if __name__ == "__main__":
    logging.info("Starting WhatsApp automation test script with Selenium")
    process_contacts()
    logging.info("WhatsApp automation test script with Selenium completed")
