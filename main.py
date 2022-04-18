"""
Copyright (c) 2022 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.

"""

__author__ = "Aron Donaldson <ardonald@cisco.com>"
__contributors__ = ""
__copyright__ = "Copyright (c) 2022 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

# Python built-in modules
import json
import csv
import argparse
import os
import sys

# PyPi imported modules
import dateutil.parser as dp
import urllib3
import requests
from dnacentersdk import DNACenterAPI, ApiError
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Disable certificate warnings - useful if using self-signed certificate
urllib3.disable_warnings()

# Load environment variables from the .env file
try:
    load_dotenv()
    if os.getenv("DNAC_USERNAME") == '':
        username = 'devnetuser'
    else:
        username = os.getenv("DNAC_USERNAME")

    if os.getenv("DNAC_PASSWORD") == '':
        password = 'Cisco123!'
    else:
        password = os.getenv("DNAC_PASSWORD")
    
    if os.getenv("DNAC_SERVER") == '':
        dnac_server = 'https://sandboxdnac.cisco.com:443'
    else:
        dnac_server = os.getenv("DNAC_SERVER")
    
    if os.getenv("DNAC_DATA_BASE_URL") == '':
        data_base_url = '/dna/data/api/v1'
    else:
        data_base_url = os.getenv("DNAC_DATA_BASE_URL")
except Exception as e:
    sys.stderr.write(f'Error encountered loading .env file:\n{e}\n')
    sys.exit(1)

def parse_arguments():
    # Parse any incoming command line arguments
    parser = argparse.ArgumentParser(description='This script returns audit log data from DNA Center, filtered '
                                    'by any command line argument options.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--sdk', help='Use the DNACenterSDK instead of the Requests module.', dest='sdk', action='store_true',
                         default=False)
    parameters = parser.add_argument_group('Audit Log Parameters')
    parameters.add_argument('-c', '--category', type=str, help='Set category; available options are: '
                            'INFO, WARN, ERROR, ALERT, TASK_PROGRESS, TASK_FAILURE, TASK_COMPLETE, COMMAND, QUERY, CONVERSATION',
                                dest='category', default='INFO')
    parameters.add_argument('--sev', type=int, help='Set audit log severity level; available options are: 1, 2, 3, 4, 5.',
                            dest='severity', default=1)
    parameters.add_argument('-s', '--start', type=str, help='Start time for audit log search. Expressed in ISO-8601 format: '
                                'https://www.w3.org/TR/NOTE-datetime  Ex.: YYYY-MM-DDThh:mm:ssTZD (eg. 1997-07-16T19:20:30+01:00)',
                                    dest='start', default='2017-01-01T00:00:00+00:00')
    parameters.add_argument('-e', '--endtime', type=str, help='End time for audit log search. Expressed in ISO-8601 format: '
                                'https://www.w3.org/TR/NOTE-datetime  Ex.: YYYY-MM-DDThh:mm:ssTZD (eg. 1997-07-16T19:20:30+01:00)',
                                    dest='end', default='2022-04-01T00:00:00+00:00')

    output = parser.add_argument_group('Output type.')
    output.add_argument('-o', '--output', type=str, help='Output results to a file; available options are: csv, json, object. '
                            'Object output will return the data in JSON format as a Python object, which can be passed to another program.', 
                                dest='output', default='csv')
    output.add_argument('-f', '--filename', type=str, help='Output filename.', dest='filename', default='output.csv')

    return parser.parse_args()


def dnac_auth():
    # Authenticate to DNA Center appliance, obtain JWT

    auth = HTTPBasicAuth(username, password)
    # Account for older auth token URL in DNAC Sandbox lab
    # if dnac_server == 'https://sandboxdnac.cisco.com:443':
    url = f"{dnac_server}/api/system/v1/auth/token"
    # else:
    #     url = f"{dnac_server}/dna/system/api/v1/auth/token"

    # Verify certificate validity is disabled, in case of self-signed certificates
    response = requests.post(url, auth=auth, verify=False)

    if response.status_code == 200:
        global token; token = response.json()['Token']
        return token
    else:
        # If auth fails for any reason, write error message to STDERR and exit script with error status code 1
        sys.stderr.write(f'Authentication to DNA Center failed.\n{response.text}\n')
        sys.exit(1)
    

