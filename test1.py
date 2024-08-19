import pywhatkit
import random
import time
import csv
import logging
import os

# Configuration
CONTACTS_FILE = 'contacts.csv'
LOG_FILE = 'whatsapp_automation_test.log'
PROMOTIONAL_MESSAGE = "This is a test message."
PDF_PATH = "path/to/your_document.pdf"
MAX_RETRIES = 2
RETRY_DELAY = 60  # 1 minute

# Set up logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def send_whatsapp_message(phone_number, message, pdf_path):
    for attempt in range(MAX_RETRIES):
        try:
            pywhatkit.sendwhats_image(
                phone_no=phone_number,
                img_path=pdf_path,
                caption=message,
                wait_time=15,
                tab_close=True,
                close_time=3
            )
            logging.info(f"Message and PDF sent to {phone_number}")
            return
        except Exception as e:
            logging.error(f"Error sending message to {phone_number}: {str(e)}")
            if attempt < MAX_RETRIES - 1:
                logging.info(f"Retrying in {RETRY_DELAY} seconds... (Attempt {attempt + 1}/{MAX_RETRIES})")
                time.sleep(RETRY_DELAY)
            else:
                logging.error(f"Failed to send message to {phone_number} after {MAX_RETRIES} attempts")

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

    if not os.path.exists(PDF_PATH):
        logging.error(f"PDF file not found at {PDF_PATH}. Exiting.")
        return

    random.shuffle(contacts)  # Randomize contact order
    for phone_number in contacts[:20]:  # Process only the first 20 contacts
        try:
            send_whatsapp_message(phone_number, PROMOTIONAL_MESSAGE, PDF_PATH)
            time.sleep(random.randint(10, 30))  # Short delay between messages
        except Exception as e:
            logging.error(f"Unexpected error processing contact {phone_number}: {str(e)}")
            continue  # Move to the next contact

    logging.info("Finished processing contacts.")

if __name__ == "__main__":
    logging.info("Starting WhatsApp automation test script")
    process_contacts()
    logging.info("WhatsApp automation test script completed")
