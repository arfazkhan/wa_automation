# logging/logger.py
# pylint: disable=no-member

import logging

def setup_logger():
    logging.basicConfig(filename='whatsapp_automation.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    return logging.getLogger()
