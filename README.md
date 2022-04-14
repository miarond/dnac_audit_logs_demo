# DNAC Audit Logs Demo Script

The purpose of this project is to demonstrate the use of DNA Center APIs to obtain data (in this case, audit logs) and output it to local files in either CSV or JSON format.  This script is written for demonstration purposes and has not been extensively tested - USE AT YOUR OWN RISK.  This scipt is provided as-is with no warranty and no support.

## Cloning The Repository

If you have `git` installed on your system, you can Clone this project's repository directly to your system from GitHub with a single command line command: `git clone <url_to_repository>.git`.  This command will create a directory inside the current directory you are in, then clone a version of the repository into this new directory.  You can then change into this new project directory and you will see a copy of all files included in the repository.

## Setup

1. Copy the `default.env` file and rename it to `.env`, then edit the file to add your login information and environment details.
2. Create a Python Virtual Environment to isolate the project and its depenencies from the rest of your system:
    1. Run the command `python3 -m venv myvenv` on Linux or MacOS systems, or `python.exe -m venv myvenv` on Windows systems.
3. Activate the Virtual Environment:
    1. Run the command `source myvenv/bin/activate` on Linux or MacOS systems, `myvenv\Scripts\Activate.ps1` for Windows PowerShell, or `myvenv\Scripts\activate.bat` for Windows CMD.
4. Use Python's PIP module to install the required dependency packages (those that are not already built into Python):
    1. Run the command `pip install -r requirements.txt`, or `pip3 install -r requirements.txt` (depending on whether you have multiple versions installed on your system).
    2. To verify that the packages were installed, you can run the command `pip freeze -l` or `pip3 freeze -l` to view a list of only those packages installed in your local virtual environment.

## Usage

The Python script `main.py` contains all of the code necessary for this project.  The script accepts several command line arguments to set various options, and you can view the available options along with their help information by issuing the command: `python3 main.py --help`.  Below is a table explaining all of the available command line arguments:


| **Argument** | **Values** | **Default Value** | **Description** |
| :--- | :--- | :--- | :--- |
| `--sdk` | N/A | False | Tells the `main.py` script to use the DNACenterSDK package for communication with DNA Center, instead of the Requests package. No argument value is needed, simply selecting the argument stores a "True" value. |
| `-h`</br>`--help` | N/A | N/A | Displays the help message with details about all CLI arguments. |
| `-c`</br>`--category` | INFO, WARN, ERROR, ALERT, TASK_PROGRESS, TASK_FAILURE, TASK_COMPLETE, COMMAND, QUERY, CONVERSATION | INFO | Selects the category of Audit Logs you want to export. |
| `--sev` | 1, 2, 3, 4, 5 | 1 | Selects the Severity Level of Audit Logs you want to export. |
| `-s`</br>`--start` | ISO-8601 formatted Date/Time strings | `2017-01-01T00:00:00+00:00` | The Start Time for the Audit Log search, expressed in an ISO-8601 date/time format (YYYY-MM-DDThh:mm:ssTZD, Ex: 1997-07-16T19:20:30+01:00).  Information on this format can be found [here](https://www.w3.org/TR/NOTE-datetime).  The script will attempt to convert this string to "Epoch Time" format, which is the number of milliseconds from January 1st, 1970, in UTC. |
| `-e`</br>`--end` | ISO-8601 formatted Date/Time strings | `2022-04-01T00:00:00+00:00` | The End Time for the Audit Log search, expressed in the same format as Start Time. |
| `-o`</br>`--output` | csv, json, object | csv | The output format of the export text file.  If `object` is chosen, no file is written to disk and the output is returned as a Python JSON object (NOTE, this will only work when this script is imported into another Python script and the `get_audit_logs` function is called directly.) |
| `-f`</br>`--filename` | Any string | `output.csv` | The filename used for saving the output file to disk.  This MUST be a string value. |

 > **NOTE:** If no command line options are given, the script will default to using the Cisco DevNet Always-on DNA Center Sandbox.  Access to this sandbox may change at any time and as such, the script may fail in the future if no arguments are given at runtime.

## API Documentation

This Python script demonstrates two separate ways of interacting with the DNA Center APIs programmatically.  One method utilizes the well-known `requests` package, which is a generic HTTP client that is user friendly; the other method utilizes Cisco's `dnacentersdk` Python package, which provides a very low-code way to begin using DNA Center APIs.

Documentation for the DNA Center APIs can be found here:
  - https://developer.cisco.com/docs/dna-center

Documentation for the `requests` package can be found here:
  - https://docs.python-requests.org/en/latest/

Documentation for the `dnacentersdk` package can be found here:
  - https://dnacentersdk.readthedocs.io/en/latest
