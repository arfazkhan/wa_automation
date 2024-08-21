# whatsapp/message_sender.py
# pylint: disable=no-member

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import logging
import os

def send_message(driver, number, message, pdf_path):
    try:
        driver.get(f'https://web.whatsapp.com/send?phone={number}&text={message}')
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@title="Attach"]'))
        )
        logging.info(f'Opened chat for contact: {number}')
        
        attachment_box = driver.find_element(By.XPATH, '//div[@title="Attach"]')
        attachment_box.click()
        
        document_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//span[@class="xdod15v xzwifym x6ikm8r x10wlt62 xlyipyv xuxw1ft" and text()="Document"]'))
        )
        document_option.click()

        sleep(2) # Ensure file picker has time to open
        
        file_input = driver.find_element(By.XPATH, '//input[@type="file"]')
        file_input.send_keys(pdf_path)
        
        logging.info('PDF file selected through file input')
        sleep(15)
        
        send_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
        )
        send_button.click()
        
        logging.info(f'Message sent to contact: {number}')
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//span[@data-icon="msg-check"] | //span[@data-icon="msg-dblcheck"]'))
        )
        logging.info(f'Message sent and confirmed for contact: {number}')
        return True
    except Exception as e:
        logging.error(f'Error while sending message to contact {number}: {e}')
        return False
