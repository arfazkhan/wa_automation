import pywhatkit
import apscheduler
import ratelimit
import random
import time
import csv
import logging
import os
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from ratelimit import limits, sleep_and_retry, RateLimitException

# Configuration
CALLS_PER_HOUR = 90
PERIOD = 3600  # 1 hour in seconds
INVALID_CONTACTS_FILE = 'invalid_contacts.csv'
CONTACTS_FILE = 'contacts.csv'
LOG_FILE = 'whatsapp_automation.log'
PROMOTIONAL_MESSAGE = "Your promotional message here"
PDF_PATH = "path/to/your_document.pdf"
MAX_RETRIES = 3
RETRY_DELAY = 300  # 5 minutes
MAX_DAILY_MESSAGES = 700
COOL_DOWN_PERIOD = 3600  # 1 hour
PROCESSED_CONTACTS_DIR = 'processed_contacts'

# Set up logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

if not os.path.exists(PROCESSED_CONTACTS_DIR):
    os.makedirs(PROCESSED_CONTACTS_DIR)

@sleep_and_retry
@limits(calls=CALLS_PER_HOUR, period=PERIOD)
def send_whatsapp_message(phone_number, message, pdf_path):
    for attempt in range(MAX_RETRIES):
        try:
            simulate_typing_delay(message)
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
        except RateLimitException:
            logging.warning(f"Rate limit reached. Waiting before retrying {phone_number}")
            time.sleep(PERIOD / CALLS_PER_HOUR)
        except Exception as e:
            logging.error(f"Error sending message to {phone_number}: {str(e)}")
            if attempt < MAX_RETRIES - 1:
                logging.info(f"Retrying in {RETRY_DELAY} seconds... (Attempt {attempt + 1}/{MAX_RETRIES})")
                time.sleep(RETRY_DELAY)
            else:
                handle_send_error(phone_number, e)

def simulate_typing_delay(message):
    typing_time = len(message) / 5 + random.uniform(2, 5)
    time.sleep(typing_time)

def handle_send_error(phone_number, error):
    error_message = str(error)
    if "Invalid phone number" in error_message:
        logging.warning(f"Invalid phone number: {phone_number}")
        log_invalid_contact(phone_number)
    else:
        logging.error(f"Failed to send message to {phone_number} after {MAX_RETRIES} attempts: {error_message}")

def log_invalid_contact(phone_number):
    try:
        with open(INVALID_CONTACTS_FILE, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([phone_number])
        logging.info(f"Logged invalid contact: {phone_number}")
    except Exception as e:
        logging.error(f"Error logging invalid contact {phone_number}: {str(e)}")

def load_contacts(file_path):
    try:
        with open(file_path, 'r') as csvfile:
            return [row['phone'] for row in csv.DictReader(csvfile)]
    except Exception as e:
        logging.error(f"Error loading contacts: {str(e)}")
        return []

def save_contacts(contacts, file_path):
    try:
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['phone'])
            for phone_number in contacts:
                writer.writerow([phone_number])
        logging.info(f"Contacts saved to {file_path}")
    except Exception as e:
        logging.error(f"Error saving contacts: {str(e)}")

def load_processed_contacts():
    processed_contacts = set()
    for file in os.listdir(PROCESSED_CONTACTS_DIR):
        if file.endswith('.csv'):
            with open(os.path.join(PROCESSED_CONTACTS_DIR, file), 'r') as csvfile:
                processed_contacts.update([row['phone'] for row in csv.DictReader(csvfile)])
    return processed_contacts

def process_contacts():
    contacts = load_contacts(CONTACTS_FILE)
    if not contacts:
        logging.error("No contacts loaded. Exiting.")
        return

    processed_contacts = load_processed_contacts()
    contacts_to_send = [contact for contact in contacts if contact not in processed_contacts]

    if not contacts_to_send:
        logging.info("All contacts have been processed. Exiting.")
        return

    random.shuffle(contacts_to_send)
    today_file = os.path.join(PROCESSED_CONTACTS_DIR, f'processed_contacts_{datetime.now().strftime("%Y-%m-%d")}.csv')
    save_contacts(contacts_to_send, today_file)

    daily_message_count = 0
    batch_size = random.randint(10, 20)
    
    for i, phone_number in enumerate(contacts_to_send):
        if daily_message_count >= MAX_DAILY_MESSAGES:
            logging.info(f"Reached maximum daily messages ({MAX_DAILY_MESSAGES}). Stopping for the day.")
            break

        if i > 0 and i % batch_size == 0:
            logging.info(f"Completed a batch of {batch_size} messages. Taking a break.")
            time.sleep(random.randint(1200, 2400))  # 20-40 minute break between batches
            batch_size = random.randint(10, 20)

        try:
            simulate_random_delay()
            send_whatsapp_message(phone_number, PROMOTIONAL_MESSAGE, PDF_PATH)
            daily_message_count += 1
            simulate_longer_break()

            if daily_message_count % 90 == 0:
                logging.info(f"Sent {daily_message_count} messages. Initiating cool-down period.")
                time.sleep(COOL_DOWN_PERIOD)

        except Exception as e:
            logging.error(f"Unexpected error processing contact {phone_number}: {str(e)}")
            continue

    remaining_contacts = contacts_to_send[daily_message_count:]
    save_contacts(remaining_contacts, CONTACTS_FILE)
    logging.info(f"Finished processing contacts. Total messages sent: {daily_message_count}")

def simulate_random_delay():
    delay = random.randint(20, 40)  # Reduced delay to fit the message target
    logging.info(f"Waiting for {delay} seconds before sending the next message")
    time.sleep(delay)

def simulate_longer_break():
    if random.randint(1, 10) == 1:  # Adjusted to take breaks less frequently
        long_delay = random.randint(600, 1200)  # Reduced break time
        logging.info(f"Taking a longer break for {long_delay} seconds")
        time.sleep(long_delay)

def run_script():
    logging.info("Starting WhatsApp automation script")
    try:
        process_contacts()
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
    finally:
        logging.info("WhatsApp automation script completed")

if __name__ == "__main__":
    logging.info("Script started")
    try:
        scheduler = BlockingScheduler()
        # Run the script once a day at a random time between 9 AM and 11 AM
        run_time = datetime.now().replace(hour=9, minute=0, second=0) + timedelta(minutes=random.randint(0, 120))
        scheduler.add_job(run_script, 'cron', hour=run_time.hour, minute=run_time.minute)
        logging.info(f"Scheduler started. Next run at {run_time.strftime('%H:%M')}")
        scheduler.start()
    except KeyboardInterrupt:
        logging.info("Script stopped by user")
    except Exception as e:
        logging.error(f"An unexpected error occurred in main loop: {str(e)}")
    finally:
        logging.info("Script ended")
