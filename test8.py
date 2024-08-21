import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep, time
import logging
import os
import random
import re

# Setup logging
logging.basicConfig(filename='whatsapp_automation.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def validate_and_format_number(number):
    logging.info(f'Validating number: {number}')

    # Remove any non-numeric characters
    clean_number = re.sub(r'\D', '', number)

    # Check and remove prefixes for Dubai numbers
    if clean_number.startswith('971'):
        clean_number = clean_number[3:]
    elif clean_number.startswith('00971'):
        clean_number = clean_number[5:]
    elif clean_number.startswith('+971'):
        clean_number = clean_number[4:]
    elif clean_number.startswith('04'):
        clean_number = '971' + clean_number[1:]
    elif clean_number.startswith('9714'):
        clean_number = clean_number
    elif clean_number.startswith('009714'):
        clean_number = '971' + clean_number[6:]
    elif clean_number.startswith('+9714'):
        clean_number = '971' + clean_number[5:]
    elif clean_number.startswith('05'):
        clean_number = '971' + clean_number[1:]
    elif clean_number.startswith('9715'):
        clean_number = clean_number
    elif clean_number.startswith('009715'):
        clean_number = '971' + clean_number[6:]
    elif clean_number.startswith('+9715'):
        clean_number = '971' + clean_number[5:]
    elif clean_number.startswith('58'):
        logging.info('Number is a valid Dubai mobile number starting with 58')
        return '971' + clean_number[1:]

    # Check and remove prefixes for Abu Dhabi numbers
    elif clean_number.startswith('56'):
        logging.info('Number is a valid Abu Dhabi mobile number starting with 56')
        return '971' + clean_number[1:]

    # Check and remove prefixes for Sharjah numbers
    elif clean_number.startswith('52'):
        logging.info('Number is a valid Sharjah mobile number starting with 52')
        return '971' + clean_number[1:]

    # Check and remove prefixes for Ajman numbers
    elif clean_number.startswith('50'):
        logging.info('Number is a valid Ajman mobile number starting with 50')
        return '971' + clean_number[1:]

    # Check and remove prefixes for Umm Al Quwain numbers
    elif clean_number.startswith('54'):
        logging.info('Number is a valid Umm Al Quwain mobile number starting with 54')
        return '971' + clean_number[1:]

    # Check and remove prefixes for Ras Al Khaimah numbers
    elif clean_number.startswith('53'):
        logging.info('Number is a valid Ras Al Khaimah mobile number starting with 53')
        return '971' + clean_number[1:]

    # Check and remove prefixes for Fujairah numbers
    elif clean_number.startswith('55'):
        logging.info('Number is a valid Fujairah mobile number starting with 55')
        return '971' + clean_number[1:]

    # Check and remove prefixes for Indian numbers
    if clean_number.startswith('91'):
        clean_number = clean_number[2:]
    elif clean_number.startswith('0091'):
        clean_number = clean_number[4:]
    elif clean_number.startswith('091'):
        clean_number = clean_number[3:]
    elif clean_number.startswith('+91'):
        clean_number = clean_number[3:]

    # Ensure the number is 10 digits after cleaning
    if len(clean_number) == 10:
        logging.info(f'Cleaned number: {clean_number}')

        # Check for Dubai mobile numbers
        if re.match(r'^05\d{8}$', clean_number):
            logging.info('Number is a valid Dubai mobile number starting with 05')
            return '971' + clean_number[1:]
        elif re.match(r'^9715\d{8}$', clean_number):
            logging.info('Number is in correct format: 9715XXXXXXXX')
            return clean_number
        elif re.match(r'^009715\d{8}$', clean_number):
            logging.warning('Number is valid but not in correct format, adjusting to 9715XXXXXXXX')
            return clean_number[2:]
        elif re.match(r'^\+9715\d{8}$', clean_number):
            logging.warning('Number is valid but not in correct format, adjusting to 9715XXXXXXXX')
            return clean_number[1:]

        # Check for Dubai landline numbers
        elif re.match(r'^04\d{7}$', clean_number):
            logging.info('Number is a valid Dubai landline number starting with 04')
            return '971' + clean_number[1:]
        elif re.match(r'^9714\d{7}$', clean_number):
            logging.info('Number is in correct format: 9714XXXXXXX')
            return clean_number
        elif re.match(r'^009714\d{7}$', clean_number):
            logging.warning('Number is valid but not in correct format, adjusting to 9714XXXXXXX')
            return clean_number[2:]
        elif re.match(r'^\+9714\d{7}$', clean_number):
            logging.warning('Number is valid but not in correct format, adjusting to 9714XXXXXXX')
            return clean_number[1:]

        # Check for Indian numbers with various prefixes
        if re.match(r'^\d{10}$', clean_number):  # 10 digits, assuming local Indian number
            logging.info('Number is a valid Indian number without prefix')
            return '91' + clean_number
        elif re.match(r'^91\d{10}$', clean_number):  # 91XXXXXXXXXX
            logging.info('Number is in correct format: 91XXXXXXXXXX')
            return clean_number
        elif re.match(r'^0091\d{10}$', clean_number):  # 0091XXXXXXXXXX
            logging.warning('Number is valid but not in correct format, adjusting to 91XXXXXXXXXX')
            return clean_number[2:]
        elif re.match(r'^091\d{10}$', clean_number):  # 091XXXXXXXXXX
            logging.warning('Number is valid but not in correct format, adjusting to 91XXXXXXXXXX')
            return clean_number[1:]
        elif re.match(r'^\+91\d{10}$', clean_number):  # +91XXXXXXXXXX
            logging.warning('Number is valid but not in correct format, adjusting to 91XXXXXXXXXX')
            return clean_number[1:]

        # Catch-all for valid but incorrectly formatted numbers starting with 91
        elif clean_number.startswith('91') and re.match(r'^\d{12}$', clean_number):
            logging.warning('Number starts with 91 but is not in the expected format, adjusting to 91XXXXXXXXXX')
            return clean_number
    else:
        logging.warning(f'Number format not recognized after cleaning: {number}')
        return None

    pass

# Rate-limiting function
def rate_limit(max_messages_per_hour, wait_time_minutes):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if hasattr(wrapper, 'message_count'):
                wrapper.message_count += 1
            else:
                wrapper.message_count = 1

            if wrapper.message_count > max_messages_per_hour:
                logging.info(f"Rate limit reached. Waiting for {wait_time_minutes} minutes before sending more messages.")
                sleep(wait_time_minutes * 60)
                wrapper.message_count = 1

            return func(*args, **kwargs)
        return wrapper
    return decorator

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
greetings = ["Dear Customer","Hi there", "Hello", "Hi", "Halla Wallah"]

# Start total time tracking
total_start_time = time()

# Counters for success and failure
success_count = 0
failure_count = 0

# CSV file to store failed contacts
failed_contacts_file = 'failed_contacts.csv'

# Open the failed contacts CSV file in append mode
with open(failed_contacts_file, 'a', newline='') as failed_file:
    failed_writer = csv.writer(failed_file)
    # Write the header if the file is empty
    if os.path.getsize(failed_contacts_file) == 0:
        failed_writer.writerow(['Name', 'Number'])

    # Read the input CSV file
    with open('contacts.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            name, number = row
            logging.info(f'Reading contact: {name}, {number}')

            # Validate and format the number
            formatted_number = validate_and_format_number(number)
            if formatted_number is None:
                logging.error(f'Failed to format number for contact {name}: {number}')
                failure_count += 1
                failed_writer.writerow([name, number])
                continue

            # Start time tracking for the individual contact
            start_time = time()

            # Randomly select a greeting
            greeting = random.choice(greetings)

            # Personalize message
            personalized_message = f"{greeting},%0A{common_message}"

            # Rate-limited send message function
            @rate_limit(max_messages_per_hour=200, wait_time_minutes=10)
            def send_message(formatted_number, personalized_message):
                try:
                    # Open chat for contact
                    driver.get(f'https://web.whatsapp.com/send?phone={formatted_number}&text={personalized_message}')
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//div[@title="Attach"]'))
                    )
                    logging.info(f'Opened chat for contact: {name}')

                    # Click the attachment box
                    attachment_box = driver.find_element(By.XPATH, '//div[@title="Attach"]')
                    attachment_box.click()
                    logging.info('Attachment box clicked')

                    # Click the "Document" option
                    document_option = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//span[@class="xdod15v xzwifym x6ikm8r x10wlt62 xlyipyv xuxw1ft" and text()="Document"]'))
                    )
                    document_option.click()
                    logging.info('Document option clicked')

                    # Wait for the file picker to open and interact with it
                    sleep(2)  # Ensure file picker has time to open
                    file_input = driver.find_element(By.XPATH, '//input[@type="file"]')
                    file_input.send_keys(pdf_path)
                    logging.info('PDF file selected through file input')

                    # Wait for the file to upload
                    sleep(15)

                    # Click the send button
                    send_button = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
                    )
                    send_button.click()
                    logging.info(f'Message sent to contact: {name}')

                    # Wait for either the single tick or double tick to confirm message was sent
                    WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.XPATH, '//span[@data-icon="msg-check"] | //span[@data-icon="msg-dblcheck"]'))
                    )
                    logging.info(f'Message sent and confirmed for contact: {name}')
                    return True
                except Exception as e:
                    logging.error(f'Error occurred for contact {name} ({number}): {e}')
                    return False

            MAX_RETRIES = 3
            retries = 0
            while retries < MAX_RETRIES:
                try:
                    if send_message(formatted_number, personalized_message):
                        success_count += 1
                        break
                    else:
                        failure_count += 1
                        failed_writer.writerow([name, number])
                        break
                except Exception as e:
                    logging.error(f'Error occurred for contact {name} ({number}): {e}')
                    retries += 1
                    if retries == MAX_RETRIES:
                        failure_count += 1
                        failed_writer.writerow([name, number])

            # Add random delay to mimic human nature
            delay = random.randint(5, 20)
            sleep(delay)
            logging.info(f'Random delay of {delay} seconds before moving to next contact.')

            # Log the time taken for the individual contact
            end_time = time()
            time_taken = end_time - start_time
            logging.info(f'Time taken for sending to contact {name}: {time_taken:.2f} seconds')

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