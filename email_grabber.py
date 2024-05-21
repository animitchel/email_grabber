import imaplib
import os
import email
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import time
import datetime
from expenses_category import EXPENSE_CATEGORIES
from sent_requests import sent_requests


load_dotenv()

# Connect to Gmail's IMAP server
mail = imaplib.IMAP4_SSL('imap.gmail.com')

time.sleep(1)

mail.login(os.getenv('USER_EMAIL'), password=os.getenv('USER_EMAIL_APP_PASSWORD'))

# Select the mailbox (e.g., 'INBOX')
mail.select('inbox')

# Calculate the date for SINCE criterion (e.g., one day ago)
since_date = datetime.datetime.now() - datetime.timedelta(days=1)
# today = datetime.date.today()
since_date_str = since_date.strftime("%d-%b-%Y")  # Format the date according to IMAP's date format
# today_date = today.strftime("%d-%b-%Y")

# Search for emails received since the calculated date
result, data = mail.search(None, f'(SINCE "{since_date_str}" FROM "Globus Bank Ltd")')

payload = {}


def transaction_income_form_data(
        description_str, amount_str, expenses_categories=EXPENSE_CATEGORIES, all_trans_bud=False):
    try:
        category_name = next(category for category in expenses_categories if category in description_str)
    except StopIteration:
        category_name = 'Other'

    amount_list = [char for char in amount_str if char.isdigit() or char == '.']

    amount_joint_str = ''.join(amount_list)
    new_amount = float(amount_joint_str)

    amount_list.clear()

    # print( f"description: {description_str}, amount: {new_amount}, category: {category_name}, all_trans_bud: {
    # all_trans_bud}" )

    return category_name, new_amount, description_str, all_trans_bud


# Iterate over email IDs
for email_id in data[0].split()[::-1]:  # Reverse the order of email IDs:
    # Fetch the email
    result_str, msg_data = mail.fetch(email_id, '(RFC822)')
    raw_email = msg_data[0][1]

    # Parse the email message
    msg = email.message_from_bytes(raw_email)

    # Access email headers and content
    sender = msg['From']
    subject = msg['Subject']
    date = msg['Date']
    content = msg.get_payload()

    # Process the email as needed
    if 'Globus' in sender and 'Debit' in subject or 'Credit' in subject:
        # Initialize variables to store plain text and HTML content
        plain_text_content = ''
        html_content = ''

        # Process each part of the email message
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == 'text/plain':
                # Plain text content
                plain_text_content += part.get_payload(decode=True).decode('utf-8')
            elif content_type == 'text/html':
                # HTML content
                html_content += part.get_payload(decode=True).decode('utf-8')

        # Parse the HTML content using Beautiful Soup
        soup = BeautifulSoup(html_content, 'html.parser')
        # plain_text = soup.prettify()
        # print(plain_text)

        # Find specific elements in the HTML content

        description_td = soup.find('td', class_='editable html',
                                   string=lambda string: string and "Description" in string)
        transaction_amount_td = soup.find('td', class_='editable',
                                          string=lambda string: string and "Transaction Amount" in string)


        def elements_to_string(element, class_name, element_name, func_name):

            if element:
                value_td = element.find_next(element_name, class_=class_name)
                if value_td:
                    value = value_td.get_text(strip=True)
                    if func_name == 'description_td':
                        description = value.strip("9013435231")
                        return description

                    if func_name == 'transaction_amount':
                        amount = value.strip("-NGN").strip(",")
                        return amount
                else:
                    print("Value not found")
            else:
                print("Description not found")


        description = elements_to_string(
            element=description_td,
            class_name='editable html',
            element_name='td',
            func_name='description_td'
        )

        amount = elements_to_string(
            element=transaction_amount_td,
            class_name='editable',
            element_name='td',
            func_name='transaction_amount'
        )

        """
        NOTICE!!!
        
            - skip transaction
            
            _ take from All Transaction Budget attach to transaction
        
        """

        if '-' not in description or 'Credit' in subject:
            if '_' in description or 'Airtime' in description:
                category, new_float_amount, description, all_trans_bud = \
                    transaction_income_form_data(description, amount, all_trans_bud=True)
            else:
                category, new_float_amount, description, all_trans_bud = \
                    transaction_income_form_data(description, amount)

            # print(category, new_float_amount, description, all_trans_bud)

            payload['category'] = category
            payload['amount'] = new_float_amount
            payload['description'] = description
            payload['is_all_trans_bud'] = all_trans_bud

            if 'Credit' in subject:
                payload['category'] = "business income"
                payload['notes'] = description
                payload.pop('is_all_trans_bud')
                payload.pop('description')
                sent_requests(payload, income_post_request=True)
            else:
                sent_requests(payload)

            payload.clear()

            # Print or process the structured content as needed
            # print("Plain Text Content:")
            # print(plain_text_content)
            # print("HTML Content:")
            # print(html_content)

# Logout from the server
mail.logout()
