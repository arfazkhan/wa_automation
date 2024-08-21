# import csv
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from time import sleep, time
# import logging
# import os
# import random
# import re

# # Setup logging
# logging.basicConfig(filename='whatsapp_automation.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# # Setup WebDriver
# logging.info('Initializing Chrome driver')
# driver = webdriver.Chrome()
# driver.get('https://web.whatsapp.com/')

# # Wait for QR code scan
# input('Enter anything after scanning QR code')
# logging.info('QR code scanned')

# # Path to the PDF file
# pdf_path = os.path.abspath('menu.pdf')

# common_message = """Greetings from City Burger Restaurant..!%0AWe are delighted to share our latest menu with you.%0A%0AFor orders, visit: https://wa.me/97142211158 or click on any pages in the menu."""

# # Define greetings list
# greetings = ["Dear Customer", "Hi there", "Hello", "Hi", "Halla Wallah"]

# # Start total time tracking
# total_start_time = time()

# # Counters for success and failure
# success_count = 0
# failure_count = 0

# # CSV file to store failed contacts
# failed_contacts_file = 'failed_contacts.csv'

# # Phone number validation function
# def validate_and_format_number(number):
#     logging.info(f'Validating number: {number}')
    
#     # Remove any non-numeric characters
#     clean_number = re.sub(r'\D', '', number)
    
#     # Check and remove prefixes for Dubai numbers
#     if clean_number.startswith('971'):
#         clean_number = clean_number[3:]
#     elif clean_number.startswith('00971'):
#         clean_number = clean_number[5:]
#     elif clean_number.startswith('+971'):
#         clean_number = clean_number[4:]
#     elif clean_number.startswith('04'):
#         clean_number = '971' + clean_number[1:]
#     elif clean_number.startswith('9714'):
#         clean_number = clean_number
#     elif clean_number.startswith('009714'):
#         clean_number = '971' + clean_number[6:]
#     elif clean_number.startswith('+9714'):
#         clean_number = '971' + clean_number[5:]
#     elif clean_number.startswith('05'):
#         clean_number = '971' + clean_number[1:]
#     elif clean_number.startswith('9715'):
#         clean_number = clean_number
#     elif clean_number.startswith('009715'):
#         clean_number = '971' + clean_number[6:]
#     elif clean_number.startswith('+9715'):
#         clean_number = '971' + clean_number[5:]

#     # Check and remove prefixes for Indian numbers
#     if clean_number.startswith('91'):
#         clean_number = clean_number[2:]
#     elif clean_number.startswith('0091'):
#         clean_number = clean_number[4:]
#     elif clean_number.startswith('091'):
#         clean_number = clean_number[3:]
#     elif clean_number.startswith('+91'):
#         clean_number = clean_number[3:]
    
#     # Ensure the number is 10 digits after cleaning
#     if len(clean_number) == 10:
#         logging.info(f'Cleaned number: {clean_number}')
        
#         # Check for Dubai mobile numbers
#         if re.match(r'^05\d{8}$', clean_number):
#             logging.info('Number is a valid Dubai mobile number starting with 05')
#             return '971' + clean_number[1:]
#         elif re.match(r'^9715\d{8}$', clean_number):
#             logging.info('Number is in correct format: 9715XXXXXXXX')
#             return clean_number
#         elif re.match(r'^009715\d{8}$', clean_number):
#             logging.warning('Number is valid but not in correct format, adjusting to 9715XXXXXXXX')
#             return clean_number[2:]
#         elif re.match(r'^\+9715\d{8}$', clean_number):
#             logging.warning('Number is valid but not in correct format, adjusting to 9715XXXXXXXX')
#             return clean_number[1:]
        
#         # Check for Dubai landline numbers
#         elif re.match(r'^04\d{7}$', clean_number):
#             logging.info('Number is a valid Dubai landline number starting with 04')
#             return '971' + clean_number[1:]
#         elif re.match(r'^9714\d{7}$', clean_number):
#             logging.info('Number is in correct format: 9714XXXXXXX')
#             return clean_number
#         elif re.match(r'^009714\d{7}$', clean_number):
#             logging.warning('Number is valid but not in correct format, adjusting to 9714XXXXXXX')
#             return clean_number[2:]
#         elif re.match(r'^\+9714\d{7}$', clean_number):
#             logging.warning('Number is valid but not in correct format, adjusting to 9714XXXXXXX')
#             return clean_number[1:]
        
#         # Check for Indian numbers with various prefixes
#         if re.match(r'^\d{10}$', clean_number):  # 10 digits, assuming local Indian number
#             logging.info('Number is a valid Indian number without prefix')
#             return '91' + clean_number
#         elif re.match(r'^91\d{10}$', clean_number):  # 91XXXXXXXXXX
#             logging.info('Number is in correct format: 91XXXXXXXXXX')
#             return clean_number
#         elif re.match(r'^0091\d{10}$', clean_number):  # 0091XXXXXXXXXX
#             logging.warning('Number is valid but not in correct format, adjusting to 91XXXXXXXXXX')
#             return clean_number[2:]
#         elif re.match(r'^091\d{10}$', clean_number):  # 091XXXXXXXXXX
#             logging.warning('Number is valid but not in correct format, adjusting to 91XXXXXXXXXX')
#             return clean_number[1:]
#         elif re.match(r'^\+91\d{10}$', clean_number):  # +91XXXXXXXXXX
#             logging.warning('Number is valid but not in correct format, adjusting to 91XXXXXXXXXX')
#             return clean_number[1:]
        
#         # Catch-all for valid but incorrectly formatted numbers starting with 91
#         elif clean_number.startswith('91') and re.match(r'^\d{12}$', clean_number):
#             logging.warning('Number starts with 91 but is not in the expected format, adjusting to 91XXXXXXXXXX')
#             return clean_number
        
