import imaplib
import os
import email
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import time
import datetime

load_dotenv()

# Connect to Gmail's IMAP server
mail = imaplib.IMAP4_SSL('imap.gmail.com')

time.sleep(5)

mail.login(os.getenv('USER_EMAIL'), password=os.getenv('USER_EMAIL_APP_PASSWORD'))

# Select the mailbox (e.g., 'INBOX')
mail.select('inbox')

# Calculate the date for SINCE criterion (e.g., one day ago)
# since_date = datetime.datetime.now() - datetime.timedelta(days=1)
today = datetime.date.today()
# since_date_str = since_date.strftime("%d-%b-%Y")  # Format the date according to IMAP's date format
today_date = today.strftime("%d-%b-%Y")

# Search for emails received since the calculated date
result, data = mail.search(None, f'(SINCE "{today_date}" FROM "Globus Bank Ltd")')

# Search for emails
# result, data = mail.search(None, 'ALL')

# Iterate over email IDs
for email_id in data[0].split()[::-1]:  # Reverse the order of email IDs:
    # Fetch the email
    result, msg_data = mail.fetch(email_id, '(RFC822)')
    raw_email = msg_data[0][1]

    # Parse the email message
    msg = email.message_from_bytes(raw_email)

    # Access email headers and content
    sender = msg['From']
    subject = msg['Subject']
    date = msg['Date']
    content = msg.get_payload()

    # Process the email as needed
    if 'Globus' in sender:
        # print(f"From: {sender}, Subject: {subject}, Date: {date}")
        # print(content)

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

        # Print or process the structured content as needed
        # print(f"From: {sender}, Subject: {subject}, Date: {date}")
        # print("Plain Text Content:")
        # print(plain_text_content)
        # print("HTML Content:")
        # print(html_content)

        # Assume 'html_content' contains the HTML content of an email
        # Parse the HTML content using Beautiful Soup
        soup = BeautifulSoup(html_content, 'html.parser')
        # plain_text = soup.prettify()
        # print(plain_text)

        # Find specific elements in the HTML content
        # Example: Extract the text from all <p> tags
        # paragraphs = soup.find_all('table tr tb')
        # for p in paragraphs:
        #     print(p.text)

        description_td = soup.find('td', class_='editable html',
                                   string=lambda string: string and "Description" in string)
        transaction_amount_td = soup.find('td', class_='editable',
                                          string=lambda string: string and "Transaction Amount" in string)

        # If the description_td is found, get the text content of the next <td> element
        def elements_to_string(element, class_name, element_name, func_name):

            if element:
                value_td = element.find_next(element_name, class_=class_name)
                if value_td:
                    value = value_td.get_text(strip=True)
                    if func_name == 'description_td':
                        print(value.strip("9013435231"))
                    if func_name == 'transaction_amount':
                        print(value.strip("-NGN").strip(","))
                else:
                    print("Value not found")
            else:
                print("Description not found")

        elements_to_string(element=description_td, class_name='editable html', element_name='td', func_name='description_td')
        elements_to_string(element=transaction_amount_td, class_name='editable', element_name='td', func_name='transaction_amount')

        print(f"From: {sender}, Subject: {subject}, Date: {date}")
        # print("Plain Text Content:")
        # print(plain_text_content)
        # print("HTML Content:")
        # print(html_content)

        # if description_td:
        #     value_td = description_td.find_next('td', class_='editable html')
        #     if value_td:
        #         value = value_td.get_text(strip=True)
        #         print(value)
        #     else:
        #         print("Value not found")
        # else:
        #     print("Description not found")

# Logout from the server
mail.logout()
