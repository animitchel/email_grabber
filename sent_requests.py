# import chardet
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()


def sent_requests(data_payload):
    def get_csrf_token(session, url):
        try:
            response = session.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'}).get('value')
                return csrf_token
            else:
                print(f"Failed to retrieve CSRF token. Status code: {response.status_code}")

                return None
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

    def post_request(url, session_object, payload):
        csrf_token = get_csrf_token(session_object, url)

        headers = {'X-CSRFToken': csrf_token}
        if csrf_token:
            payload['csrfmiddlewaretoken'] = csrf_token

            # Set the CSRF token in the headers
            # session_object.headers.update({'X-CSRFToken': csrf_token, 'Referer': url})

        response = session_object.post(
            url,
            data=payload,
            allow_redirects=True,
            headers=headers
        )
        # Raise an HTTPError if the request was unsuccessful
        # print(response.text)
        response.raise_for_status()

        return response

    session = login(login_url, username, password)
    if session:
        print("Login successful!")

        endpoint = ['budget-overview/', 'recurring-transactions/', 'recurring-incomes/', 'notifications/']
        for i in range(len(endpoint)):
            res = session.get(url=f'https://track-finance.onrender.com/{endpoint[i]}', allow_redirects=True)
            # res = session.get(url=f'http://127.0.0.1:8000/{endpoint[i]}', allow_redirects=True)

        # data = {
        #     'category': 'Transportation',
        #     'amount': 2000.0,
        #     'description': 'Test the bot tyt your Transportation',
        #     'is_all_trans_bud': False,
        # }
        # for i in range(len(endpoint)):
        post_request(
            url='https://track-finance.onrender.com/add_transactions/',
            # url='http://127.0.0.1:8000/add_transactions/',
            session_object=session,
            payload=data_payload

        )

    else:
        print("Login failed. Please check your credentials.")
