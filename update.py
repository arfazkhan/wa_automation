import csv
import logging
from pathlib import Path

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='contact_removal.log',
        filemode='w'
    )

def remove_failed_contacts(contacts_file, failed_file, output_file, has_header=True):
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Read failed contacts into a set for faster lookup
        failed_contacts = set()
        try:
            with open(failed_file, 'r') as f:
                reader = csv.reader(f)
                if has_header:
                    next(reader)  # Skip header row
                for row in reader:
                    if row:  # Check if row is not empty
                        failed_contacts.add(row[0])  # Assuming the contact is in the first column
            logger.info(f"Successfully read {len(failed_contacts)} failed contacts from {failed_file}")
        except FileNotFoundError:
            logger.error(f"Failed contacts file not found: {failed_file}")
            return
        except csv.Error as e:
            logger.error(f"Error reading failed contacts file: {e}")
            return

        # Read contacts.csv and write to a new file, excluding failed contacts
        try:
            with open(contacts_file, 'r') as input_file, open(output_file, 'w', newline='') as output_file:
                reader = csv.reader(input_file)
                writer = csv.writer(output_file)
                
                # Handle header
                if has_header:
                    header = next(reader, None)
                    if header:
                        writer.writerow(header)
                    else:
                        logger.warning("Header expected but file is empty")
                        return
                
                removed_count = 0
                total_count = 0
                for row in reader:
                    total_count += 1
                    if row and row[0] not in failed_contacts:
                        writer.writerow(row)
                    else:
                        removed_count += 1

            logger.info(f"Successfully processed {total_count} contacts")
            logger.info(f"Removed {removed_count} failed contacts")
            logger.info(f"Updated contacts written to {output_file}")
        except FileNotFoundError:
            logger.error(f"Contacts file not found: {contacts_file}")
        except csv.Error as e:
            logger.error(f"Error processing contacts file: {e}")
        except IOError as e:
            logger.error(f"IOError while writing output file: {e}")

    except Exception as e:
        logger.exception(f"Unexpected error occurred: {e}")

def detect_header(file_path):
    try:
        with open(file_path, 'r') as f:
            first_line = f.readline().strip()
            # Check if the first line contains any non-numeric data
            return any(not part.replace('+', '').replace('-', '').isdigit() for part in first_line.split(','))
    except Exception as e:
        logging.error(f"Error detecting header in {file_path}: {e}")
        return False

if __name__ == "__main__":
    contacts_file = 'contacts.csv'
    failed_file = 'failed_contact.csv'
    output_file = 'updated_contacts.csv'

    if not Path(contacts_file).exists():
        print(f"Error: {contacts_file} not found")
    elif not Path(failed_file).exists():
        print(f"Error: {failed_file} not found")
    else:
        # Attempt to detect headers
        contacts_has_header = detect_header(contacts_file)
        failed_has_header = detect_header(failed_file)
        
        if contacts_has_header != failed_has_header:
            print("Warning: Header detection results differ between files.")
            print(f"{contacts_file} header detected: {contacts_has_header}")
            print(f"{failed_file} header detected: {failed_has_header}")
            user_input = input("Do you want to proceed assuming both files have headers? (y/n): ").lower()
            if user_input != 'y':
                print("Process aborted.")
                exit()
            has_header = True
        else:
            has_header = contacts_has_header

        remove_failed_contacts(contacts_file, failed_file, output_file, has_header)
        print("Process completed. Check the log file for details.")