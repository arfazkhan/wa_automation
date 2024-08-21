# utils/file_management.py
# pylint: disable=no-member

import csv
import os

def create_failed_contacts_file(file_path):
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'Number'])

def write_failed_contact(file_path, name, number):
    with open(file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([name, number])
