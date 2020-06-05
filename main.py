""" >>>>>>>>>> IMPORTANT <<<<<<<<<<

You will need to create a Sumo Logic access key to use this script.
Follow the guide here: https://help.sumologic.com/Manage/Security/Access-Keys#manage-your-access-keys-on-preferences-page

"""

import requests

# Calculating epoch time
import time

# Secure ways to get credentials
import sys, getpass

# Encode the credentials
from base64 import b64encode

# URL encoding
import urllib.parse

# Pretty print
import pprint

# Handling different file/content types
import csv
import json

# Import modules used for handling exit actions.
import atexit, signal

# These lines allow us to interactively ask for the access_id and access_key if this script
# is run interactively. Alternatively, we will read in additional input from the CLI.
# https://pymotw.com/2/getpass/
if sys.stdin.isatty():
    print('Enter SumoLogic credentials')
    access_id = input('access_id: ')
    access_key = getpass.getpass('access_key: ')
else:
    access_id = sys.stdin.readline().rstrip()
    access_key = sys.stdin.readline().rstrip()

assert access_id is not None and access_key is not None, "You must supply both access_id and access_key!"

base_url = 'https://api.au.sumologic.com/api'

def execute_api(request_url, request_type, additional_headers={}, request_data=None):
    """Basic function to remove this snippet of code out of every other function.

    Args:
        request_url: string, the target API URL.
        request_type: string, what type of request is being made (ie - GET, POST, DELETE).
        additional_headers: dict, any extra headers to add to the base auth headers.
        request_data: string, any data that needs to be sent, usually only required for POST.
    """

    # Construct the auth header for regular API queries
    request_headers = {
        'Authorization': 'Basic '+b64encode(bytes(access_id+':'+access_key,'utf-8')).decode('utf-8')
    }
    # If any API calls require additional headers, add them here.
    request_headers.update(additional_headers)

    # There are a specific set of request types that can be executed.
    valid_types = {'GET', 'OPTIONS', 'HEAD', 'POST', 'PUT', 'PATCH', 'DELETE'}
    if request_type not in valid_types:
        raise ValueError('execute_api: request_type must be one of {0}.'.format(valid_types))    

    # Execute the request, and return the JSON payload.
    return requests.request(request_type, request_url, headers=request_headers, data=json.dumps(request_data))


def generate_arg_string(arguments):
    arg_array = []
    for key, value in arguments.items():
        arg_array.append(key+'='+str(value))
    arg_string = '&'.join(filter(None, arg_array))
    return arg_string



### ============================================================
### COLLECTOR MANAGEMENT API
### https://help.sumologic.com/APIs/01Collector-Management-API

### ========================================
### Collector API Methods
### https://help.sumologic.com/APIs/01Collector-Management-API/Collector-API-Methods-and-Examples

### ====================
### GET methods
### https://help.sumologic.com/APIs/01Collector-Management-API/Collector-API-Methods-and-Examples#get-methods

""" List Collectors  
Get a list of Collectors with an optional limit and offset.

Method: GET
Path: /collectors
https://help.sumologic.com/APIs/01Collector-Management-API/Collector-API-Methods-and-Examples#list-collectors

Example: list_collectors()
"""
def list_collectors():
    request_url = base_url+'/v1/collectors'
    return execute_api(
        request_url = request_url,
        request_type = 'GET'
    )


""" List Offline Collectors
Get a list of Installed Collectors last seen alive before a specified number of days with an optional limit and offset.

Method: GET
Path: /collectors/offline
https://help.sumologic.com/APIs/01Collector-Management-API/Collector-API-Methods-and-Examples#list-offline-collectors

Parameter:	    aliveBeforeDays
Type:	        Integer
Required:       No
Default:        100
Description:	Minimum number of days the Collectors have been offline. Must be at least 1 day.

Parameter:	    limit
Type:	        Integer
Required:	    No
Default:	    1000
Description:	Max number of Collectors to return.

Parameter:      offset
Type:	        Integer
Required:	    No
Default:	    0
Description:	Offset into the list of Collectors.

Example:
arguments = {
    'aliveBeforeDays': 100,
    'limit': 1000,
    'offset': 0
}
list_offline_collectors(arguments)
"""
def list_offline_collectors(arguments=None):
    request_url = base_url+'/v1/collectors/offline'
    if arguments:
        request_url += '?'+generate_arg_string(arguments)
    return execute_api(
        request_url = request_url,
        request_type = 'GET'
    )


