import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep, time
import logging
import os

# Setup logging
logging.basicConfig(filename='whatsapp_automation.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Setup WebDriver
logging.info('Initializing Chrome driver')
driver = webdriver.Chrome()
driver.get('https://web.whatsapp.com/')

# Wait for QR code scan
input('Enter anything after scanning QR code')
logging.info('QR code scanned')

# Path to the PDF file
pdf_path = os.path.abspath('menu.pdf')

common_message = """Greetings from City Burger Restaurant..!%0AWe are delighted to share our latest menu with you.%0A%0AFor orders, visit: https://wa.me/97142211158"""

# Start total time tracking
total_start_time = time()

# Read CSV file
with open('contacts.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        name, number = row
        logging.info(f'Reading contact: {name}, {number}')

        # Start time tracking for the individual contact
        start_time = time()

        # Personalize message
        personalized_message = f"*_Please Ignore the following message. This is just a test run for the promotion of City Burger._*%0A%0A*KINDLY IGNORE!!!!*%0A%0ADear {name},%0A{common_message}"

        # Open chat for contact
        try:
            driver.get(f'https://web.whatsapp.com/send?phone={number}&text={personalized_message}')
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@title="Attach"]'))
            )
            logging.info(f'Opened chat for contact: {name}')
        except Exception as e:
            logging.error(f'Failed to open chat for contact {name} ({number}): {e}')
            continue

        # Click the attachment box
        try:
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

            # Use JavaScript to set the file directly (if the file input is available)
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
        except Exception as e:
            logging.error(f'Failed to attach PDF or send message for contact {name} ({number}): {e}')

        # Log the time taken for the individual contact
        end_time = time()
        time_taken = end_time - start_time
        logging.info(f'Time taken for sending to contact {name}: {time_taken:.2f} seconds')

        # Wait before sending to next contact
        sleep(15)
        logging.info('Waiting before sending to next contact...')

# Log the total time taken
total_end_time = time()
total_time_taken = total_end_time - total_start_time
logging.info(f'Total time taken for sending messages: {total_time_taken:.2f} seconds')

# Close the browser
logging.info('Closing the browser')
driver.quit()