def sdk_auth():
    # Authenticate to DNA Center using the SDK
    try:
        dnac_session = DNACenterAPI(username=username, password=password, base_url=dnac_server, verify=False)
    except ApiError as e:
        sys.stderr.write(f'Authentication to DNA Center using SDK failed.\n{e}\n')
        sys.exit(1)
    # Storing token in global variable for consistency; it is stored inside the "api" object when using the SDK
    global token; token = dnac_session.access_token
    return dnac_session


def get_epoch(input):
    # Convert input date/time to epoch time
    try:
        input = str(input)
    except TypeError as e:
        sys.stderr.write(f'Failed to convert date/time input to string:\n{e}\n')
        sys.exit(1)
    
    try:
        epoch_time = int(dp.parse(input).timestamp())
        # Add millisencond precision if input is in seconds
        if len(str(epoch_time)) == 10:
            epoch_time = epoch_time * 1000
    except Exception as e:
        sys.stderr.write(f'Failed to convert date/time input to epoch time:\n{e}\n')
        sys.exit(1)
    return epoch_time


def to_csv(logs, args):
    # Convert JSON logs to CSV format
    # Get field names from the keys of the first Dictionary in the logs output list
    fields = list(logs[0].keys())
    with open(args.filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(fields)
        # Found that some values contain "\n" characters, which cause a newline break when writing to CSV
        # This method is much slower but is necessary to escape any special characters in each value
        # Also, if the length of a value is greater than 32,767, Excel will wrap it to a new row
        for log in logs:
            row = []
            for item in log.values():
                if len(str(item)) > 32767:
                    print('WARNING!!\nCell length exceeds maximum supported in Excel.\nYou may find cells split across multiple rows.\n')
                row.append(repr(item))
            writer.writerow(row)
        f.close()
    file_path = os.path.realpath(args.filename)
    print(f'CSV file is located at:\n{file_path}\n')
    return file_path


def to_json(logs, args):
    # Write JSON output of logs to a text file
    # Attempt to format JSON with indentation and whitespace
    try:
        output = json.dumps(logs, indent=4)
    except Exception as e:
        sys.stderr.write(f'Failed to serialize audit log output as JSON:\n{e}\n')
        output = logs
    
    # If no filename is specified, default is output.csv. Here we remove the .csv and replace it with .json
    if args.filename == 'output.csv':
        args.filename = args.filename.split(".")[0] + ".json"
    with open(args.filename, 'w', newline='') as f:
        f.write(output)
        f.close()
    file_path = os.path.realpath(args.filename)
    print(f'JSON file is located at:\n{file_path}\n')
    return file_path


def sdk_get_audit_logs(args, dnac_session):
    # Obtain any audit log results from DNA Center
    start = get_epoch(args.start)
    end = get_epoch(args.end)

    try:
        logs = dnac_session.event_management.get_auditlog_records(category=args.category, severity=str(args.severity), start_time=start, end_time=end)
    except ApiError as e:
        sys.stderr.write(f'An error occurred while obtaining Audit Logs from DNAC via the SDK:\n{e}\n')
        sys.exit(1)
    print(f'There are a total count of {len(logs)} records returned by your query.\n')
    if len(logs) > 0:
        if args.output == 'csv':
            return to_csv(logs, args)
        elif args.output == 'json':
            return to_json(logs, args)
        elif args.output == 'terminal':
            print(json.dumps(logs, indent=4))
        else:
            return json.loads(logs)
    else:
        return logs


def get_audit_logs(args, token):
    # Obtain any audit log results from DNA Center
    start_time = get_epoch(args.start)
    end_time = get_epoch(args.end)

    logs_url = f'{dnac_server}{data_base_url}/event/event-series/audit-logs'
    header = {
        'Content-Type': 'application/json',
        'x-auth-token': token
    }
    query_params = {
        'category': args.category.upper(),
        'severity': str(args.severity),
        'startTime': start_time,
        'endTime': end_time
    }

    logs = requests.get(logs_url, params=query_params, headers=header, verify=False)
    if logs.status_code == 200:
        print(f'There are a total count of {len(logs.json())} records returned by your query.\n')
        if len(logs.json()) > 0:
            if args.output == 'csv':
                return to_csv(logs.json(), args)
            elif args.output == 'json':
                return to_json(logs.json(), args)
            elif args.output == 'terminal':
                print(json.dumps(logs.json(), indent=4))
            else:
                return logs.json()
    else:
        return logs.text


if __name__ == '__main__':
    args = parse_arguments()
    if args.sdk is True:
        result = sdk_get_audit_logs(args, sdk_auth())
    else:
        token = dnac_auth()
        result = get_audit_logs(args, token)
