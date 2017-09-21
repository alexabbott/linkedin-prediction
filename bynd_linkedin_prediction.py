from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import csv
import numpy
from sklearn import tree

# this is a basic prediction to determine the number of LinkedIn connections for an employee
# based on their gender, department and location

features = []
labels = []

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Test'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """Shows basic usage of the Sheets API.

    Creates a Sheets API service object and prints the names and majors of
    students in a sample spreadsheet:
    https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    spreadsheetId = '1o1brUpoRGjTOJCGEGAqoBA1KbC33gSLSqmNJu5ca18s'
    rangeName = 'FormattedData!A1:D'
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        print('Data:')
        for row in values:
            # Push data into features and labels arrays
            features.append([row[0], row[1], row[2]])
            labels.append(row[3])

    # clf is a box of rules using a decision tree as the rules
    clf = tree.DecisionTreeClassifier()

    # fit is an algorithm that finds patterns in data
    clf.fit(features, labels)

    # ask user for input
    gender = raw_input('''
                    Enter:
                    0 for female
                    1 for male
                    ''')

    department = raw_input('''
                    Enter:
                    0 for Client Strategist
                    1 for Content
                    2 for Dev
                    3 for GM
                    4 for I&A
                    5 for Operations
                    6 for PM
                    7 for Product
                    8 for Strategy
                    9 for UX/Designer
                    ''')

    location = raw_input('''
                    Enter:
                    0 for Austin
                    1 for London
                    2 for Mountain View
                    3 for New York
                    4 for San Francisco
                    ''')

    # Predict the number of LinkedIn Connections
    prediction = clf.predict([[int(gender), int(department), int(location)]])[0]

    if prediction == '500':
        prediction = '500+'

    print ('The predicted number of LinkedIn connections is %s' % (prediction))

if __name__ == '__main__':
    main()
