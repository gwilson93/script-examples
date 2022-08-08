import os
import requests
import json
import csv
from ratelimit import limits, sleep_and_retry
from datetime import datetime, timezone, timedelta, date


# Load Environment variables
from dotenv import load_dotenv
load_dotenv()
api_token = os.getenv('API_TOKEN')
org_id = os.getenv('ORG_ID')


#Return all users in org with rate limiting handling
@sleep_and_retry
@limits(calls=200, period=60)
def retrieve_org_members():
    final_data=[]
    url = f'https://api.miro.com/v2/orgs/{org_id}/members'
    headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {api_token}"
    } 
    response = requests.get(url, headers=headers)  
    data = response.json()
    final_data = data['data']

    # Pagination
    while data['data']:
        cursor = data['data'][-1]['id']
        url = f'https://api.miro.com/v2/orgs/{org_id}/members?cursor={cursor}'
        response = requests.get(url,headers=headers)
        if response.status_code !=200:
            raise Exception ('API response: {}'.format(response.status_code))
        data = response.json()
        final_data = final_data + data['data']
    return final_data


#Create CSV from data returned in API requests
def generate_csv(final_data,file_name):
    print(final_data)
    exportdata = []
    csvheader = ['Active', 'User Email', 'User ID', 'Last Activity', 'License', 'License Assigned At', 'Role']
    for x in final_data:
            listing = []
            if 'active' in x:
                listing.append(x['active'])
            else:
                listing.append('')
            if 'email' in x:
                listing.append(x['email'])
            else:
                listing.append('')
            if 'id' in x:
                listing.append(x['id'])
            else:
                listing.append('')
            if 'lastActivityAt' in x:
                listing.append(x['lastActivityAt'])
            else:
                listing.append('')
            if 'license' in x:
                listing.append(x['license'])
            else:
                listing.append('')
            if 'licenseAssignedAt' in x:
                listing.append(x['licenseAssignedAt'])
            else:
                listing.append('')
            if 'role' in x:
                listing.append(x['role'])
            else:
                listing.append('')
            exportdata.append(listing)


    with open(file_name, 'w', encoding='UTF8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(csvheader)
        writer.writerows(exportdata)
    
    print('Done!')


#Filter data helper function
def data_filter(data,days):
    today_date = datetime.now(timezone.utc)
    filtered_data = []
    for x in data:
        if x.get('lastActivityAt'):
            if datetime.fromisoformat(x.get('lastActivityAt').replace("Z", "+00:00")) >= today_date - timedelta(days=days):
                filtered_data.append(x)
    return filtered_data


#Retrieve all users in enterprise account
def generate_all_users():
    fname = file_name()
    print('Retrieving Users from Account...')
    data = retrieve_org_members()
    print('Generating CSV File...')
    generate_csv(data,fname)


#Retrieve subset of users based specified last activity date
def generate_subset_users():
    fname = file_name()
    days = activity_date()
    print('Retrieving Users from Account...')
    data = retrieve_org_members()
    print('Generating CSV File...')
    filtered_data = data_filter(data,days)
    generate_csv(filtered_data,fname)



menu_options = {
    1: 'Generate Report of All Active/Deactivated Users',
    2: 'Generate Report of All Users Active in a Specified Timeframe',
    3: 'Exit',
}

#Menu Generation
def print_menu():
    print()
    for key in menu_options.keys():
        print (key, '--', menu_options[key] )


#Creating file name and appending csv file type
def file_name():
    print()
    fname = input('Please specify a name for your file: ') + '.csv'
    return fname


#Get activity date and check for positive integer value
def activity_date():
    while(True):
        try:
            # read input and try and covert to integer
            n = int(input('This report will retrieve the users who were active in a specified amount of days. Enter the number of days you would like to look back at: '))

            # if we get here we got an int but it may be negative
            if n < 0:
                raise ValueError
        
            # if we get here we have a non-negative integer so exit loop
            break
        # catch any error thrown by int()
        except ValueError:
            print('Entered value was not a postive whole number')
    return n        


#Main Function
if __name__=='__main__':
    while(True):
        print_menu()
        option = ''
        try:
            option = int(input('Enter your choice: '))
        except:
            print('Wrong input. Please enter a number ...')
        #Check what choice was entered and act accordingly
        if option == 1:
            generate_all_users()
        elif option == 2:
            generate_subset_users()
        elif option == 3:
            print('Exiting script!')
            exit()
        else:
            print('Invalid option. Please enter a number between 1 and 3.')