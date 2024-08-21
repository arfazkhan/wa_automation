# main.py
# pylint: disable=no-member

import csv
import logging
import random
import time
from logging.logger import setup_logger
from whatsapp.driver_manager import init_driver
from whatsapp.chat_manager import process_contact
from utils.file_management import create_failed_contacts_file
from config.settings import PDF_PATH

def main():
    setup_logger()
    
    driver = init_driver()
    
    input('Enter anything after scanning QR code')
    logging.info('QR code scanned')
    
    failed_contacts_file = 'failed_contacts.csv'
    create_failed_contacts_file(failed_contacts_file)

    total_start_time = time.time()
    success_count = 0
    failure_count = 0
    
    with open('contacts.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            name, number = row
            logging.info(f'Reading contact: {name}, {number}')
            
            if process_contact(driver, name, number, PDF_PATH, failed_contacts_file):
                success_count += 1
            else:
                failure_count += 1

            # Add random delay to mimic human nature
            delay = random.randint(5, 20)
            time.sleep(delay)
            logging.info(f'Random delay of {delay} seconds before moving to the next contact')

    total_end_time = time.time()
    total_duration = total_end_time - total_start_time
    logging.info(f'Total duration: {total_duration / 60:.2f} minutes')
    logging.info(f'Successful messages: {success_count}')
    logging.info(f'Failed messages: {failure_count}')

    driver.quit()

if __name__ == '__main__':
    main()
