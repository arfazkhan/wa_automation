# whatsapp/driver_manager.py
# pylint: disable=no-member

from selenium import webdriver
import logging

def init_driver():
    logging.info('Initializing Chrome driver')
    driver = webdriver.Chrome()
    driver.get('https://web.whatsapp.com/')
    return driver
