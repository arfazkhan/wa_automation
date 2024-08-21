# whatsapp/chat_manager.py
# pylint: disable=no-member

import random
import time
import logging
from utils.validation import validate_and_format_number
from utils.rate_limiting import rate_limit
from utils.file_management import write_failed_contact
from config.settings import GREETINGS, COMMON_MESSAGE
from whatsapp.message_sender import send_message

@rate_limit(max_messages_per_hour=200, wait_time_minutes=10)
def process_contact(driver, name, number, pdf_path, failed_contacts_file):
    formatted_number = validate_and_format_number(number)
    if formatted_number is None:
        logging.error(f'Failed to format number for contact {name}: {number}')
        write_failed_contact(failed_contacts_file, name, number)
        return False

    greeting = random.choice(GREETINGS)
    personalized_message = f"*{greeting},%0A{COMMON_MESSAGE}"

    if send_message(driver, formatted_number, personalized_message, pdf_path):
        return True
    else:
        write_failed_contact(failed_contacts_file, name, number)
        return False