#     else:
#         logging.warning(f'Number format not recognized after cleaning: {number}')
#         return None

# # Function to check for message status
# def check_message_status(driver, name, formatted_number):
#     try:
#         # Wait for either the single tick, double tick, or msg-time
#         WebDriverWait(driver, 30).until(
#             EC.presence_of_element_located((By.XPATH, '//span[@data-icon="msg-check"] | //span[@data-icon="msg-dblcheck"] | //span[@data-icon="msg-time"]'))
#         )
#         logging.info(f'Initial message status found for contact: {name}')

#         # Check if the message is still pending
#         for _ in range(3):  # Retry 3 times
#             if driver.find_elements(By.XPATH, '//span[@data-icon="msg-check"] | //span[@data-icon="msg-dblcheck"]'):
#                 logging.info(f'Message sent and confirmed for contact: {name}')
#                 return True  # Success
#             elif driver.find_elements(By.XPATH, '//span[@data-icon="msg-time"]'):
#                 logging.info(f'Message is pending for contact: {name}. Waiting before retrying...')
#                 sleep(random.randint(5, 10))  # Wait before retrying
#             else:
#                 logging.info(f'Message status unknown for contact: {name}. Retrying...')
#                 sleep(random.randint(5, 10))

#         logging.error(f'Failed to send message to contact {name} ({formatted_number}): message stuck on pending')
#         return False  # Failure

#     except Exception as e:
#         logging.error(f'Error while checking message status for contact {name} ({formatted_number}): {e}')
#         return False  # Failure

# # Open the failed contacts CSV file in write mode
# with open(failed_contacts_file, 'w', newline='') as failed_file:
#     failed_writer = csv.writer(failed_file)
#     # Write the header
#     failed_writer.writerow(['Name', 'Number'])

#     # Read the input CSV file
#     with open('contacts.csv', 'r') as file:
#         reader = csv.reader(file)
#         for row in reader:
#             name, number = row
#             logging.info(f'Reading contact: {name}, {number}')

#             # Validate and format the number
#             formatted_number = validate_and_format_number(number)
#             if not formatted_number:
#                 logging.error(f'Invalid number for contact {name}: {number}')
#                 failure_count += 1
#                 failed_writer.writerow([name, number])
#                 continue

#             logging.info(f'Formatted number: {formatted_number}')

#             # Start time tracking for the individual contact
#             start_time = time()

#             # Randomly select a greeting
#             greeting = random.choice(greetings)

#             # Personalize message
#             personalized_message = f"*_Please Ignore the following message. This is just a test run for the promotion of City Burger._*%0A%0A*KINDLY IGNORE!!!!*%0A%0A{greeting},%0A{common_message}"

#             # Open chat for contact
#             try:
#                 driver.get(f'https://web.whatsapp.com/send?phone={formatted_number}&text={personalized_message}')
#                 WebDriverWait(driver, 10).until(
#                     EC.presence_of_element_located((By.XPATH, '//div[@title="Attach"]'))
#                 )
#                 logging.info(f'Opened chat for contact: {name}')
#             except Exception as e:
#                 logging.error(f'Failed to open chat for contact {name} ({formatted_number}): {e}')
#                 failure_count += 1  # Increment failure counter
#                 # Write failed contact to CSV
#                 failed_writer.writerow([name, formatted_number])
#                 continue

#             # Click the attachment box
#             try:
#                 attachment_box = driver.find_element(By.XPATH, '//div[@title="Attach"]')
#                 attachment_box.click()
#                 logging.info('Attachment box clicked')

#                 # Click the "Document" option
#                 document_option = WebDriverWait(driver, 10).until(
#                     EC.element_to_be_clickable((By.XPATH, '//span[@class="xdod15v xzwifym x6ikm8r x10wlt62 xlyipyv xuxw1ft" and text()="Document"]'))
#                 )
#                 document_option.click()
#                 logging.info('Document option clicked')

#                 # Wait for the file picker to open and interact with it
#                 sleep(2)  # Ensure file picker has time to open

#                 # Use JavaScript to set the file directly (if the file input is available)
#                 file_input = driver.find_element(By.XPATH, '//input[@accept="*/*"]')
#                 file_input.send_keys(pdf_path)
#                 logging.info(f'File {pdf_path} selected')

#                 # Wait for the send button to be clickable and then click it
#                 send_button = WebDriverWait(driver, 10).until(
#                     EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
#                 )
#                 send_button.click()
#                 logging.info(f'Message sent to contact: {name}')

#             except Exception as e:
#                 logging.error(f'Failed to send document to contact {name} ({formatted_number}): {e}')
#                 failure_count += 1  # Increment failure counter
#                 # Write failed contact to CSV
#                 failed_writer.writerow([name, formatted_number])
#                 continue

#             # Wait for confirmation that the message was sent
#             if check_message_status(driver, name, formatted_number):
#                 success_count += 1  # Increment success counter
#             else:
#                 failure_count += 1  # Increment failure counter
#                 # Write failed contact to CSV
#                 failed_writer.writerow([name, formatted_number])

#             # End time tracking for the individual contact
#             end_time = time()
#             elapsed_time = end_time - start_time
#             logging.info(f'Time taken for {name}: {elapsed_time:.2f} seconds')

#             # Random delay to mimic human behavior
#             sleep(random.randint(5, 10))

# # End total time tracking
# total_end_time = time()
# total_elapsed_time = total_end_time - total_start_time
# logging.info(f'Total time taken: {total_elapsed_time:.2f} seconds')

# # Log final success and failure counts
# logging.info(f'Successful sends: {success_count}')
# logging.info(f'Failed sends: {failure_count}')