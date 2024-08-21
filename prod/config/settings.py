# config/settings.py
# pylint: disable=no-member

# Path to the PDF file
PDF_PATH = 'menu.pdf'

# Rate limiting settings
MAX_MESSAGES_PER_HOUR = 200
WAIT_TIME_MINUTES = 10

# Common message
COMMON_MESSAGE = """Greetings from City Burger Restaurant..!%0AWe are delighted to share our latest menu with you.%0A%0AFor orders, visit: https://wa.me/97142211158 or click on any pages in the menu."""

# Greetings list
GREETINGS = ["Dear Customer","Hi there", "Hello", "Hi", "Halla Wallah"]
