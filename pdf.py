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
import os
import random
import re
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
logging.basicConfig(filename='whatsapp_automation.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize rate limiter
rate_limiter = RateLimiter()

def validate_and_format_number(number):
    logging.info(f'Validating number: {number}')
    clean_number = re.sub(r'\D', '', number)

    # Remove country codes and prefixes
    for prefix in ['971', '00971', '+971', '91', '0091', '+91']:
        clean_number = clean_number.removeprefix(prefix)

    # Add country code if missing
    if clean_number.startswith(('5', '4', '52', '53', '54', '55', '56', '58')):
        clean_number = '971' + clean_number
    elif len(clean_number) == 10:
        clean_number = '91' + clean_number

    # Validate and format number
    if len(clean_number) == 12:
        if re.match(r'^971[45][\d]{8}$', clean_number):
            logging.info('Number is a valid UAE number')
            return clean_number
        elif re.match(r'^919[\d]{9}$', clean_number):
            logging.info('Number is a valid Indian number')
            return clean_number
    logging.warning(f'Number format not recognized after cleaning: {number}')
    return None

# Setup WebDriver
logging.info('Initializing Chrome driver')
driver = webdriver.Chrome()
driver.get('https://web.whatsapp.com/')

# Wait for QR code scan
input('Enter anything after scanning QR code')
logging.info('QR code scanned')

# Path to the PDF file
pdf_path = os.path.abspath('menu.pdf')

common_message = """Greetings from City Burger Restaurant..!%0AWe are delighted to share our latest menu with you.%0A%0AFor orders, visit: https://wa.me/97142211158 or click on any pages in the menu."""

# Define greetings list
greetings = ["Dear Customer", "Hi there", "Hello", "Hi", "Halla Wallah"]

# Start total time tracking
total_start_time = time()

# Counters for success and failure
success_count = 0
failure_count = 0

# CSV file to store failed contacts
failed_contacts_file = 'failed_contacts.csv'

# CSV file to store sent contacts
sent_contacts_file = 'sent_contacts.csv'

# Load sent contacts from CSV into a set
sent_contacts = set()
if os.path.exists(sent_contacts_file):
    with open(sent_contacts_file, 'r') as sc_file:
        reader = csv.reader(sc_file)
        for row in reader:
            if row:
                sent_contacts.add(row[0])

# Open the failed contacts CSV file in write mode and sent contacts in append mode
with open(failed_contacts_file, 'w', newline='') as failed_file, \
     open(sent_contacts_file, 'a', newline='') as sc_file:

    failed_writer = csv.writer(failed_file)
    sent_writer = csv.writer(sc_file)

    # Write the header for failed contacts if not already written
    if os.stat(failed_contacts_file).st_size == 0:
        failed_writer.writerow(['Name', 'Number'])

    # Read the input CSV file
    with open('contacts.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            try:
                # Check for empty row
                if not row or row == ['']:
                    logging.info('Skipping empty row')
                    continue

                if len(row) != 2:
                    raise ValueError('Incorrect row format')

                name, number = row

                if not name:
                    raise ValueError('Contact without name')

                if not number:
                    raise ValueError('Contact without number')

                logging.info(f'Reading contact: {name}, {number}')
                # Validate and format the number
                formatted_number = validate_and_format_number(number)
                if formatted_number is None:
                    logging.error(f'Failed to format number for contact {name}: {number}')
                    failure_count += 1  # Increment failure counter
                    # Write failed contact to CSV
                    failed_writer.writerow([name, number])
                    continue

                # Check if the contact has already received the message
                if formatted_number in sent_contacts:
                    logging.info(f'Skipping duplicate contact: {name} ({formatted_number})')
                    continue

                # Add the contact to the set of sent contacts and CSV
                sent_contacts.add(formatted_number)
                sent_writer.writerow([formatted_number])

                # Start time tracking for the individual contact
                start_time = time()

                # Randomly select a greeting
                greeting = random.choice(greetings)

                # Personalize message
                personalized_message = f"*_Please Ignore the following message. This is just a test run for the promotion of City Burger._*%0A%0A*KINDLY IGNORE!!!!*%0A%0A{greeting},%0A{common_message}"

                # Open chat for contact
                try:
                    driver.get(f'https://web.whatsapp.com/send?phone={formatted_number}&text={personalized_message}')
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//div[@title="Attach"]'))
                    )
                    logging.info(f'Opened chat for contact: {name}')
                except Exception as e:
                    logging.error(f'Failed to open chat for contact {name} ({number}): {e}')
                    failure_count += 1  # Increment failure counter
                    # Write failed contact to CSV
                    failed_writer.writerow([name, number])
                    continue

                # Click the attachment box
                try:
                    attachment_box = driver.find_element(By.XPATH, '//div[@title="Attach"]')
                    attachment_box.click()
                    logging.info('Attachment box clicked')

                    # Click the "Document" option
                    document_option = WebDriverWait(driver, 15).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, '//span[@class="xdod15v xzwifym x6ikm8r x10wlt62 xlyipyv xuxw1ft" and text()="Document"]'))
                    )
                    document_option.click()
                    logging.info('Document option clicked')

                    # Wait for the file picker to open and interact with it
                    sleep(2)  # Ensure file picker has time to open

                    # Use JavaScript to set the file directly (if the file input is available)
                    file_input = driver.find_element(By.XPATH, '//input[@type="file"]')
                    file_input.send_keys(pdf_path)
                    logging.info('PDF file selected through file input')

                    # Wait for the file to upload
                    sleep(8)

                    # Click the send button
                    send_button = WebDriverWait(driver, 8).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, '//span[@data-icon="send"]'))
                    )
                    send_button.click()
                    logging.info(f'Message sent to contact: {name}')

                    # Wait for either the single tick or double tick to confirm message was sent
                    try:
                        WebDriverWait(driver, 30).until(
                            EC.presence_of_element_located(
                                (By.XPATH, '//span[@data-icon="msg-check"] | //span[@data-icon="msg-dblcheck"]'))
                        )
                        logging.info(f'Message sent and confirmed for contact: {name}')
                        success_count += 1  # Increment success counter
                    except Exception as e:
                        logging.error(f'Failed to confirm message sent for contact {name}: {e}')
                        failure_count += 1  # Increment failure counter
                        # Write failed contact to CSV
                        failed_writer.writerow([name, number])
                        continue

                except Exception as e:
                    logging.error(f'Error while sending message to {name}: {e}')
                    failure_count += 1  # Increment failure counter
                    # Write failed contact to CSV
                    failed_writer.writerow([name, number])
                    continue

                # End time tracking for the individual contact
                end_time = time()
                time_taken = end_time - start_time
                logging.info(f'Time taken for contact {name}: {time_taken:.2f} seconds')

                # Simulate rate limiting
                rate_limiter.get_token()

            except ValueError as e:
                logging.error(f'Error reading contact: {e}')
                # Write bad row to CSV
                with open('bad.csv', 'a', newline='') as bad_file:
                    bad_writer = csv.writer(bad_file)
                    bad_writer.writerow(row)

            except Exception as e:
                logging.error(f'Unexpected error reading contact: {e}')
                # Write error row to CSV
                with open('error.csv', 'a', newline='') as error_file:
                    error_writer = csv.writer(error_file)
                    error_writer.writerow(row)

# Log total time taken
total_end_time = time()
total_time_taken = total_end_time - total_start_time
logging.info(f'Total time taken for the process: {total_time_taken:.2f} seconds')
logging.info(f'Successfully sent messages: {success_count}')
logging.info(f'Failed messages: {failure_count}')

# Close the browser
driver.quit()
logging.info('Browser closed')
