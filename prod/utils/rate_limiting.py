# utils/rate_limiting.py
# pylint: disable=no-member

import logging
from time import sleep

def rate_limit(max_messages_per_hour, wait_time_minutes):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if hasattr(wrapper, 'message_count'):
                wrapper.message_count += 1
            else:
                wrapper.message_count = 1

            if wrapper.message_count > max_messages_per_hour:
                logging.info(f"Rate limit reached. Waiting for {wait_time_minutes} minutes before sending more messages.")
                sleep(wait_time_minutes * 60)
                wrapper.message_count = 1

            return func(*args, **kwargs)
        return wrapper
    return decorator
