import csv
import logging
import time
import random

# Setup logging for the test
logging.basicConfig(filename='rate_limit_test.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Mock send_message function for testing
def mock_send_message(formatted_number, personalized_message):
    logging.info(f'Mock send message to {formatted_number} with message: {personalized_message}')
    return True  # Simulate a successful message send

# Rate-limiting function (same as in your original code)
def rate_limit(max_messages_per_hour, wait_time_minutes):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if hasattr(wrapper, 'message_count'):
                wrapper.message_count += 1
            else:
                wrapper.message_count = 1

            if wrapper.message_count > max_messages_per_hour:
                logging.info(f"Rate limit reached. Waiting for {wait_time_minutes} minutes before sending more messages.")
                time.sleep(wait_time_minutes * 60)
                wrapper.message_count = 1

            return func(*args, **kwargs)
        return wrapper
    return decorator

# Rate-limited mock_send_message function
@rate_limit(max_messages_per_hour=5, wait_time_minutes=1)  # Set lower limits for testing
def rate_limited_mock_send_message(formatted_number, personalized_message):
    return mock_send_message(formatted_number, personalized_message)

# Test parameters
test_contacts = [("Test User", f"+971{str(i).zfill(9)}") for i in range(1, 21)]  # 20 test contacts
common_message = "This is a test message."

# Start total time tracking
total_start_time = time.time()

# Counters for success and failure
success_count = 0
failure_count = 0

# Open the failed contacts CSV file in write mode
with open('failed_contacts_test.csv', 'w', newline='') as failed_file:
    failed_writer = csv.writer(failed_file)
    # Write the header
    failed_writer.writerow(['Name', 'Number'])

    for name, number in test_contacts:
        logging.info(f'Testing contact: {name}, {number}')
        
        # Personalize message
        personalized_message = f"Test message for {name}: {common_message}"

        # Call the rate-limited send_message function
        if rate_limited_mock_send_message(number, personalized_message):
            success_count += 1
        else:
            failure_count += 1
            # Write failed contact to CSV
            failed_writer.writerow([name, number])

        # Add random delay to mimic human nature
        delay = random.randint(1, 3)  # Shorter delays for testing
        time.sleep(delay)
        logging.info(f'Random delay of {delay} seconds before moving to next contact.')

# Log the total time taken
total_end_time = time.time()
total_time_taken = total_end_time - total_start_time
logging.info(f'Total time taken for test: {total_time_taken:.2f} seconds')

# Log the success and failure counts
logging.info(f'Total successful sends: {success_count}')
logging.info(f'Total failed sends: {failure_count}')
