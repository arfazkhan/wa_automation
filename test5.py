import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep, time
import logging
import os
import random 

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

# Open the failed contacts CSV file in write mode
with open(failed_contacts_file, 'w', newline='') as failed_file:
    failed_writer = csv.writer(failed_file)
    # Write the header
    failed_writer.writerow(['Name', 'Number'])

    # Read the input CSV file
    with open('contacts.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            name, number = row
            logging.info(f'Reading contact: {name}, {number}')

            # Start time tracking for the individual contact
            start_time = time()

            # Randomly select a greeting
            greeting = random.choice(greetings)

            # Personalize message
            personalized_message = f"*_Please Ignore the following message. This is just a test run for the promotion of City Burger._*%0A%0A*KINDLY IGNORE!!!!*%0A%0A{greeting},%0A{common_message}"

            # Open chat for contact
            try:
                driver.get(f'https://web.whatsapp.com/send?phone={number}&text={personalized_message}')
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@title="Attach"]'))
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

                # Wait for either the single tick or double tick to confirm message was sent
                try:
                    WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.XPATH, '//span[@data-icon="msg-check"] | //span[@data-icon="msg-dblcheck"]'))
                    )
                    logging.info(f'Message sent and confirmed for contact: {name}')
                    success_count += 1  # Increment success counter
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
