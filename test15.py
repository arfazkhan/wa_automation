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
import phonenumbers
import threading
from time import sleep, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Rate limiter settings
RATE_LIMIT = 200 # 200 tokens per hour
TIME_WINDOW = 3600 # 1 hour
COOL_DOWN = 600 # 10 minutes

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

# def validate_and_format_number(number):
#     logging.info(f'Validating number: {number}')
#     clean_number = re.sub(r'\D', '', number)  # Remove any non-digit characters

#     # Handle UAE numbers starting with '05'
#     if clean_number.startswith('05') and len(clean_number) == 10:
#         clean_number = '971' + clean_number[1:]
#         logging.info('Number is a valid UAE number')
#         return clean_number

#     # Remove country codes and prefixes for UAE and India
#     for prefix in ['971', '00971', '+971', '91', '0091', '+91']:
#         if clean_number.startswith(prefix):
#             clean_number = clean_number[len(prefix):]

#     # Add country code if missing for UAE or Indian numbers
#     if len(clean_number) == 10 and clean_number.startswith(('5', '4')):
#         clean_number = '971' + clean_number
#     elif len(clean_number) == 10 and clean_number.startswith(('6', '7', '8', '9')):  # Valid Indian number prefixes
#         clean_number = '91' + clean_number

#     # Validate number format
#     if re.match(r'^971[45]\d{8}$', clean_number):  # UAE number validation
#         logging.info('Number is a valid UAE number')
#         return clean_number
#     elif re.match(r'^91\d{10}$', clean_number):  # Indian number validation
#         logging.info('Number is a valid Indian number')
#         return clean_number

#     logging.warning(f'Number format not recognized after cleaning: {number}')
#     return None
def validate_and_format_number(number):
    logging.info(f'Validating number: {number}')
    
    # List of country codes to check
    country_codes = ['AE', 'IN', 'PK', 'SA', 'QA', 'KW', 'BH', 'OM']
    
    # Remove any non-digit characters
    clean_number = ''.join(filter(str.isdigit, number))
    
    for country in country_codes:
        try:
            # Parse the number with the country code
            possible_number = phonenumbers.parse(clean_number, country)
            
            # Check if the number is valid
            if phonenumbers.is_valid_number(possible_number):
                formatted_number = phonenumbers.format_number(possible_number, phonenumbers.PhoneNumberFormat.E164)
                logging.info(f'Number is valid for {country}: {formatted_number}')
                return formatted_number[1:]  # Remove the '+' at the beginning
        except phonenumbers.phonenumberutil.NumberParseException:
            continue
    
    logging.warning(f'Number format not recognized: {number}')
    return None


def load_sent_contacts(sent_contacts_file):
    """Load sent contacts from a CSV file to avoid duplicate messages."""
    sent_contacts = set()
    if os.path.exists(sent_contacts_file):
        with open(sent_contacts_file, 'r', newline='') as sent_file:
            reader = csv.reader(sent_file)
            next(reader, None)  # Skip header
            for row in reader:
                if row:  # Ensure row is not empty
                    sent_contacts.add(row[0])
                    sent_contacts.add(row[1])
    logging.info(f'Loaded {len(sent_contacts)} sent contacts from {sent_contacts_file}')
    return sent_contacts

def save_sent_contact(sent_contacts_file, name, number, formatted_number):
    """Save successfully sent contact to a CSV file."""
    with open(sent_contacts_file, 'a', newline='') as sent_file:
        writer = csv.writer(sent_file)
        writer.writerow([name, number, formatted_number])
    logging.info(f'Saved sent contact {name} with number {number} and formatted number {formatted_number}')

# Setup WebDriver
logging.info('Initializing Chrome driver with custom user data directory')
chrome_options = Options()
chrome_options.add_argument("user-data-dir=C:/Users/ASUS/wa_auto/data")
driver = webdriver.Chrome(options=chrome_options)
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

# CSV file to store failed and sent contacts
failed_contacts_file = 'failed_contacts.csv'
sent_contacts_file = 'sent_contacts.csv'

# Open the failed contacts CSV file in write mode
with open(failed_contacts_file, 'w', newline='') as failed_file:
    failed_writer = csv.writer(failed_file)
    # Write the header
    failed_writer.writerow(['Name', 'Number'])

# Check and create sent contacts CSV file if not exists
if not os.path.exists(sent_contacts_file):
    with open(sent_contacts_file, 'w', newline='') as sent_file:
        sent_writer = csv.writer(sent_file)
        sent_writer.writerow(['Name', 'Original Number', 'Formatted Number'])

# Load already sent contacts to avoid duplicates
sent_contacts = load_sent_contacts(sent_contacts_file)

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

            # Check if the contact was already processed
            if number in sent_contacts or formatted_number in sent_contacts:
                logging.info(f'Duplicate contact found: {name} with number {number} (formatted: {formatted_number}) has already been processed. Skipping.')
                continue

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
                    # Save the successfully sent contact
                    save_sent_contact(sent_contacts_file, name, number, formatted_number)
                except Exception as e:
                    logging.error(f'Failed to confirm message sent for contact {name} ({number}): {e}')
                    failure_count += 1  # Increment failure counter
                    # Write failed contact to CSV
                    failed_writer.writerow([name, number])

                # Add random delay to mimic human nature
                delay = random.randint(5, 20)
                sleep(delay)
                logging.info(f'Random delay of {delay} seconds before moving to next contact.')

            except Exception as e:
                logging.error(f'Failed to attach PDF or send message for contact {name} ({number}): {e}')
                failure_count += 1  # Increment failure counter
                # Write failed contact to CSV
                failed_writer.writerow([name, number])

            # Log the time taken for the individual contact
            end_time = time()
            time_taken = end_time - start_time
            logging.info(f'Time taken for sending to contact {name}: {time_taken:.2f} seconds')

            # Rate limiting
            rate_limiter.get_token()

        except ValueError as e:
            logging.error(f'Error reading contact: {e}')
            with open('bad.csv', 'a', newline='') as bad_file:
                bad_writer = csv.writer(bad_file)
                bad_writer.writerow(row)

        except Exception as e:
            logging.error(f'Unexpected error reading contact: {e}')
            with open('error.csv', 'a', newline='') as error_file:
                error_writer = csv.writer(error_file)
                error_writer.writerow(row)

# Log the total time taken
total_end_time = time()
total_time_taken = total_end_time - total_start_time
logging.info(f'Total time taken for sending messages: {total_time_taken:.2f} seconds')

# Log the success and failure counts
logging.info(f'Total successful sends: {success_count}')
logging.info(f'Total failed sends: {failure_count}')

# Close the browser
logging.info('Closing the browser')
driver.quit()
