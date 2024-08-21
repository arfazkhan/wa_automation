# utils/validation.py
# pylint: disable=no-member

import re
import logging

def validate_and_format_number(number):
    logging.info(f'Validating number: {number}')

    # Remove any non-numeric characters
    clean_number = re.sub(r'\D', '', number)

    # Check and remove prefixes for Dubai numbers
    if clean_number.startswith(('971', '00971', '+971')):
        clean_number = clean_number.lstrip('971').lstrip('00971').lstrip('+971')
    elif clean_number.startswith(('04', '009714', '+9714', '05', '009715', '+9715', '58', '56', '52', '50', '54', '53', '55')):
        clean_number = clean_number.lstrip('04').lstrip('009714').lstrip('+9714').lstrip('05').lstrip('009715').lstrip('+9715').lstrip('58').lstrip('56').lstrip('52').lstrip('50').lstrip('54').lstrip('53').lstrip('55')
        clean_number = '971' + clean_number

    # Check and remove prefixes for Indian numbers
    if clean_number.startswith(('91', '0091', '091', '+91')):
        clean_number = clean_number.lstrip('91').lstrip('0091').lstrip('091').lstrip('+91')
        if len(clean_number) == 10:
            return '91' + clean_number
        else:
            logging.warning(f'Number format not recognized after cleaning: {number}')
            return None
    return clean_number