""" Get Collector by ID 
Get the Collector with the specified Identifier.

Method: GET
Path: /collectors/[collectorId]
https://help.sumologic.com/APIs/01Collector-Management-API/Collector-API-Methods-and-Examples#get-collector%C2%A0by-id

Parameter:	    collectorId
Type:	        Integer
Required:       Yes
Default:        NA
Description:	Unique Collector identifier.

Example:        get_collector_by_id([collectorId])
"""
def get_collector_by_id(collector_id):
    request_url = base_url+'/v1/collectors/'+str(collector_id)
    return execute_api(
        request_url = request_url,
        request_type = 'GET'
    )


""" Get Collector by Name 
Get the Collector with the specified Name.

Method: GET
Path: /collectors/name/[name]
https://help.sumologic.com/APIs/01Collector-Management-API/Collector-API-Methods-and-Examples#get-collector%C2%A0by-name

Parameter:	    collectorName
Type:	        String
Required:       Yes
Default:        NA
Description:	Name of the Collector.

Example:        get_collector_by_name([collectorName])
 """
def get_collector_by_name(collector_name):
    # Names with special characters are not supported, such as ; / % \ even if they are URL encoded.
    special_characters = [';','/','%','\\']
    if any(special_char in collector_name for special_char in special_characters):
        raise ValueError('get_collector_by_name: collector_name must not contain any of these characters {0}.'.format(special_characters))

    request_url = base_url+'/v1/collectors/name/'+urllib.parse.quote(collector_name)

    # Names with a period . need to have a trailing forward slash / at the end of the request URL.
    if '.' in collector_name:
        request_url += '/'

    return execute_api(
        request_url = request_url,
        request_type = 'GET'
    )


### ====================
### POST methods
### https://help.sumologic.com/APIs/01Collector-Management-API/Collector-API-Methods-and-Examples#post-methods

""" Create Hosted Collector
Use the POST method with a JSON file to create a new Hosted Collector. The required parameters can be referenced in the Response fields table above. Note that "id" field should be omitted when creating a new Hosted Collector.
Important: This method can only be used to create Hosted Collectors. You must install a Collector manually to create an Installed Collector.

Method: POST
Path: /collectors
https://help.sumologic.com/APIs/01Collector-Management-API/Collector-API-Methods-and-Examples#create-hosted-collector

Example:
collector_json = {
    "collector":{
        "collectorType":"Hosted",
        "name":"My Hosted Collector",
        "description":"An example Hosted Collector",
        "category":"HTTP Collection",
        "fields": {
            "_budget":"test_budget"
        }
    }
}
create_hosted_collector(collector_json)
"""
def create_hosted_collector(collector_json):
    request_url = base_url + '/v1/collectors'
    additional_headers = {
        'Content-Type': 'application/json'
    }
    return execute_api(
        request_url = request_url,
        request_type = 'POST',
        additional_headers = additional_headers,
        request_data = collector_json
    )


### ====================
### PUT methods
### https://help.sumologic.com/APIs/01Collector-Management-API/Collector-API-Methods-and-Examples#put-methods

""" Update a Collector 
Use the PUT method with your JSON file to update an existing Collector. Available parameters can be referenced in the Response fields table above. The JSON request file must specify values for all required fields. Not modifiable fields must match their current values in the system. This is in accordance with HTTP 1.1 RFC-2616 Section 9.6. 

Updating a Collector also requires the "If-Match" header to be specified with the "ETag" provided in the headers of a previous GET request.

Method: PUT
Path: /collectors/[collectorId]
https://help.sumologic.com/APIs/01Collector-Management-API/Collector-API-Methods-and-Examples#update%C2%A0a-collector

Parameter:	    collectorId
Type:	        Integer
Required:       Yes
Default:        NA
Description:	Unique Collector identifier.

Example:
fields_json = {
    'targetCpu': [Long]
}
get_source_by_id([collectorId], fields_json)
"""
def update_collector(collector_id, fields_json):
    collector = get_collector_by_id(collector_id)

    collector_mod = collector.json()
    collector_mod['collector'].update(fields_json)

    request_url = base_url + '/v1/collectors/' + str(collector_id)
    additional_headers = {
        'Content-Type': 'application/json',
        'If-Match': collector.headers['ETag']
    }
    return execute_api(
        request_url = request_url,
        request_type = 'PUT',
        additional_headers = additional_headers,
        request_data = collector_mod
    )


