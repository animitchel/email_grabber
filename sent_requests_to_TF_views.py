import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import time

load_dotenv()


def get_csrf_token(session, url):
    try:
        response = session.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'}).get('value')
            return csrf_token
        else:
            print(f"Failed to retrieve CSRF token. Status code: {response.status_code}")
            print('retrying...')
            get_csrf_token(session, url)

            # return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


def login(url, username, password):
    try:
        # Create a session to persist cookies (including CSRF token)
        session = requests.Session()
        csrf_token = get_csrf_token(session, url)
        if csrf_token:
            # Construct the login data with username, password, and CSRF token
            login_data = {
                'username': username,
                'password': password,
                'csrfmiddlewaretoken': csrf_token
            }
            # Set the CSRF token in the headers
            session.headers.update({'X-CSRFToken': csrf_token, 'Referer': url})
            # Send a POST request to the login endpoint
            response = session.post(url, data=login_data, allow_redirects=True)
            # Check if login was successful (status code 200)
            if response.status_code == 200:
                print("Login successful!")
                return session  # Return the session object for further requests
            else:
                print(f"Failed to login. Status code: {response.status_code}")
                return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


login_url = 'https://track-finance.onrender.com/login/'
# login_url = 'http://127.0.0.1:8000/login/'

username = os.environ.get('LOGIN_USERNAME')
password = os.environ.get('LOGIN_PASSWORD')

# username = os.environ.get('LOCAL_LOGIN_USERNAME')
# password = os.environ.get('LOCAL_LOGIN_PASSWORD')

session = login(login_url, username, password)

if session:

    start_time = time.time()

    endpoint = [
        'budget-overview/', 'recurring-transactions/', 'recurring-incomes/', 'notifications/',
        'overview/',
    ]

    for i in range(len(endpoint)):
        res = session.get(url=f'https://track-finance.onrender.com/{endpoint[i]}', allow_redirects=True)
        # res = session.get(url=f'http://127.0.0.1:8000/{endpoint[i]}', allow_redirects=True)
        # print(res.text)

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"Request job ran successfully! in {elapsed_time} seconds")
else:
    print("Login failed. Please check your credentials.")
