import logging
import threading
from time import sleep, time

# Setup logging for the test
logging.basicConfig(filename='ratelimit_test.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Rate limiter settings
RATE_LIMIT = 5
TIME_WINDOW = 30  # 2 minutes
COOL_DOWN = 10   # 10 seconds

class RateLimiter:
    def __init__(self):
        self.tokens = RATE_LIMIT
        self.last_reset = time()
        self.lock = threading.Lock()
        logging.info(f'RateLimiter initialized with {self.tokens} tokens and last reset at {self.last_reset}')

    def get_token(self):
        with self.lock:
            current_time = time()
            elapsed_time = current_time - self.last_reset

            # Update tokens based on elapsed time
            self.tokens = min(RATE_LIMIT, self.tokens + (elapsed_time / TIME_WINDOW) * RATE_LIMIT)
            self.last_reset = current_time

            if self.tokens < 1:
                logging.info('Rate limit exceeded. Entering cooldown period.')
                # Log the state before cooldown
                logging.info(f'Tokens before cooldown: {self.tokens}')
                sleep(COOL_DOWN)
                # After cooldown, reset tokens and update last_reset to the current time
                self.tokens = RATE_LIMIT
                self.last_reset = time()
                # Log the state after cooldown
                logging.info(f'Tokens after cooldown: {self.tokens}')
                logging.info('Cooldown period ended. Tokens reset.')

            self.tokens -= 1
            logging.info(f'Token acquired. Remaining tokens: {self.tokens}')

def test_rate_limiter():
    logging.info('Starting rate limiter test')
    
    # Create a rate limiter instance
    rate_limiter = RateLimiter()

    # Variables to track test results
    start_time = time()
    delays = []

    # Simulate acquiring tokens
    for _ in range(RATE_LIMIT + 1):  # Request more tokens than the limit to test cooldown
        request_start = time()
        rate_limiter.get_token()
        request_end = time()
        
        # Calculate time taken for each request
        delays.append(request_end - request_start)
        
        # Add a small delay between requests
        sleep(1)
    
    # Check if the cooldown was triggered
    elapsed_time = time() - start_time
    logging.info(f'Time elapsed during token requests: {elapsed_time:.2f} seconds')
    logging.info(f'Time between token requests: {delays}')

    # Assert if the cooldown period was respected
    assert len(delays) > 1, "Rate limiter did not wait before the cooldown period."
    assert elapsed_time >= COOL_DOWN, f"Rate limiter cooldown period should be at least {COOL_DOWN} seconds."

    logging.info('Rate limiter test passed.')

# Call the test function if the script is run directly
if __name__ == "__main__":
    test_rate_limiter()