### ====================
### DELETE methods
### https://help.sumologic.com/APIs/01Collector-Management-API/Collector-API-Methods-and-Examples#delete-methods

""" Delete Collector by ID
Use the DELETE method to delete an existing Collector.

Method: DELETE
Path: /collectors/[collectorId]
https://help.sumologic.com/APIs/01Collector-Management-API/Collector-API-Methods-and-Examples#delete%C2%A0collector-by-id

Parameter:	    collectorId
Type:	        Integer
Required:       Yes
Default:        NA
Description:	Unique Collector identifier.

Example:        get_source_by_id([collectorId])
"""
def delete_collector_by_id(collector_id):
    request_url = base_url+'/v1/collectors/'+str(collector_id)
    return execute_api(
        request_url = request_url,
        request_type = 'DELETE'
    )


""" Delete Offline Collectors
Delete Installed Collectors last seen alive before a specified number of days.

Method: DELETE
Path: /collectors/offline
https://help.sumologic.com/APIs/01Collector-Management-API/Collector-API-Methods-and-Examples#delete-offline-collectors

Parameter:	    aliveBeforeDays
Type:	        Integer
Required:       No
Default:        100
Description:	Minimum number of days the Collectors have been offline. Must be at least 1 day.

Example:
arguments = {
    'aliveBeforeDays': 100
}
get_source_by_id(arguments)
"""
def delete_offline_collectors(arguments=None):
    request_url = base_url+'/v1/collectors/offline'
    if arguments:
        request_url += '?'+generate_arg_string(arguments)
    return execute_api(
        request_url = request_url,
        request_type = 'DELETE'
    )



### ========================================
### Source API Methods
### https://help.sumologic.com/APIs/01Collector-Management-API/Source-API

### ====================
### GET methods
### https://help.sumologic.com/APIs/01Collector-Management-API/Source-API#get-methods

""" List Sources
Gets information about all Sources for a specified Collector.

Method: GET
Path: /collectors/[collectorId]/sources
https://help.sumologic.com/APIs/01Collector-Management-API/Source-API#list%C2%A0sources

Parameter:	    collectorId
Type:	        Integer
Required:       Yes
Default:        NA
Description:	Unique Collector identifier.

Parameter:	    download
Type:	        Boolean
Required:       No
Default:        false
Description:	When set to true, the response will be a JSON array of Sources that can be used to register a new Collector.

Example:
arguments = {
    'download': true
}
get_source_by_id([collectorId], arguments)
"""
def list_sources(collector_id, arguments=None):
    request_url = base_url+'/v1/collectors/'+str(collector_id)+'/sources'
    if arguments:
        request_url += '?'+generate_arg_string(arguments)
    return execute_api(
        request_url = request_url,
        request_type = 'GET'
    )


""" Get Source by ID
Gets information about a specified Collector and Source.

Method: GET
Path: /collectors/[collectorId]/sources/[sourceId]
https://help.sumologic.com/APIs/01Collector-Management-API/Source-API#get%C2%A0source-by-id

Parameter:	    collectorId
Type:	        Integer
Required:       Yes
Default:        NA
Description:	Unique Collector identifier.

Parameter:	    sourceId
Type:	        Integer
Required:       Yes
Default:        NA
Description:	Unique Source identifier.

Parameter:	    download
Type:	        Boolean
Required:       No
Default:        false
Description:	When set to true, the response will be a JSON array of Sources that can be used to register a new Collector.

Example:
arguments = {
    'download': [Boolean]
}
get_source_by_id([collectorId], [sourceId], arguments)
"""
def get_source_by_id(collector_id, source_id, arguments=None):
    request_url = base_url+'/v1/collectors/'+str(collector_id)+'/sources/'+str(source_id)
    if arguments:
        request_url += '?'+generate_arg_string(arguments)
    return execute_api(
        request_url = request_url,
        request_type = 'GET'
    )


### ====================
### POST methods
### https://help.sumologic.com/APIs/01Collector-Management-API/Source-API#post-methods

""" Create Source
Creates a new Source for a Collector. See Use JSON to Configure Sources for required fields for the request JSON file.

Method: POST
Path: /collectors/[collectorId]/sources
https://help.sumologic.com/APIs/01Collector-Management-API/Source-API#create-source

Parameter:	    collectorId
Type:	        Integer
Required:       Yes
Default:        NA
Description:	Unique Collector identifier.

Example:
source_json = {
    "source":{
        "sourceType":"SystemStats",
        "name":"Host_Metrics",
        "interval":60000,
        "hostName":"my_host",
        "metrics":[
            "CPU_User",
            "CPU_Sys"
        ]
    }
}
create_source([collectorId], source_json)
"""
def create_source(collector_id, source_json):
    request_url = base_url+'/v1/collectors/'+str(collector_id)+'/sources'
    additional_headers = {
        'Content-Type': 'application/json'
    }
    return execute_api(
        request_url = request_url,
        request_type = 'POST',
        additional_headers = additional_headers,
        request_data = source_json
    )


### ====================
### PUT methods
### https://help.sumologic.com/APIs/01Collector-Management-API/Source-API#put-methods

""" Update Source
Updates an existing source. All modifiable fields must be provided, and all not modifiable fields must match those existing in the system.

Updating a Source also requires the "If-Match" header to be specified with the "ETag" provided in the headers of a previous GET request.

Method: PUT
Path: /collectors/[collectorId]/sources/[sourceId]

Parameter:	    collectorId
Type:	        Integer
Required:       Yes
Default:        NA
Description:	Unique Collector identifier.

Parameter:	    sourceId
Type:	        Integer
Required:       Yes
Default:        NA
Description:	Unique Source identifier.

Example:
fields_json = {
	"source": {
		"id": 101833059,
		"name": "Host_Metrics",
		"hostName": "my_host",
		"automaticDateParsing": true,
		"multilineProcessingEnabled": true,
		"useAutolineMatching": true,
		"contentType": "HostMetrics",
		"forceTimeZone": false,
		"filters": [
			{
				"filterType": "Exclude",
				"name": "Filter keyword",
				"regexp": "(?s).*EventCode = (?:700|701).*Logfile = \"Directory Service\".*(?s)"
			}
		],
		"cutoffTimestamp": 0,
		"encoding": "UTF-8",
		"interval": 15000,
		"metrics": [
			"CPU_User",
			"CPU_Sys"
		],
		"sourceType": "SystemStats",
		"alive": true
	}
}
update_source([collectorId], [sourceId], fields_json)
"""
def update_source(collector_id, source_id, fields_json):
    source = get_source_by_id(collector_id, source_id)

    source_mod = source.json()
    source_mod['source'].update(fields_json)

    request_url = base_url+'/v1/collectors/'+str(collector_id)+'/sources/'+str(source_id)
    additional_headers = {
        'Content-Type': 'application/json',
        'If-Match': source.headers['ETag']
    }
    return execute_api(
        request_url = request_url,
        request_type = 'PUT',
        additional_headers = additional_headers,
        request_data = source_mod
    )


### ====================
### DELETE methods
### https://help.sumologic.com/APIs/01Collector-Management-API/Source-API#delete-methods

""" Delete Source
Deletes the specified Source from the specified Collector.

Method: DELETE
Path: /collectors/[collectorId]/sources/[sourceId]

Parameter:	    collectorId
Type:	        Integer
Required:       Yes
Default:        NA
Description:	Unique Collector identifier.

Parameter:	    sourceId
Type:	        Integer
Required:       Yes
Default:        NA
Description:	Unique Source identifier.

Example:
delete_source([collectorId], [sourceId])
"""
def delete_source(collector_id, source_id):
    request_url = base_url + '/v1/collectors/' + str(collector_id) + '/sources/' + str(source_id)
    return execute_api(
        request_url = request_url,
        request_type = 'DELETE'
    )



### ========================================
### Upgrade or Downgrade Collectors Using the API
### https://help.sumologic.com/APIs/01Collector-Management-API/Upgrade-or-Downgrade-Collectors-Using-the-API

""" Get upgradable Collectors
Sends a request to get Collectors you can upgrade.

Method: GET 
Path: collectors/upgrades/collectors
https://help.sumologic.com/APIs/01Collector-Management-API/Upgrade-or-Downgrade-Collectors-Using-the-API#get-upgradable-collectors
"""
def get_upgradable_collectors(arguments):
    pass


""" Get available builds

Method: GET 
Path: /collectors/upgrades/targets
https://help.sumologic.com/APIs/01Collector-Management-API/Upgrade-or-Downgrade-Collectors-Using-the-API#get-available-builds
"""
def get_available_builds():
    pass


""" Create an upgrade or downgrade task

Method: POST 
Path: /collectors/upgrades
https://help.sumologic.com/APIs/01Collector-Management-API/Upgrade-or-Downgrade-Collectors-Using-the-API#create-an-upgrade-or-downgrade-task
"""
def create_an_upgrade_or_downgrade_task():
    pass


""" Get upgrade task status
After obtaining the upgrade job ID, you can obtain the status of the upgrade task from the status endpoint.

Method: GET 
Path: /collectors/upgrades/[upgradeTaskID]
https://help.sumologic.com/APIs/01Collector-Management-API/Upgrade-or-Downgrade-Collectors-Using-the-API#get-upgrade-task-status
"""
def get_upgrade_task_status():
    pass



### ========================================
### Custom Methods

def delete_all_sources(collector_id):
    sources = list_sources(collector_id,{})
    for source in sources.json()['sources']:
        delete_source(collector_id, source['id'])


def set_all_collectors_cpu_limit():
    new_cpu = {
        'targetCpu': 20
    }
    for collector in list_collectors().json()['collectors']:
        if collector['collectorType'] == 'Installable':
            print('Setting targetCpu on [{0}]'.format(collector['name']))
            update_collector(collector['id'],new_cpu)


def source_update():
    # EXAMPLE
    # source_replacement = {
    #     'collector-name-0':'.\\.sources\\new-source-file-0.json',
    #     'collector-name-1':'.\\.sources\\new-source-file-1.json',
    #     'collector-name-2':'.\\.sources\\new-source-file-2.json',
    # }
    source_replacement = {
    }

    for collector in list_collectors().json()['collectors']:
        if collector['name'] in source_replacement.keys():
            print('Processing [{0}]'.format(collector['name']))

            # Delete ALL sources from this collector.
            print('\tDeleting all sources...')
            delete_all_sources(collector['id'])

            # Construct the JSON file.
            print('\tCreating new sources...')

            # The cutoff data is 30 days before today in epoch time.
            # 30days * 24hrs * 60min * 60sec * 1,000ms = 2,592,000,000ms
            new_cutoff = (int(time.time())*1000)-2592000000
            with open(source_replacement[collector['name']]) as json_file:
                data = json.load(json_file)
                for source in data['sources']:
                    temp_name = collector['name'].split('-')
                    temp_cat = source['category'].split('/')
                    temp_cat[0] = temp_name[0]+'-'+temp_name[1]
                    temp_cat[1] = temp_name[2]
                    temp_cat[2] = temp_name[3]
                    print('\t\t{0}::{1}'.format('/'.join(temp_cat),new_cutoff))

                    source['category'] = '/'.join(temp_cat)
                    source['cutoffTimestamp'] = new_cutoff
                    source = {
                        'source': source
                    }

                    create_source(collector['id'],source)


def collector_name_update():
    # EXAMPLE
    # collector_name_replacement = {
    #     'old-collector-name-0':'new-collector-name-0',
    #     'old-collector-name-1':'new-collector-name-1',
    #     'old-collector-name-2':'new-collector-name-2',
    # }
    collector_name_replacement = {
    }

    for collector in list_collectors().json()['collectors']:
        if collector['name'] in collector_name_replacement.keys():
            print('Processing [{0}]'.format(collector['name']))
            fields_json = {
                'name': collector_name_replacement[collector['name']]
            }
            update_collector(collector['id'],fields_json)
            print('\tRenamed to [{0}]'.format(collector_name_replacement[collector['name']]))


def get_hosted_sources():
    for collector in list_collectors().json()['collectors']:
        if collector['collectorType'] == 'Hosted':
            print('Fetching sources for [{0}]'.format(collector['name']))
            pprint.pprint(list_sources(collector['id']).json())
            print('')