""" >>>>>>>>>> IMPORTANT <<<<<<<<<<

You will need to create a Sumo Logic access key to use this script.
Follow the guide here: https://help.sumologic.com/Manage/Security/Access-Keys#manage-your-access-keys-on-preferences-page

"""

import requests

# Encode the credentials
import base64

# URL encoding
import urllib.parse

# Pretty print
import pprint

# Handling different file/content types
import json
import jsonschema


class SumoClient:
    def __init__(self, access_id, access_key):
        self.__access_id    = access_id
        self.__access_key   = access_key
        self.__endpoint     = self.__get_geo_endpoint()

    def __execute_api(self, request_type, request_url, request_params = None, request_data = None, additional_headers = {}):
        """Basic function to remove this snippet of code out of every other function.

        Args:
            request_type: string, what type of request is being made (ie - GET, POST, DELETE).
            request_url: string, the target API URL.
            request_params: dict, any data that needs to be sent through a query string.
            request_data: dict, any data that needs to be sent through the message body rather than through
                parameters in the query string. Only required for POST, PUT, and PATCH.
            additional_headers: dict, any extra headers to add to the base auth headers.
        """

        # There are a specific set of request types that can be executed.
        valid_types = ['GET', 'OPTIONS', 'HEAD', 'POST', 'PUT', 'PATCH', 'DELETE']
        if request_type not in valid_types:
            raise ValueError('execute_api: request_type must be one of {0}.'.format(valid_types))   

        # Construct the auth header for regular API queries
        request_headers = {
            'Authorization': 'Basic {0}'.format(
                base64.b64encode(
                    bytes(
                        '{0}:{1}'.format(
                            self.__access_id,
                            self.__access_key
                        ),
                        'utf-8'
                    )
                ).decode('utf-8')
            )
        }

        # If any data is being passed, it will need to have the Content-Type header set.
        if request_data is not None:
            request_headers['Content-Type'] = 'application/json'

        # If any API calls require additional headers, add them here.
        request_headers.update(additional_headers) 

        # Execute the request, and return the JSON payload.
        return requests.request(
            method  = request_type,
            url     = request_url,
            params  = request_params,
            data    = json.dumps(request_data),
            headers = request_headers
        )
    
    def __get_geo_endpoint(self):
        return self.__execute_api(
            request_type    = 'GET',
            request_url     = 'https://api.sumologic.com/api'
        ).url

    def __generate_path_param_string(self, path_params):
        arg_array = []
        for key, value in path_params.items():
            arg_array.append(key+'='+str(value))
        arg_string = '&'.join(filter(None, arg_array))
        return arg_string

    def __is_json_valid(self, json, schema):
        try:
            jsonschema.validate(instance=json, schema=schema)
        except jsonschema.exceptions.ValidationError:
            return False
        return True


    # # # ==================================================
    # # #
    # # # COLLECTOR MANAGEMENT API
    # # # https://help.sumologic.com/APIs/01Collector-Management-API

    # # # --------------------------------------------------
    # # #
    # # # Collector API Methods
    # # # https://help.sumologic.com/APIs/01Collector-Management-API/Collector-API-Methods-and-Examples

    """ List Collectors  
    Get a list of Collectors with an optional limit and offset.

    Method: GET
    Path:   /collectors
    https://help.sumologic.com/APIs/01Collector-Management-API/Collector-API-Methods-and-Examples#list-collectors
    """
    def list_collectors(self, path_params = {}):
        path_params_schema = {
            '$schema': 'http://json-schema.org/draft/2019-09/schema',
            'type': 'object',
            'properties': {
                'aliveBeforeDays': {
                    'type': 'integer',
                    'minimum': 1
                },
                'limit': {
                    'type': 'integer'
                },
                'offset': {
                    'type': 'integer'
                }
            },
            'required': [],
            'additionalProperties': False
        }
        jsonschema.validate(
            instance        = path_params,
            schema          = path_params_schema
        )
        request_url = '{0}/v1/collectors'.format(
            self.__endpoint
        )
        return self.__execute_api(
            request_type    = 'GET',
            request_url     = request_url
        )


    """ List Offline Collectors
    Get a list of Installed Collectors last seen alive before a specified number of days with an optional limit and
    offset.

    Method: GET
    Path:   /collectors/offline
    https://help.sumologic.com/APIs/01Collector-Management-API/Collector-API-Methods-and-Examples#list-offline-collectors
    """
    def list_offline_collectors(self, path_params = {}):
        path_params_schema = {
            '$schema': 'http://json-schema.org/draft/2019-09/schema',
            'type': 'object',
            'properties': {
                'aliveBeforeDays': {
                    'type': 'integer',
                    'minimum': 1
                },
                'limit': {
                    'type': 'integer'
                },
                'offset': {
                    'type': 'integer'
                }
            },
            'required': [],
            'additionalProperties': False
        }
        jsonschema.validate(
            instance        = path_params,
            schema          = path_params_schema
        )

        request_url = '{0}/v1/collectors/offline'.format(
            self.__endpoint
        )
        request_url = '{0}?{1}'.format(
            request_url,
            self.__generate_path_param_string(path_params)
        )
        return self.__execute_api(
            request_type    = 'GET',
            request_url     = request_url
        )


    """ Get Collector by ID 
    Get the Collector with the specified Identifier.

    Method: GET
    Path:   /collectors/{collector_id}
    https://help.sumologic.com/APIs/01Collector-Management-API/Collector-API-Methods-and-Examples#get-collector%C2%A0by-id
    """
    def get_collector_by_id(self, collector_id):
        request_url = '{0}/v1/collectors/{1}'.format(
            self.__endpoint,
            collector_id
        )
        return self.__execute_api(
            request_type    = 'GET',
            request_url     = request_url
        )


    """ Get Collector by Name 
    Get the Collector with the specified Name.

    Method: GET
    Path:   /collectors/name/{collector_name}
    https://help.sumologic.com/APIs/01Collector-Management-API/Collector-API-Methods-and-Examples#get-collector%C2%A0by-name
    """
    def get_collector_by_name(self, collector_name):
        # Names with special characters are not supported, such as ; / % \ even if they are URL encoded.
        special_characters = [';','/','%','\\']
        if any(char in collector_name for char in special_characters):
            raise ValueError('get_collector_by_name: collector_name must not contain any of these characters {0}.'.format(special_characters))

        request_url = '{0}/v1/collectors/name/{1}'.format(
            self.__endpoint,
            urllib.parse.quote(collector_name)
        )

        # Names with a period . need to have a trailing forward slash / at the end of the request URL.
        if '.' in collector_name:
            request_url += '/'

        return self.__execute_api(
            request_type    = 'GET',
            request_url     = request_url
        )


    """ Create Hosted Collector
    Use the POST method with a JSON file to create a new Hosted Collector. The required parameters can be referenced
    in the Response fields table above. Note that "id" field should be omitted when creating a new Hosted Collector.

    Important: This method can only be used to create Hosted Collectors. You must install a Collector manually to
    create an Installed Collector.

    Method: POST
    Path:   /collectors
    https://help.sumologic.com/APIs/01Collector-Management-API/Collector-API-Methods-and-Examples#create-hosted-collector
    """
    def create_hosted_collector(self, collector_data):
        collector_schema = {
            '$schema': 'http://json-schema.org/draft/2019-09/schema',
            'type': 'object',
            'properties': {
                'category': {
                    'type': 'string'
                },
                'collectorType': {
                    'type': 'string',
                    'enum': [
                        'Hosted'
                    ]
                },
                'cutoffRelativeTime': {
                    'type': 'string'
                },
                'cutoffTimestamp': {
                    'type': 'integer'
                },
                'description': {
                    'type': 'sring'
                },
                'ephemeral': {
                    'type': 'boolean'
                },
                'fields': {
                    'type': 'object'
                },
                'hostName': {
                    'type': 'string'
                },
                'name': {
                    'type': 'string'
                },
                'sourceSyncMode': {
                    'type': 'string',
                    'enum': [
                        'Json',
                        'UI'
                    ]
                },
                'timeZone': {
                    'type': 'string'
                },
                'targetCpu': {
                    'type': 'integer'
                }
            },
            'required': [
                'collectorType',
                'ephemeral',
                'name'
            ],
            'not': {
                'required': [
                    'cutoffRelativeTime',
                    'cutoffTimestamp'
                ] 
            },
            'additionalProperties': False
        }
        jsonschema.validate(
            instance        = collector_data,
            schema          = collector_schema
        )
        request_url = '{0}/v1/collectors'.format(
            self.__endpoint
        )
        return self.__execute_api(
            request_type    = 'POST',
            request_url     = request_url,
            request_data    = collector_data
        )


    """ Update a Collector 
    Use the PUT method with your JSON file to update an existing Collector. Available parameters can be referenced in
    the Response fields table above. The JSON request file must specify values for all required fields. Not modifiable
    fields must match their current values in the system. This is in accordance with HTTP 1.1 RFC-2616 Section 9.6. 

    Updating a Collector also requires the "If-Match" header to be specified with the "ETag" provided in the headers
    of a previous GET request.

    Method: PUT
    Path:   /collectors/{collector_id}
    https://help.sumologic.com/APIs/01Collector-Management-API/Collector-API-Methods-and-Examples#update%C2%A0a-collector
    """
    def update_collector(self, collector_id, collector_updates):
        update_schema = {
            '$schema': 'http://json-schema.org/draft/2019-09/schema',
            'type': 'object',
            'properties': {
                'category': {
                    'type': 'string'
                },
                'cutoffTimestamp': {
                    'type': 'integer'
                },
                'description': {
                    'type': 'sring'
                },
                'ephemeral': {
                    'type': 'boolean'
                },
                'fields': {
                    'type': 'object'
                },
                'hostName': {
                    'type': 'string'
                },
                'name': {
                    'type': 'string'
                },
                'sourceSyncMode': {
                    'type': 'string',
                    'enum': [
                        'Json',
                        'UI'
                    ]
                },
                'timeZone': {
                    'type': 'string'
                },
                'targetCpu': {
                    'type': 'integer'
                }
            },
            'required': [],
            'additionalProperties': False
        }
        jsonschema.validate(
            instance    = collector_updates,
            schema      = update_schema
        )

        collector = self.get_collector_by_id(collector_id).json()
        collector['collector'].update(collector_updates)

        request_url = '{0}/v1/collectors/{1}'.format(
            self.__endpoint,
            collector_id
        )
        additional_headers = {
            'If-Match': collector.headers['ETag']
        }
        return self.__execute_api(
            request_type        = 'PUT',
            request_url         = request_url,
            additional_headers  = additional_headers,
            request_data        = collector
        )


    """ Delete Collector by ID
    Use the DELETE method to delete an existing Collector.

    Method: DELETE
    Path:   /collectors/{collector_id}
    https://help.sumologic.com/APIs/01Collector-Management-API/Collector-API-Methods-and-Examples#delete%C2%A0collector-by-id
    """
    def delete_collector_by_id(self, collector_id):
        request_url = '{0}/v1/collectors/{1}'.format(
            self.__endpoint,
            collector_id
        )
        return self.__execute_api(
            request_type    = 'DELETE',
            request_url     = request_url
        )


    """ Delete Offline Collectors
    Delete Installed Collectors last seen alive before a specified number of days.

    Method: DELETE
    Path:   /collectors/offline
    https://help.sumologic.com/APIs/01Collector-Management-API/Collector-API-Methods-and-Examples#delete-offline-collectors
    """
    def delete_offline_collectors(self, path_params = {}):
        path_params_schema = {
            '$schema': 'http://json-schema.org/draft/2019-09/schema',
            'type': 'object',
            'properties': {
                'aliveBeforeDays': {
                    'type': 'integer',
                    'minimum': 1
                }
            },
            'required': [],
            'additionalProperties': False
        }
        jsonschema.validate(
            instance        = path_params,
            schema          = path_params_schema
        )
        request_url = '{0}/v1/collectors/offline'.format(
            self.__endpoint
        )
        request_url = '{0}?{1}'.format(
            request_url,
            self.__generate_path_param_string(path_params)
        )
        return self.__execute_api(
            request_type        = 'DELETE',
            request_url         = request_url
        )



    # # # --------------------------------------------------
    # # #
    # # # Source API Methods
    # # # https://help.sumologic.com/APIs/01Collector-Management-API/Source-API

    """ List Sources
    Gets information about all Sources for a specified Collector.

    Method: GET
    Path:   /collectors/{collector_id}/sources
    https://help.sumologic.com/APIs/01Collector-Management-API/Source-API#list%C2%A0sources
    """
    def list_sources(self, collector_id, path_params = {}):
        path_params_schema = {
            '$schema': 'http://json-schema.org/draft/2019-09/schema',
            'type': 'object',
            'properties': {
                'download': {
                    'type': 'boolean'
                }
            },
            'required': [],
            'additionalProperties': False
        }
        jsonschema.validate(
            instance        = path_params,
            schema          = path_params_schema
        )
        request_url = '{0}/v1/collectors/{1}/sources'.format(
            self.__endpoint,
            collector_id
        )
        request_url = '{0}?{1}'.format(
            request_url,
            self.__generate_path_param_string(path_params)
        )
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url
        )


    """ Get Source by ID
    Gets information about a specified Collector and Source.

    Method: GET
    Path:   /collectors/{collector_id}/sources/{source_id}
    https://help.sumologic.com/APIs/01Collector-Management-API/Source-API#get%C2%A0source-by-id
    """
    def get_source_by_id(self, collector_id, source_id, path_params = {}):
        path_params_schema = {
            '$schema': 'http://json-schema.org/draft/2019-09/schema',
            'type': 'object',
            'properties': {
                'download': {
                    'type': 'boolean'
                }
            },
            'required': [],
            'additionalProperties': False
        }
        jsonschema.validate(
            instance        = path_params,
            schema          = path_params_schema
        )
        request_url = '{0}/v1/collectors/{1}/sources/{2}'.format(
            self.__endpoint,
            collector_id,
            source_id
        )
        request_url = '{0}?{1}'.format(
            request_url,
            self.__generate_path_param_string(path_params)
        )
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url
        )


    """ Create Source
    Creates a new Source for a Collector. See
    https://help.sumologic.com/03Send-Data/Sources/03Use-JSON-to-Configure-Sources for required fields for the
    request JSON file.

    Method: POST
    Path:   /collectors/{collector_id}/sources
    https://help.sumologic.com/APIs/01Collector-Management-API/Source-API#create-source
    """
    def create_source(self, collector_id, source_json):
        source_schema = {
            '$schema': 'http://json-schema.org/draft/2019-09/schema',
            'type': 'object',
            'properties': {
                'sourceType': {
                    'type': 'string',
                    'enum': [
                        'LocalFile',
                        'RemoteFileV2',
                        'LocalWindowsEventLog',
                        'RemoteWindowsEventLog',
                        'LocalWindowsPerfMon',
                        'RemoteWindowsPerfMon',
                        'Syslog',
                        'Script',
                        'DockerLog',
                        'DockerStats',
                        'SystemStats',
                        'StreamingMetrics',
                        'HTTP',
                        'Cloudsyslog',
                        'Polling'
                    ]
                },
                'name': {
                    'type': 'string'
                },
                'description': {
                    'type': 'string'
                },
                'fields': {
                    'type': 'object'
                },
                'hostName': {
                    'type': 'string'
                },
                'category': {
                    'type': 'string'
                },
                'automaticDateParsing': {
                    'type': 'boolean'
                },
                'timeZone': {
                    'type': 'string'
                },
                'forceTimeZone': {
                    'type': 'boolean'
                },
                'defaultDateFormat': {
                    'type': 'string'
                },
                'defaultDateFormats': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'format': 'string',
                            'locator': 'string'
                        },
                        'required': [
                            'format'
                        ],
                        'additionalProperties': False
                    }
                },
                'multilineProcessingEnabled': {
                    'type': 'boolean'
                },
                'useAutolineMatching': {
                    'type': 'boolean'
                },
                'manualPrefixRegexp': {
                    'type': 'string'
                },
                'filters': {
                    'type': 'array',
                    'items': {
                        'type': 'string'
                    }
                },
                'cutoffTimestamp': {
                    'type': 'integer'
                },
                'cutoffRelativeTime': {
                    'type': 'string'
                }
            },
            'required': [
                'sourceType',
                'name'
            ],
            'not': {
                'required': [
                    'cutoffRelativeTime',
                    'cutoffTimestamp'
                ] 
            },
            'additionalProperties': False
        }
        jsonschema.validate(
            instance        = source_json,
            schema          = source_schema
        )
        request_url = '{0}/v1/collectors/{1}/sources'.format(
            self.__endpoint,
            collector_id
        )
        return self.__execute_api(
            request_type    = 'POST',
            request_url     = request_url,
            request_data    = source_json
        )


    """ Update Source
    Updates an existing source. All modifiable fields must be provided, and all not modifiable fields must match those
    existing in the system.

    Updating a Source also requires the "If-Match" header to be specified with the "ETag" provided in the headers of a
    previous GET request.

    Method: PUT
    Path:   /collectors/{collector_id}/sources/{source_id}
    """
    def update_source(self, collector_id, source_id, source_updates):
        update_schema = {
            '$schema': 'http://json-schema.org/draft/2019-09/schema',
            'type': 'object',
            'properties': {
                'name': {
                    'type': 'string'
                },
                'description': {
                    'type': 'string'
                },
                'fields': {
                    'type': 'object'
                },
                'hostName': {
                    'type': 'string'
                },
                'category': {
                    'type': 'string'
                },
                'automaticDateParsing': {
                    'type': 'boolean'
                },
                'timeZone': {
                    'type': 'string'
                },
                'forceTimeZone': {
                    'type': 'boolean'
                },
                'defaultDateFormat': {
                    'type': 'string'
                },
                'defaultDateFormats': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'format': 'string',
                            'locator': 'string'
                        },
                        'required': [
                            'format'
                        ],
                        'additionalProperties': False
                    }
                },
                'multilineProcessingEnabled': {
                    'type': 'boolean'
                },
                'useAutolineMatching': {
                    'type': 'boolean'
                },
                'manualPrefixRegexp': {
                    'type': 'string'
                },
                'filters': {
                    'type': 'array',
                    'items': {
                        'type': 'string'
                    }
                },
                'cutoffTimestamp': {
                    'type': 'integer'
                }
            },
            'required': [
                'sourceType',
                'name'
            ],
            'additionalProperties': False
        }
        jsonschema.validate(
            instance        = source_updates,
            schema          = update_schema
        )

        source = self.get_source_by_id(collector_id, source_id).json()
        source['source'].update(source_updates)

        request_url = '{0}/v1/collectors/{1}/sources/{2}'.format(
            self.__endpoint,
            collector_id,
            source_id
        )
        additional_headers = {
            'If-Match': source.headers['ETag']
        }
        return self.__execute_api(
            request_type        = 'PUT',
            request_url         = request_url,
            additional_headers  = additional_headers,
            request_data        = source
        )


    """ Delete Source
    Deletes the specified Source from the specified Collector.

    Method: DELETE
    Path:   /collectors/{collector_id}/sources/{source_id}
    """
    def delete_source(self, collector_id, source_id):
        request_url = '{0}/v1/collectors/{1}/sources/{2}'.format(
            self.__endpoint,
            collector_id,
            source_id
        )
        return self.__execute_api(
            request_type    = 'DELETE',
            request_url     = request_url
        )



    # # #   --------------------------------------------------
    # # #
    # # #   Upgrade or Downgrade Collectors Using the API
    # # #   https://help.sumologic.com/APIs/01Collector-Management-API/Upgrade-or-Downgrade-Collectors-Using-the-API

    """ Get upgradable Collectors
    Sends a request to get Collectors you can upgrade.

    Method: GET 
    Path:   /collectors/upgrades/collectors
    https://help.sumologic.com/APIs/01Collector-Management-API/Upgrade-or-Downgrade-Collectors-Using-the-API#get-upgradable-collectors
    """
    def get_upgradable_collectors(self, path_params = {}):
        path_params_schema = {
            '$schema': 'http://json-schema.org/draft/2019-09/schema',
            'type': 'object',
            'properties': {
                'toVersion': {
                    'type': 'string'
                },
                'offset': {
                    'type': 'integer'
                },
                'limit': {
                    'type': 'integer'
                }
            },
            'required': [],
            'additionalProperties': False
        }
        jsonschema.validate(
            instance    = path_params,
            schema      = path_params_schema
        )
        request_url = '{0}/v1/collectors/upgrades/collectors'.format(
            self.__endpoint
        )
        request_url = '{0}?{1}'.format(
            request_url,
            self.__generate_path_param_string(path_params)
        )
        additional_headers = {
            'Accept': 'application/json'
        }
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url,
            additional_headers  = additional_headers
        )


    """ Get available builds

    Method: GET 
    Path:   /collectors/upgrades/targets
    https://help.sumologic.com/APIs/01Collector-Management-API/Upgrade-or-Downgrade-Collectors-Using-the-API#get-available-builds
    """
    def get_available_builds(self):
        request_url = '{0}/v1/collectors/upgrades/targets'.format(
            self.__endpoint
        )
        return self.__execute_api(
            request_type    = 'GET',
            request_url     = request_url
        )


    """ Create an upgrade or downgrade task

    Method: POST 
    Path:   /collectors/upgrades
    https://help.sumologic.com/APIs/01Collector-Management-API/Upgrade-or-Downgrade-Collectors-Using-the-API#create-an-upgrade-or-downgrade-task
    """
    def create_an_upgrade_or_downgrade_task(self, request_data):
        data_schema = {
            '$schema': 'http://json-schema.org/draft/2019-09/schema',
            'type': 'object',
            'properties': {
                'collectorId': {
                    'type': 'integer'
                },
                'toVersion': {
                    'type': 'string'
                }
            },
            'required': [
                'collectorId'
            ],
            'additionalProperties': False
        }
        jsonschema.validate(
            instance    = request_data,
            schema      = data_schema
        )
        request_url = '{0}/v1/collectors/upgrades'.format(
            self.__endpoint
        )
        return self.__execute_api(
            request_type    = 'POST',
            request_url     = request_url,
            request_data    = request_data
        )


    """ Get upgrade task status
    After obtaining the upgrade job ID, you can obtain the status of the upgrade task from the status endpoint.

    Method: GET 
    Path:   /collectors/upgrades/{upgrade_task_id}
    https://help.sumologic.com/APIs/01Collector-Management-API/Upgrade-or-Downgrade-Collectors-Using-the-API#get-upgrade-task-status
    """
    def get_upgrade_task_status(self, upgrade_task_id):
        request_url = '{0}/v1/collectors/upgrades/{1}'.format(
            self.__endpoint,
            upgrade_task_id
        )
        return self.__execute_api(
            request_type    = 'GET',
            request_url     = request_url
        )



    # # #   ==================================================
    # # #   ----[BETA]----------------------------------------
    # # #   HEALTH EVENTS MANAGEMENT API
    # # #   https://api.au.sumologic.com/docs/#tag/healthEvents
    # # #
    # # #   Health Events allow you to keep track of the health of your Collectors and Sources. You can use them to
    # # #   find and investigate common errors and warnings that are known to cause collection issues. For more
    # # #   information see https://help.sumologic.com/?cid=0020.
    # # #
    # # #   This API is in private beta and is not available until access is granted. Contact your Sumo Logic account
    # # #   representative to participate in the beta program.

    """ Get a list of health events.
    Get a list of all the unresolved health events in your account.

    Method: GET
    Path:   /v1/healthEvents
    https://api.au.sumologic.com/docs/#operation/listAllHealthEvents
    """
    def get_health_events(self, request_params={}):
        request_params_schema = {
            '$schema': 'http://json-schema.org/draft/2019-09/schema',
            'type': 'object',
            'properties': {
                'limit': {
                    'type': 'integer',
                    'minimum': 1,
                    'maximum': 1000
                },
                'token': {
                    'type': 'string'
                },
            },
            'required': [],
            'additionalProperties': False
        }
        jsonschema.validate(
            instance    = request_params,
            schema      = request_params_schema
        )
        request_url = '{0}/v1/healthEvents'.format(
            self.__endpoint
        )
        return self.__execute_api(
            request_type    = 'GET',
            request_url     = request_url,
            request_params  = request_params
        )


    """ Health events for specific resources.
    Get a list of all the unresolved events in your account that belong to the supplied resource identifiers.

    Method: POST
    Path:   /v1/healthEvents/resources
    https://api.au.sumologic.com/docs/#operation/listAllHealthEventsForResources
    """
    def get_specific_health_events(self, resource_list, request_params={}):
        resource_list_schema = {
            '$schema': 'http://json-schema.org/draft/2019-09/schema',
            'type': 'object',
            'properties': {
                'data': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {
                                'type': 'string'
                            },
                            'name': {
                                'type': 'string'
                            },
                            'type': {
                                'type': 'string',
                                'enum': [
                                    'Collector',
                                    'Source',
                                    'IngestBudget',
                                    'Organisation',
                                    'LogsToMetricsRule'
                                ]
                            }
                        },
                        'required': [
                            'id',
                            'type'
                        ],
                        'additionalProperties': False
                    }
                },
            },
            'required': [
                'data'
            ],
            'additionalProperties': False
        }
        jsonschema.validate(
            instance    = resource_list,
            schema      = resource_list_schema
        )
        request_params_schema = {
            '$schema': 'http://json-schema.org/draft/2019-09/schema',
            'type': 'object',
            'properties': {
                'limit': {
                    'type': 'integer',
                    'minimum': 1,
                    'maximum': 1000
                },
                'token': {
                    'type': 'string'
                },
            },
            'required': [],
            'additionalProperties': False
        }
        jsonschema.validate(
            instance    = request_params,
            schema      = request_params_schema
        )
        request_url = '{0}/v1/healthEvents/resources'.format(
            self.__endpoint
        )
        request_data = {
            'data': resource_list
        }
        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url,
            request_params      = request_params,
            request_data        = request_data
        )



    # # #   ==================================================
    # # # 
    # # #   INGEST BUDGET MANAGEMENT API
    # # #   https://api.au.sumologic.com/docs/#tag/ingestBudgetManagementV1
    # # #
    # # #   Ingest Budgets allow you to control the capacity of daily ingestion volume sent to Sumo Logic from
    # # #   Collectors. For more information see https://help.sumologic.com/?cid=5235.

    """ Get a list of ingest budgets.
    Get a list of all ingest budgets. The response is paginated with a default limit of 100 budgets per page.

    Method: GET
    Path:   /v1/ingestBudgets
    https://api.au.sumologic.com/docs/#operation/listIngestBudgets
    """
    def get_ingest_budgets(self, request_params={}):
        request_params_schema = {
            '$schema': 'http://json-schema.org/draft/2019-09/schema',
            'type': 'object',
            'properties': {
                'limit': {
                    'type': 'integer',
                    'minimum': 1,
                    'maximum': 1000
                },
                'token': {
                    'type': 'string'
                },
            },
            'required': [],
            'additionalProperties': False
        }
        jsonschema.validate(
            instance    = request_params,
            schema      = request_params_schema
        )
        request_url = '{0}/v1/ingestBudgets'.format(
            self.__endpoint
        )
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url,
            request_params      = request_params
        )


    """ Create a new ingest budget.
    Create a new ingest budget.

    Method: POST
    Path:   /v1/ingestBudgets
    https://api.au.sumologic.com/docs/#operation/createIngestBudget
    """
    def create_ingest_budget(self, request_data):
        request_data_schema = {
            '$schema': 'http://json-schema.org/draft/2019-09/schema',
            'type': 'object',
            'properties': {
                'name': {
                    'type': 'string',
                    'minLength': 1,
                    'maxLength': 128
                },
                'fieldValue': {
                    'type': 'string',
                    'minLength': 1,
                    'maxLength': 1024
                },
                'capacityBytes': {
                    'type': 'integer',
                    'minimum': 0
                },
                'timezone': {
                    'type': 'string'
                },
                'resetTime': {
                    'type': 'string',
                    'minLength': 5,
                    'maxLength': 5
                },
                'description' : {
                    'type': 'string',
                    'minLength': 1,
                    'maxLength': 1024
                },
                'action': {
                    'type': 'string',
                    'enum': [
                        'stopCollecting',
                        'keepCollecting'
                    ]
                },
                'auditThreshold': {
                    'type': 'integer',
                    'minimum': 1,
                    'maximum': 99
                }
            },
            'required': [
                'name',
                'fieldValue',
                'capacityBytes',
                'timezone',
                'resetTime',
                'action'
            ],
            'additionalProperties': False
        }
        jsonschema.validate(
            instance    = request_data,
            schema      = request_data_schema
        )
        request_url = '{0}/v1/ingestBudgets'.format(
            self.__endpoint
        )
        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url,
            request_data        = request_data
        )


    """ Get an ingest budget.
    Get an ingest budget by the given identifier.

    Method: GET
    Path:   /v1/ingestBudgets/{budget_id}
    https://api.au.sumologic.com/docs/#operation/getIngestBudget
    """
    def get_ingest_budget(self, budget_id):
        request_url = '{0}/v1/ingestBudgets/{1}'.format(
            self.__endpoint,
            budget_id
        )
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url
        )


    """ Update an ingest budget.
    Update an existing ingest budget. All properties specified in the request are required.

    Method: PUT
    Path:   /v1/ingestBudgets/{budget_id}
    https://api.au.sumologic.com/docs/#operation/updateIngestBudget
    """
    def update_ingest_budget(self, budget_id, request_data):
        request_data_schema = {
            '$schema': 'http://json-schema.org/draft/2019-09/schema',
            'type': 'object',
            'properties': {
                'name': {
                    'type': 'string',
                    'minLength': 1,
                    'maxLength': 128
                },
                'fieldValue': {
                    'type': 'string',
                    'minLength': 1,
                    'maxLength': 1024
                },
                'capacityBytes': {
                    'type': 'integer',
                    'minimum': 0
                },
                'timezone': {
                    'type': 'string'
                },
                'resetTime': {
                    'type': 'string',
                    'minLength': 5,
                    'maxLength': 5
                },
                'description' : {
                    'type': 'string',
                    'minLength': 1,
                    'maxLength': 1024
                },
                'action': {
                    'type': 'string',
                    'enum': [
                        'stopCollecting',
                        'keepCollecting'
                    ]
                },
                'auditThreshold': {
                    'type': 'integer',
                    'minimum': 1,
                    'maximum': 99
                }
            },
            'required': [
                'name',
                'fieldValue',
                'capacityBytes',
                'timezone',
                'resetTime',
                'action'
            ],
            'additionalProperties': False
        }
        jsonschema.validate(
            instance    = request_data,
            schema      = request_data_schema
        )
        request_url = '{0}/v1/ingestBudgets/{1}'.format(
            self.__endpoint,
            budget_id
        )
        return self.__execute_api(
            request_type        = 'PUT',
            request_url         = request_url,
            request_data        = request_data
        )


    """ Delete an ingest budget.
    Delete an ingest budget with the given identifier.

    Method: DELETE
    Path:   /v1/ingestBudgets/{budget_id}
    https://api.au.sumologic.com/docs/#operation/deleteIngestBudget
    """
    def delete_ingest_budget(self, budget_id):
        request_url = '{0}/v1/ingestBudgets/{1}'.format(
            self.__endpoint,
            budget_id
        )
        return self.__execute_api(
            request_type        = 'DELETE',
            request_url         = request_url
        )


    """ Reset usage.
    Reset ingest budget's current usage to 0 before the scheduled reset time.

    Method: POST
    Path:   /v1/ingestBudgets/{budget_id}/usage/reset
    https://api.au.sumologic.com/docs/#operation/resetUsage
    """
    def reset_budget_usage(self, budget_id):
        request_url = '{0}/v1/ingestBudgets/{1}/usage/reset'.format(
            self.__endpoint,
            budget_id
        )
        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url
        )


    """ Get a list of Collectors.
    Get a list of Collectors assigned to an ingest budget. The response is paginated with a default limit of 100
    Collectors per page.

    Method: GET
    Path:   /v1/ingestBudgets/{budget_id}/collectors
    https://api.au.sumologic.com/docs/#operation/getAssignedCollectors
    """
    def get_budget_collectors(self, budget_id, request_params={}):
        request_params_schema = {
            '$schema': 'http://json-schema.org/draft/2019-09/schema',
            'type': 'object',
            'properties': {
                'limit': {
                    'type': 'integer',
                    'minimum': 1,
                    'maximum': 1000
                },
                'token': {
                    'type': 'string'
                },
            },
            'required': [],
            'additionalProperties': False
        }
        jsonschema.validate(
            instance    = request_params,
            schema      = request_params_schema
        )
        request_url = '{0}/v1/ingestBudgets/{1}/collectors'.format(
            self.__endpoint,
            budget_id
        )
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url,
            request_params      = request_params
        )


    """ Assign a Collector to a budget.
    Assign a Collector to a budget.

    Method: PUT
    Path:   /v1/ingestBudgets/{budget_id}/collectors/{collector_id}
    https://api.au.sumologic.com/docs/#operation/assignCollectorToBudget
    """
    def assign_budget_collector(self, budget_id, collector_id):
        request_url = '{0}/v1/ingestBudgets/{1}/collectors/{2}'.format(
            self.__endpoint,
            budget_id,
            collector_id
        )
        return self.__execute_api(
            request_type    = 'PUT',
            request_url     = request_url
        )


    """ Remove Collector from a budget.
    Remove Collector from a budget.

    Method: DELETE
    Path:   /v1/ingestBudgets/{budget_id}/collectors/{collector_id}
    https://api.au.sumologic.com/docs/#operation/removeCollectorFromBudget
    """
    def remove_budget_collector(self, budget_id, collector_id):
        request_url = '{0}/v1/ingestBudgets/{1}/collectors/{2}'.format(
            self.__endpoint,
            budget_id,
            collector_id
        )
        return self.__execute_api(
            request_type    = 'DELETE',
            request_url     = request_url
        )



    # # #   ==================================================
    # # #   ----[BETA]----------------------------------------
    # # #   APP MANAGEMENT API
    # # #   https://api.au.sumologic.com/docs/#tag/appManagement
    # # #
    # # #   App installation API. View and install Sumo Logic Applications that deliver out-of-the-box dashboards,
    # # #   saved searches, and field extraction for popular data sources. For more information see
    # # #   https://help.sumologic.com/07Sumo-Logic-Apps.

    """ List available apps.
    Lists all available apps from the App Catalog.

    Method: GET
    Path:   /v1/apps
    https://api.au.sumologic.com/docs/#operation/listApps
    """
    def list_apps(self):
        request_url = '{0}/v1/apps'.format(
            self.__endpoint
        )
        return self.__execute_api(
            request_type    = 'GET',
            request_url     = request_url
        )

    """ Get an app by UUID.
    Gets the app with the given universally unique identifier (UUID).

    Method: GET
    Path:   /v1/apps/{uuid}
    https://api.au.sumologic.com/docs/#operation/getApp
    """
    def get_app(self, uuid):
        request_url = '{0}/v1/apps/{1}'.format(
            self.__endpoint,
            uuid
        )
        return self.__execute_api(
            request_type    = 'GET',
            request_url     = request_url
        )

    """ Install an app by UUID.
    Installs the app with given UUID in the folder specified using destinationFolderId.

    Method: POST
    Path:   /v1/apps/{uuid}/install
    https://api.au.sumologic.com/docs/#operation/installApp
    """
    def install_app(self, uuid, request_data):
        request_data_schema = {
            '$schema': 'http://json-schema.org/draft/2019-09/schema',
            'type': 'object',
            'properties': {
                'name': {
                    'type': 'string',
                    'minLength': 1,
                    'maxLength': 128
                },
                'description' : {
                    'type': 'string',
                    'minLength': 1,
                    'maxLength': 255
                },
                'destinationFolderId': {
                    'type': 'string'
                },
                'dataSourceValues': {
                    'type': 'object',
                    'additionalProperties': True
                }
            },
            'required': [
                'name',
                'description',
                'destinationFolderId'
            ],
            'additionalProperties': False
        }
        jsonschema.validate(
            instance    = request_data,
            schema      = request_data_schema
        )
        request_url = '{0}/v1/apps/{1}/install'.format(
            self.__endpoint,
            uuid
        )
        return self.__execute_api(
            request_type    = 'POST',
            request_url     = request_url,
            request_data    = request_data
        )

    """ App install job status.
    Get the status of an asynchronous app install request for the given job identifier.

    Method: GET
    Path:   /v1/apps/install/{job_id}/status
    https://api.au.sumologic.com/docs/#operation/getAsyncInstallStatus
    """
    def get_app_install_status(self, job_id):
        request_url = '{0}/v1/apps/install/{1}/status'.format(
            self.__endpoint,
            job_id
        )
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url
        )



    # # #   ==================================================
    # # #
    # # #   CONTENT MANAGEMENT API
    # # #   https://help.sumologic.com/APIs/Content-Management-API
    # # #   https://api.au.sumologic.com/docs/#tag/contentManagement
    # # #
    # # #   You can export, import, delete and copy content in your organization’s Library. For more information see
    # # #   https://help.sumologic.com/?cid=5173. You can perform the request as a Content Administrator by using the
    # # #   is_admin_mode parameter. For more information see
    # # #   https://help.sumologic.com/Manage/Content_Sharing/Admin_Mode.

    """ Get content item by path.
    Get a content item corresponding to the given path.

    Method: GET
    Path:   /v2/content/path
    https://api.au.sumologic.com/docs/#operation/getItemByPath
    """
    def get_content_item_by_path(self, request_params):
        request_params_schema = {
            '$schema': 'http://json-schema.org/draft/2019-09/schema',
            'type': 'object',
            'properties': {
                'path': {
                    'type': 'string'
                }
            },
            'required': [
                'path'
            ],
            'additionalProperties': False
        }
        jsonschema.validate(
            instance    = request_params,
            schema      = request_params_schema
        )
        request_url = '{0}/v2/content/path'.format(
            self.__endpoint
        )
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url,
            request_params      = request_params
        )


    """ Get path of an item.
    Get full path of a content item with the given identifier.

    Method: GET
    Path:   /v2/content/{content_id}/path
    https://api.au.sumologic.com/docs/#operation/getPathById
    """
    def get_content_path_by_id(self, content_id):
        request_url = '{0}/v2/content/{1}/path'.format(
            self.__endpoint,
            content_id
        )
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url
        )



    """ Start a content export job.
    Schedule an asynchronous export of content with the given identifier. You will get back an asynchronous job
    identifier on success. Use the getAsyncExportStatus endpoint and the job identifier you got back in the response
    to track the status of an asynchronous export job. If the content item is a folder, everything under the folder is
    exported recursively. Keep in mind when exporting large folders that there is a limit of 1000 content objects that
    can be exported at once. If you want to import more than 1000 content objects, then be sure to split the import
    into batches of 1000 objects or less. The results from the export are compatible with the Library import feature
    in the Sumo Logic user interface as well as the API content import job.

    Method: POST
    Path:   /v2/content/{content_id}/export
    https://api.au.sumologic.com/docs/#operation/beginAsyncExport
    """
    def start_content_export(self, content_id, is_admin_mode=None):
        request_url = '{0}/v2/content/{1}/export'.format(
            self.__endpoint,
            content_id
        )
        additional_headers = {}
        if is_admin_mode is not None:
            additional_headers['isAdminMode'] = str(is_admin_mode).lower()
        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url,
            additional_headers  = additional_headers
        )


    """ Content export job status.
    Get the status of an asynchronous content export request for the given job identifier. On success, use the
    getExportResult endpoint to get the result of the export job.

    Method: GET
    Path:   /v2/content/{content_id}/export/{job_id}/status
    https://api.au.sumologic.com/docs/#operation/getAsyncExportStatus
    """
    def get_content_export_status(self, content_id, job_id, is_admin_mode=None):
        request_url = '{0}/v2/content/{1}/export/{2}/status'.format(
            self.__endpoint,
            content_id,
            job_id
        )
        additional_headers = {}
        if is_admin_mode is not None:
            additional_headers['isAdminMode'] = str(is_admin_mode).lower()
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url,
            additional_headers  = additional_headers
        )


    """ Content export job result.
    Get results from content export job for the given job identifier. The results from this export are incompatible
    with the Library import feature in the Sumo user interface.

    Method: GET
    Path:   /v2/content/{content_id}/export/{job_id}/result
    https://api.au.sumologic.com/docs/#operation/getAsyncExportResult
    """
    def get_content_export_result(self, content_id, job_id, is_admin_mode=None):
        request_url = '{0}/v2/content/{1}/export/{2}/result'.format(
            self.__endpoint,
            content_id,
            job_id
        )
        additional_headers = {}
        if is_admin_mode is not None:
            additional_headers['isAdminMode'] = str(is_admin_mode).lower()
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url,
            additional_headers  = additional_headers
        )


    # # #
    # # #   TODO: Implement checking of parsed JSON structures VS documentation.
    # # #
    """ Start a content import job.
    Schedule an asynchronous import of content inside an existing folder with the given identifier. Import requests
    can be used to create or update content within a folder. Content items need to have a unique name within their
    folder. If there is already a content item with the same name in the folder, you can set the overwrite parameter
    to true to overwrite existing content items. By default, the overwrite parameter is set to false, where the import
    will fail if a content item with the same name already exist. Keep in mind when importing large folders that there
    is a limit of 1000 content objects that can be imported at once. If you want to import more than 1000 content
    objects, then be sure to split the import into batches of 1000 objects or less.

    Method: POST
    Path:   /v2/content/folders/{folder_id}/import
    https://api.au.sumologic.com/docs/#operation/beginAsyncImport
    """
    def start_content_import(self, folder_id, request_data, request_params={}, is_admin_mode=None):
        request_params_schema = {
            '$schema': 'http://json-schema.org/draft/2019-09/schema',
            'type': 'object',
            'properties': {
                'overwrite': {
                    'type': 'boolean'
                }
            },
            'required': [],
            'additionalProperties': False
        }
        jsonschema.validate(
            instance    = request_params,
            schema      = request_params_schema
        )
        request_url = '{0}/v2/content/folders/{1}/import'.format(
            self.__endpoint,
            folder_id
        )
        additional_headers = {}
        if is_admin_mode is not None:
            additional_headers['isAdminMode'] = str(is_admin_mode).lower()
        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url,
            request_params      = request_params,
            additional_headers  = additional_headers,
            request_data        = request_data
        )


    """ Content import job status.
    Get the status of a content import job for the given job identifier.

    Method: GET
    Path:   /v2/content/folders/{folder_id}/import/{job_id}/status
    https://api.au.sumologic.com/docs/#operation/getAsyncImportStatus
    """
    def get_content_import_status(self, folder_id, job_id, is_admin_mode=None):
        request_url = '{0}/v2/content/folders/{1}/import/{2}/status'.format(
            self.__endpoint,
            folder_id,
            job_id
        )
        additional_headers = {}
        if is_admin_mode is not None:
            additional_headers['isAdminMode'] = str(is_admin_mode).lower()
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url,
            additional_headers  = additional_headers
        )


    """ Start a content deletion job.
    Start an asynchronous content deletion job with the given identifier.

    Method: DELETE
    Path:   /v2/content/{content_id}/delete
    https://api.au.sumologic.com/docs/#operation/beginAsyncDelete
    """
    def start_content_deletion(self, content_id, is_admin_mode=None):
        request_url = '{0}/v2/content/{1}/delete'.format(
            self.__endpoint,
            content_id
        )
        additional_headers = {}
        if is_admin_mode is not None:
            additional_headers['isAdminMode'] = str(is_admin_mode).lower()
        return self.__execute_api(
            request_type        = 'DELETE',
            request_url         = request_url,
            additional_headers  = additional_headers
        )


    """ Content deletion job status.
    Get the status of an asynchronous content deletion job request for the given job identifier.

    Method: GET
    Path:   /v2/content/{content_id}/delete/{job_id}/status
    https://api.au.sumologic.com/docs/#operation/getAsyncDeleteStatus
    """
    def get_content_deletion_status(self, content_id, job_id, is_admin_mode=None):
        request_url = '{0}/v2/content/{1}/delete/{2}/status'.format(
            self.__endpoint,
            content_id,
            job_id
        )
        additional_headers = {}
        if is_admin_mode is not None:
            additional_headers['isAdminMode'] = str(is_admin_mode).lower()
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url,
            additional_headers  = additional_headers
        )


    """ Start a content copy job.
    Start an asynchronous content copy job with the given identifier to the destination folder. If the content item is
    a folder, everything under the folder is copied recursively.

    Method: POST
    Path:   /v2/content/{content_id}/copy
    https://api.au.sumologic.com/docs/#operation/beginAsyncCopy
    """
    def start_content_copy(self, content_id, destination_folder_id, is_admin_mode=None):
        request_url = '{0}/v2/content/{1}/copy'.format(
            self.__endpoint,
            content_id
        )
        request_params = {
            'destinationFolder': destination_folder_id
        }
        additional_headers = {}
        if is_admin_mode is not None:
            additional_headers['isAdminMode'] = str(is_admin_mode).lower()
        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url,
            request_params      = request_params,
            additional_headers  = additional_headers
        )


    """ Content copy job status.
    Get the status of the copy request with the given job identifier. On success, field statusMessage will contain
    identifier of the newly copied content in format: id: {hexIdentifier}.

    Method: GET
    Path:   /v2/content/{content_id}/copy/{job_id}/status
    https://api.au.sumologic.com/docs/#operation/asyncCopyStatus
    """
    def get_content_copy_status(self, content_id, job_id, is_admin_mode=None):
        request_url = '{0}/v2/content/{1}/copy/{2}/status'.format(
            self.__endpoint,
            content_id,
            job_id
        )
        additional_headers = {}
        if is_admin_mode is not None:
            additional_headers['isAdminMode'] = str(is_admin_mode).lower()
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url,
            additional_headers  = additional_headers
        )


    """ Move an item.
    Moves an item from its current location to another folder.

    Method: POST
    Path:   /v2/content/{content_id}/move
    https://api.au.sumologic.com/docs/#operation/moveItem
    """
    def move_content_item(self, content_id, destination_folder_id, is_admin_mode=None):
        request_url = '{0}/v2/content/{1}/move'.format(
            self.__endpoint,
            content_id
        )
        request_params = {
            'destinationFolderId': destination_folder_id
        }
        additional_headers = {}
        if is_admin_mode is not None:
            additional_headers['isAdminMode'] = str(is_admin_mode).lower()
        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url,
            request_params      = request_params,
            additional_headers  = additional_headers
        )



    # # #   ==================================================
    # # #
    # # #   CONTENT PERMISSIONS API
    # # #   https://help.sumologic.com/APIs/Content_Permissions_API
    # # #   https://api.au.sumologic.com/docs/#tag/contentPermissions
    # # #
    # # #   You can share your folders, searches, and dashboards with specific users or roles. For more information
    # # #   see https://help.sumologic.com/?cid=8675309. You can perform the request as a Content Administrator by
    # # #   using the is_admin_mode parameter. For more information see
    # # #   https://help.sumologic.com/Manage/Content_Sharing/Admin_Mode.

    """ Get permissions of a content item
    Returns content permissions of a content item with the given identifier.

    Method: GET
    Path:   /v2/content/{content_id}/permissions
    https://api.au.sumologic.com/docs/#operation/getContentPermissions
    """
    def get_content_permissions(self, content_id, explicit_only=None, is_admin_mode=None):
        request_url = '{0}/v2/content/path'.format(
            self.__endpoint
        )
        request_params = {}
        if explicit_only is not None:
            request_params['explicitOnly'] = explicit_only
        additional_headers = {}
        if is_admin_mode is not None:
            additional_headers['isAdminMode'] = str(is_admin_mode).lower()
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url,
            request_params      = request_params,
            additional_headers  = additional_headers
        )


    # # #
    # # #   TODO: Implement checking of parsed JSON structures VS documentation.
    # # #
    """ Add permissions to a content item.
    Add permissions to a content item with the given identifier.

    Method: PUT
    Path:   /v2/content/{content_id}/permissions/add
    https://api.au.sumologic.com/docs/#operation/addContentPermissions
    """
    def add_content_permissions(self, content_id, content_permission_assignments, notify_recipients, notification_message, is_admin_mode=None):
        request_url = '{0}/v2/content/{1}/permissions/add'.format(
            self.__endpoint,
            content_id
        )
        request_data = {
            'contentPermissionAssignments': content_permission_assignments,
            'notifyRecipients': notify_recipients,
            'notificationMessage': notification_message
        }
        additional_headers = {}
        if is_admin_mode is not None:
            additional_headers['isAdminMode'] = str(is_admin_mode).lower()
        return self.__execute_api(
            request_type        = 'PUT',
            request_url         = request_url,
            request_data        = request_data,
            additional_headers  = additional_headers
        )


    # # #
    # # #   TODO: Implement checking of parsed JSON structures VS documentation.
    # # #
    """ Remove permissions from a content item.
    Remove permissions from a content item with the given identifier.

    Method: PUT
    Path:   /v2/content/{content_id}/permissions/remove
    https://api.au.sumologic.com/docs/#operation/removeContentPermissions
    """
    def remove_content_permissions(self, content_id, content_permission_assignments, notify_recipients, notification_message, is_admin_mode=None):
        request_url = '{0}/v2/content/{1}/permissions/add'.format(
            self.__endpoint,
            content_id
        )
        additional_headers = {}
        if is_admin_mode is not None:
            additional_headers['isAdminMode'] = str(is_admin_mode).lower()
        request_data = {
            'contentPermissionAssignments': content_permission_assignments,
            'notifyRecipients': notify_recipients,
            'notificationMessage': notification_message
        }
        return self.__execute_api(
            request_type        = 'PUT',
            request_url         = request_url,
            request_data        = request_data,
            additional_headers  = additional_headers
        )



    # # #   ==================================================
    # # #
    # # #   FOLDER MANAGEMENT API
    # # #   https://help.sumologic.com/APIs/Folder_Management_API
    # # #   https://api.au.sumologic.com/docs/#tag/folderManagement
    # # #
    # # #   You can add folders and subfolders to the Library in order to organize your content for easy access or to
    # # #   share content. For more information see https://help.sumologic.com/?cid=5020. You can perform the request
    # # #   as a Content Administrator by using the is_admin_mode parameter. For more information see
    # # #   https://help.sumologic.com/Manage/Content_Sharing/Admin_Mode.

    """ Create a new folder.
    Creates a new folder under the given parent folder.

    Method: POST
    Path:   /v2/content/folders
    https://api.au.sumologic.com/docs/#operation/createFolder
    """
    def create_folder(self, name, parent_id, description=False, is_admin_mode=None):
        request_url = '{0}/v2/content/folders'.format(
            self.__endpoint
        )
        request_data = {
            'name': name,
            'parentId': parent_id
        }
        if description is not None:
            request_data['description'] = description
        additional_headers = {}
        if is_admin_mode is not None:
            additional_headers['isAdminMode'] = str(is_admin_mode).lower()
        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url,
            request_data        = request_data,
            additional_headers  = additional_headers
        )


    """ Get a folder.
    Get a folder with the given identifier.

    Method: GET
    Path:   /v2/content/folders/{folder_id}
    https://api.au.sumologic.com/docs/#operation/getFolder
    """
    def get_folder(self, folder_id, is_admin_mode=None):
        request_url = '{0}/v2/content/folders/{1}'.format(
            self.__endpoint,
            folder_id
        )
        additional_headers = {}
        if is_admin_mode is not None:
            additional_headers['isAdminMode'] = str(is_admin_mode).lower()
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url,
            additional_headers  = additional_headers
        )


    """ Update a folder.
    Update an existing folder with the given identifier.

    Method: PUT
    Path:   /v2/content/folders/{folder_id}
    https://api.au.sumologic.com/docs/#operation/updateFolder
    """
    def update_folder(self, folder_id, name, description=None, is_admin_mode=None):
        request_url = '{0}/v2/content/folders/{1}'.format(
            self.__endpoint,
            folder_id
        )
        request_data = {
            'name': name
        }
        if description is not None:
            request_data['description'] = description
        additional_headers = {}
        if is_admin_mode is not None:
            additional_headers['isAdminMode'] = str(is_admin_mode).lower()
        return self.__execute_api(
            request_type        = 'PUT',
            request_url         = request_url,
            request_data        = request_data,
            additional_headers  = additional_headers
        )


    """ Get personal folder.
    Get the personal folder of the current user.

    Method: GET
    Path:   /v2/content/folders/personal
    https://api.au.sumologic.com/docs/#operation/getPersonalFolder
    """
    def get_personal_folder(self):
        request_url = '{0}/v2/content/folders/personal'.format(
            self.__endpoint
        )
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url
        )


    """ Get global folder.
    Schedule an asynchronous job to get global folder. Global folder contains all content items that a user has
    permissions to view in the organization.

    Method: GET
    Path:   /v2/content/folders/global
    https://api.au.sumologic.com/docs/#operation/getGlobalFolderAsync
    """
    def get_global_folder_job(self, is_admin_mode=None):
        request_url = '{0}/v2/content/folders/global'.format(
            self.__endpoint
        )
        additional_headers = {}
        if is_admin_mode is not None:
            additional_headers['isAdminMode'] = str(is_admin_mode).lower()
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url,
            additional_headers  = additional_headers
        )


    """ Global folder job status.
    Get the status of an asynchronous global folder job for the given job identifier.

    Method: GET
    Path:   /v2/content/folders/global/{job_id}/status
    https://api.au.sumologic.com/docs/#operation/getGlobalFolderAsyncStatus
    """
    def get_global_folder_status(self, job_id):
        request_url = '{0}/v2/content/folders/global/{1}/status'.format(
            self.__endpoint,
            job_id
        )
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url
        )


    """ Global folder job result.
    Get results from global folder job for the given job identifier.

    Method: GET
    Path:   /v2/content/folders/global/{job_id}/result
    https://api.au.sumologic.com/docs/#operation/getGlobalFolderAsyncResult
    """
    def get_global_folder_result(self, job_id):
        request_url = '{0}/v2/content/folders/global/{1}/result'.format(
            self.__endpoint,
            job_id
        )
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url
        )


    """ Get Admin Recommended folder.
    Schedule an asynchronous job to get the top-level Admin Recommended content items.

    Method: GET
    Path:   /v2/content/folders/adminRecommended
    https://api.au.sumologic.com/docs/#operation/getAdminRecommendedFolderAsync
    """
    def get_admin_recommended_folder_job(self, is_admin_mode=None):
        request_url = '{0}/v2/content/folders/adminRecommended'.format(
            self.__endpoint
        )
        additional_headers = {}
        if is_admin_mode is not None:
            additional_headers['isAdminMode'] = str(is_admin_mode).lower()
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url,
            additional_headers  = additional_headers
        )


    """ Admin Recommended folder job status.
    Get the status of an asynchronous Admin Recommended folder job for the given job identifier.

    Method: GET
    Path:   /v2/content/folders/adminRecommended/{job_id}/status
    https://api.au.sumologic.com/docs/#operation/getAdminRecommendedFolderAsyncStatus
    """
    def get_admin_recommended_folder_status(self, job_id):
        request_url = '{0}/v2/content/folders/adminRecommended/{1}/status'.format(
            self.__endpoint,
            job_id
        )
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url
        )


    """ Admin Recommended folder job result.
    Get results from Admin Recommended job for the given job identifier.

    Method: GET
    Path:   /v2/content/folders/adminRecommended/{job_id}/result
    https://api.au.sumologic.com/docs/#operation/getAdminRecommendedFolderAsyncResult
    """
    def get_admin_recommended_folder_result(self, job_id):
        request_url = '{0}/v2/content/folders/adminRecommended/{1}/result'.format(
            self.__endpoint,
            job_id
        )
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url
        )



    # # #   ==================================================
    # # #   ----[BETA]----------------------------------------
    # # #   LOOKUP TABLE MANAGEMENT API
    # # #   https://api.au.sumologic.com/docs/#tag/lookupManagement
    # # #
    # # #   A Lookup Table is a table of data hosted on Sumo Logic that you can use to enrich the log and event data
    # # #   received by Sumo Logic and Cloud SIEM. You must create a table schema before you can populate the table.
    # # #   You can update and remove Lookup Tables using a Cloud SIEM rule. For more information see
    # # #   https://help.sumologic.com/?cid=10109.
    # # #
    # # #   This API is in private beta and is not available until given access. To participate in the beta program
    # # #   contact your Sumo Logic account representative.

    # # #
    # # #   TODO: Implement checking of parsed values VS documentation.
    # # #
    """ Create a lookup table.
    Create a new lookup table by providing a schema and specifying its configuration. Providing either
    parent_folder_id or contentPath is mandatory. If both parent_folder_id and contentPath are provided and point to
    different paths in the Library, the parent_folder_id is given preference.

    Method: POST
    Path:   /v1/lookupTables
    https://api.au.sumologic.com/docs/#operation/createTable
    """
    def create_lookup_table(self, name, description, parent_folder_id, fields, primary_keys, ttl=None, secondary_keys=None, size_limit_action=None):
        request_url = '{0}/v1/lookupTables'.format(
            self.__endpoint
        )
        request_data = {
            'name': name,
            'description': description,
            'parentFolderId': parent_folder_id,
            'fields': fields,
            'primaryKeys': primary_keys
        }
        if ttl is not None:
            request_data['ttl'] = ttl
        if size_limit_action is not None:
            request_data['sizeLimitAction'] = size_limit_action
        if secondary_keys is not None:
            request_data['secondaryKeys'] = secondary_keys
        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url,
            request_data        = request_data
        )


    """ Get a lookup table.
    Get a lookup table for the given identifier.

    Method: GET
    Path:   /v1/lookupTables/{lookup_table_id}
    https://api.au.sumologic.com/docs/#operation/lookupTableById
    """
    def get_lookup_table(self, lookup_table_id):
        request_url = '{0}/v1/lookupTables/{1}'.format(
            self.__endpoint,
            lookup_table_id
        )
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url
        )


    # # #
    # # #   TODO: Implement checking of parsed values VS documentation.
    # # #
    """ Edit a lookup table.
    Edit the lookup table data. All the fields are mandatory in the request.

    Method: PUT
    Path:   /v1/lookupTables/{lookup_table_id}
    https://api.au.sumologic.com/docs/#operation/updateTable
    """
    def update_lookup_table(self, lookup_table_id, description, ttl, size_limit_action=None):
        request_url = '{0}/v1/lookupTables/{1}'.format(
            self.__endpoint,
            lookup_table_id
        )
        request_data = {
            'description': description,
            'ttl': ttl
        }
        if size_limit_action is not None:
            request_data['sizeLimitAction'] = size_limit_action
        return self.__execute_api(
            request_type        = 'PUT',
            request_url         = request_url,
            request_data        = request_data
        )


    """Delete a lookup table.
    Delete a lookup table completely.

    Method: DELETE
    Path:   /v1/lookupTables/{lookup_table_id}
    https://api.au.sumologic.com/docs/#operation/deleteTable
    """
    def delete_lookup_table(self, lookup_table_id):
        request_url = '{0}/v1/lookupTables/{1}'.format(
            self.__endpoint,
            lookup_table_id
        )
        return self.__execute_api(
            request_type        = 'DELETE',
            request_url         = request_url
        )


    """ Upload a CSV file.
    Create a request to populate a lookup table with a CSV file.

    Method: POST
    Path:   /v1/lookupTables/{lookup_table_id}/upload
    https://api.au.sumologic.com/docs/#operation/uploadFile
    """
    def upload_lookup_table_csv(self, lookup_table_id, csv_file, merge=False, file_encoding=None):
        request_url = '{0}/v1/lookupTables/{1}/upload'.format(
            self.__endpoint,
            lookup_table_id
        )
        request_params = {}
        if merge is not None:
            request_params['merge'] = merge
        if file_encoding is not None:
            request_params['fileEncoding'] = file_encoding
        request_data = {
            'file': csv_file
        }
        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url,
            request_params      = request_params,
            request_data        = request_data
        )


    """ Get the status of an async job.
    Retrieve the status of a previously made request. If the request was successful, the status of the response object
    will be Success.

    Method: GET
    Path:   /v1/lookupTables/jobs/{job_id}/status
    https://api.au.sumologic.com/docs/#operation/requestJobStatus
    """
    def get_lookup_table_upload_status(self, job_id):
        request_url = '{0}/v1/lookupTables/jobs/{1}/status'.format(
            self.__endpoint,
            job_id
        )
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url
        )


    """ Empty a lookup table.
    Delete all data from a lookup table.

    Method: POST
    Path:   /v1/lookupTables/{lookup_table_id}/truncate
    https://api.au.sumologic.com/docs/#operation/truncateTable
    """
    def truncate_lookup_table(self, lookup_table_id):
        request_url = '{0}/v1/lookupTables/{1}/truncate'.format(
            self.__endpoint,
            lookup_table_id
        )
        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url
        )


    # # #
    # # #   TODO: Implement checking of parsed array VS documentation.
    # # #
    """ Insert or Update a lookup table row.
    Insert or update a row of a lookup table with the given identifier. A new row is inserted if the primary key does
    not exist already, otherwise the existing row with the specified primary key is updated. All the fields of the
    lookup table are required and will be updated to the given values. In case a field is not specified then it will
    be assumed to be set to null. If the table size exceeds the maximum limit of 100MB then based on the size limit
    action of the table the update will be processed or discarded.

    Method: PUT
    Path:   /v1/lookupTables/{lookup_table_id}/row
    https://api.au.sumologic.com/docs/#operation/updateTableRow
    """
    def update_table_row(self, lookup_table_id, row):
        request_url = '{0}/v1/lookupTables/{1}/truncate'.format(
            self.__endpoint,
            lookup_table_id
        )
        request_data = {
            'row': row
        }
        return self.__execute_api(
            request_type        = 'PUT',
            request_url         = request_url,
            request_data        = request_data
        )


    """ Add secondary keys
    Add new secondary keys to existing lookup table.

    Method: POST
    Path:   /v1/lookupTables/{lookup_table_id}/secondaryKeys
    https://api.au.sumologic.com/docs/#operation/addSecondaryKeys
    """
    def add_secondary_keys(self, lookup_table_id, secondary_keys):
        request_url = '{0}/v1/lookupTables/{1}/secondaryKeys'.format(
            self.__endpoint,
            lookup_table_id
        )
        request_data = {
            'secondaryKeys': secondary_keys
        }
        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url,
            request_data        = request_data
        )


    """ Delete Secondary Keys
    Deleted Secondary Keys from existing lookup table.

    Method: DELETE
    Path:   /v1/lookupTables/{lookup_table_id}/secondaryKeys
    https://api.au.sumologic.com/docs/#operation/addSecondaryKeys
    """
    def delete_secondary_keys(self, lookup_table_id, secondary_keys):
        request_url = '{0}/v1/lookupTables/{1}/secondaryKeys'.format(
            self.__endpoint,
            lookup_table_id
        )
        request_data = {
            'secondaryKeys': secondary_keys
        }
        return self.__execute_api(
            request_type        = 'DELETE',
            request_url         = request_url,
            request_data        = request_data
        )



    # # #   ==================================================
    # # #   ----[BETA]----------------------------------------
    # # #   METRICS ALERT MONITOR MANAGEMENT API
    # # #   https://api.au.sumologic.com/docs/#tag/metricsAlertMonitorManagement
    # # #
    # # #   Alert Monitors allow you to monitor a time series and alert when the metric has crossed a static threshold
    # # #   by sending an email or webhook notification. For more information see
    # # #   https://help.sumologic.com/?cid=8002.
    # # #
    # # #   This API is in private beta and is not available until access is granted. Contact your Sumo Logic account
    # # #   representative to participate in the beta program.

    """ Get a list of metrics monitors.
    Get a list of all metrics monitors in the organization. The response is paginated with a default limit of 100
    monitors per page.

    Method: GET
    Path:   /v1/metricsAlertMonitors
    https://api.au.sumologic.com/docs/#operation/getMonitors
    """
    def get_monitors(self, limit=None, token=None):
        request_url = '{0}/v1/metricsAlertMonitors'.format(
            self.__endpoint
        )
        request_params = {}
        if limit is not None:
            request_params['limit'] = limit
        if token is not None:
            request_params['token'] = token
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url,
            request_params      = request_params
        )


    # # #
    # # #   TODO: Implement checking of parsed array VS documentation.
    # # #
    """ Create a new metrics monitor.
    Create a new metrics monitor.

    Method: POST
    Path:   /v1/metricsAlertMonitors
    https://api.au.sumologic.com/docs/#operation/createMonitor
    """
    def create_monitor(self, request_data):
        request_url = '{0}/v1/metricsAlertMonitors'.format(
            self.__endpoint
        )
        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url,
            request_data        = request_data
        )


    """ Get a metrics monitor.
    Get a metrics monitor with the given identifier.

    Method: GET
    Path:   /v1/metricsAlertMonitors/{monitor_id}
    https://api.au.sumologic.com/docs/#operation/getMonitor
    """
    def get_monitor(self, monitor_id):
        request_url = '{0}/v1/metricsAlertMonitors/{1}'.format(
            self.__endpoint,
            monitor_id
        )
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url
        )


    """ Update a metrics monitor.
    Update an existing metrics monitor.

    Method: PUT
    Path:   /v1/metricsAlertMonitors/{monitor_id}
    https://api.au.sumologic.com/docs/#operation/updateMonitor
    """
    def update_monitor(self, monitor_id, request_data):
        request_url = '{0}/v1/metricsAlertMonitors/{1}'.format(
            self.__endpoint,
            monitor_id
        )
        return self.__execute_api(
            request_type        = 'PUT',
            request_url         = request_url,
            request_data        = request_data
        )


    """ Delete a metrics monitor.
    Delete an existing metrics monitor.

    Method: DELETE
    Path:   /v1/metricsAlertMonitors/{monitor_id}
    https://api.au.sumologic.com/docs/#operation/deleteMonitor
    """
    def delete_monitor(self, monitor_id):
        request_url = '{0}/v1/metricsAlertMonitors/{1}'.format(
            self.__endpoint,
            monitor_id
        )
        return self.__execute_api(
            request_type        = 'DELETE',
            request_url         = request_url
        )


    """ Mute a metrics monitor.
    Mute a metrics monitor.

    Method: POST
    Path:   /v1/metricsAlertMonitors/{monitor_id}/mute
    https://api.au.sumologic.com/docs/#operation/mute
    """
    def mute_monitor(self, monitor_id, mute_until):
        request_url = '{0}/v1/metricsAlertMonitors/{1}/mute'.format(
            self.__endpoint,
            monitor_id
        )
        request_data = {
            'muteUntil': mute_until
        }
        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url,
            request_data        = request_data
        )


    """ Unmute a metrics monitor.
    Unmute a metrics monitor.

    Method: POST
    Path:   /v1/metricsAlertMonitors/{monitor_id}/unmute
    https://api.au.sumologic.com/docs/#operation/unmute
    """
    def unmute_monitor(self, monitor_id):
        request_url = '{0}/v1/metricsAlertMonitors/{1}/unmute'.format(
            self.__endpoint,
            monitor_id
        )
        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url
        )



    # # #   ==================================================
    # # #   ----[BETA]----------------------------------------
    # # #   METRICS SEARCH MANAGEMENT API
    # # #   https://api.au.sumologic.com/docs/#tag/metricsSearchesManagement
    # # #
    # # #   Save metrics searches in the content library and organize them in a folder hierarchy. Share useful queries
    # # #   with users in your organization. For more information see
    # # #   https://help.sumologic.com/Metrics/03-Metric-Charts/Share_a_Metric_Chart.

    # # #
    # # #   TODO: Implement checking of parsed JSON structures VS documentation.
    # # #
    """ Save a metrics search.
    Saves a metrics search in the content library. Metrics search consists of one or more queries, a time range, a
    quantization period and a set of chart properties like line width.

    Method: POST
    Path:   /v1/metricsSearches
    https://api.au.sumologic.com/docs/#operation/createMetricsSearch
    """
    def create_metrics_search(self, request_data):
        request_url = '{0}/v1/metricsSearches'.format(
            self.__endpoint
        )
        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url,
            request_data        = request_data
        )


    """ Get a metrics search.
    Returns a metrics search with the specified identifier.

    Method: GET
    Path:   /v1/metricsSearches/{search_id}
    https://api.au.sumologic.com/docs/#operation/getMetricsSearch
    """
    def get_metrics_search(self, search_id):
        request_url = '{0}/v1/metricsSearches/{1}'.format(
            self.__endpoint,
            search_id
        )
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url
        )


    """ Updates a metrics search.
    Updates a metrics search with the specified identifier. Partial updates are not supported, you must provide
    values for all fields.

    Method: PUT
    Path:   /v1/metricsSearches/{search_id}
    https://api.au.sumologic.com/docs/#operation/updateMetricsSearch
    """
    def update_metrics_search(self, search_id, request_data):
        request_url = '{0}/v1/metricsSearches/{1}'.format(
            self.__endpoint,
            search_id
        )
        return self.__execute_api(
            request_type        = 'PUT',
            request_url         = request_url,
            request_data        = request_data
        )


    """ Deletes a metrics search.
    Deletes a metrics search from the content library.

    Method: DELETE
    Path:   /v1/metricsSearches/{search_id}
    https://api.au.sumologic.com/docs/#operation/deleteMetricsSearch
    """
    def delete_metrics_search(self, search_id):
        request_url = '{0}/v1/metricsSearches/{1}'.format(
            self.__endpoint,
            search_id
        )
        return self.__execute_api(
            request_type        = 'DELETE',
            request_url         = request_url
        )



    # # #   ==================================================
    # # #   ----[BETA]----------------------------------------
    # # #   TRANSFORMATION RULE MANAGEMENT API
    # # #   https://api.au.sumologic.com/docs/#tag/transformationRuleManagement
    # # #
    # # #   Transformation Rule management API. Metrics Transformation Rules allow you control how long raw metrics
    # # #   are retained. You can also aggregate metrics at collection time and specify a separate retention period
    # # #   for the aggregated metrics. For more information see https://help.sumologic.com/?cid=10117.

    """ Get a list of transformation rules.
    Get a list of transformation rules in the organization. The response is paginated with a default limit of 100
    rules per page.

    Method: GET
    Path:   /v1/transformationRules
    https://api.au.sumologic.com/docs/#operation/getTransformationRules
    """
    def get_transformation_rules(self, limit=None, token=None):
        request_url = '{0}/v1/transformationRules'.format(
            self.__endpoint
        )
        request_params = {}
        if limit is not None:
            request_params['limit'] = limit
        if token is not None:
            request_params['token'] = token
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url,
            request_params      = request_params
        )


    # # #
    # # #   TODO: Implement checking of parsed JSON structures VS documentation.
    # # #
    """ Create a new transformation rule.
    Create a new transformation rule.

    Method: POST
    Path:   /v1/transformationRules
    https://api.au.sumologic.com/docs/#operation/createRule
    """
    def create_transformation_rule(self, request_data):
        request_url = '{0}/v1/transformationRules'.format(
            self.__endpoint
        )
        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url,
            request_data        = request_data
        )


    """ Get a transformation rule.
    Get a transformation rule with the given identifier.

    Method: GET
    Path:   /v1/transformationRules/{rule_id}
    https://api.au.sumologic.com/docs/#operation/getTransformationRule
    """
    def get_transformation_rule(self, rule_id):
        request_url = '{0}/v1/transformationRules/{1}'.format(
            self.__endpoint,
            rule_id
        )
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url
        )


    # # #
    # # #   TODO: Implement checking of parsed JSON structures VS documentation.
    # # #
    """ Update a transformation rule.
    Update an existing transformation rule. All properties specified in the request are replaced. Missing properties
    will remain the same.

    Method: PUT
    Path:  /v1/transformationRules/{rule_id}
    https://api.au.sumologic.com/docs/#operation/updateTransformationRule
    """
    def update_transformation_rule(self, rule_id, request_data):
        request_url = '{0}/v1/transformationRules/{1}'.format(
            self.__endpoint,
            rule_id
        )
        return self.__execute_api(
            request_type        = 'PUT',
            request_url         = request_url,
            request_data        = request_data
        )


    """ Delete a transformation rule.
    Delete a transformation rule with the given identifier.

    Method: DELETE
    Path:   /v1/transformationRules/{rule_id}
    https://api.au.sumologic.com/docs/#operation/deleteRule
    """
    def delete_transformation_rule(self, rule_id):
        request_url = '{0}/v1/transformationRules/{1}'.format(
            self.__endpoint,
            rule_id
        )
        return self.__execute_api(
            request_type        = 'DELETE',
            request_url         = request_url
        )



    # # #   ==================================================
    # # #
    # # #   ACCESS KEY MANAGEMENT API
    # # #   https://api.au.sumologic.com/docs/#tag/accessKeyManagement
    # # #
    # # #   Access Keys allow you to securely register new Collectors and access Sumo Logic APIs. For more information
    # # #   see https://help.sumologic.com/?cid=6690.

    """ List all access keys.
    List all access keys in your account.

    Method: GET
    Path:   /v1/accessKeys
    https://api.au.sumologic.com/docs/#operation/listAccessKeys
    """
    def list_access_keys(self, limit=None, token=None):
        request_url = '{0}/v1/accessKeys'.format(
            self.__endpoint
        )
        request_params = {}
        if limit is not None:
            request_params['limit'] = limit
        if token is not None:
            request_params['token'] = token
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url,
            request_params      = request_params
        )


    # # #
    # # #   TODO: Implement checking of parsed JSON structures VS documentation.
    # # #
    """ Create an access key.
    Creates a new access ID and key pair. The new access key can be used from the domains specified in corsHeaders
    field. Whether Sumo Logic accepts or rejects an API request depends on whether it contains an ORIGIN header and
    the entries in the whitelist. Sumo Logic will reject:

        1. Requests with an ORIGIN header but the whitelist is empty.
        2. Requests with an ORIGIN header that don't match any entry in the whitelist.

    Method: POST
    Path:   /v1/accessKeys
    https://api.au.sumologic.com/docs/#operation/createAccessKey
    """
    def create_access_key(self, request_data):
        request_url = '{0}/v1/accessKeys'.format(
            self.__endpoint
        )
        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url,
            request_data        = request_data
        )


    """ List personal keys.
    List all access keys that belong to your user.

    Method: GET
    Path:   /v1/accessKeys/personal
    https://api.au.sumologic.com/docs/#operation/listPersonalAccessKeys
    """
    def list_personal_keys(self):
        request_url = '{0}/v1/accessKeys/personal'.format(
            self.__endpoint
        )
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url
        )


    # # #
    # # #   TODO: Implement checking of parsed JSON structures VS documentation.
    # # #
    """ Update an access key.
    Updates the properties of existing accessKey by accessId. It can be used to enable or disable the access key and
    to update the corsHeaders list.

    Method: PUT
    Path:   /v1/accessKeys/{access_id}
    https://api.au.sumologic.com/docs/#operation/updateAccessKey
    """
    def update_access_key(self, access_id, request_data):
        request_url = '{0}/v1/accessKeys/{1}'.format(
            self.__endpoint,
            access_id
        )
        return self.__execute_api(
            request_type        = 'PUT',
            request_url         = request_url,
            request_data        = request_data
        )


    """ Delete an access key.
    Deletes the access key with the given accessId.

    Method: DELETE
    Path:   /v1/accessKeys/{id}
    https://api.au.sumologic.com/docs/#operation/deleteAccessKey
    """
    def delete_access_key(self, access_id):
        request_url = '{0}/v1/accessKeys/{1}'.format(
            self.__endpoint,
            access_id
        )
        return self.__execute_api(
            request_type        = 'DELETE',
            request_url         = request_url
        )



    # # #   ==================================================
    # # #
    # # #   SAML CONFIGURATION MANAGEMENT API
    # # #   https://api.au.sumologic.com/docs/#tag/samlConfigurationManagement
    # # #
    # # #   Organizations with Enterprise accounts can provision Security Assertion Markup Language (SAML) 2.0 to
    # # #   enable Single Sign-On (SSO) for user access to Sumo Logic. For more information see
    # # #   https://help.sumologic.com/?cid=4016.

    """ Get a list of SAML configurations.
    Get a list of all SAML configurations in the organization.

    Method: GET
    Path:   /v1/saml/identityProviders
    https://api.au.sumologic.com/docs/#operation/getIdentityProviders
    """
    def get_identity_providers(self):
        request_url = '{0}/v1/saml/identityProviders'.format(
            self.__endpoint
        )
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url
        )


    # # #
    # # #   TODO: Implement checking of parsed JSON structures VS documentation.
    # # #
    """ Create a new SAML configuration.
    Create a new SAML configuration in the organization.

    Method: POST
    Path:   /v1/saml/identityProviders
    https://api.au.sumologic.com/docs/#operation/createIdentityProvider
    """
    def create_identity_provider(self, request_data):
        request_url = '{0}/v1/saml/identityProviders'.format(
            self.__endpoint
        )
        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url,
            request_data        = request_data
        )


    # # #
    # # #   TODO: Implement checking of parsed JSON structures VS documentation.
    # # #
    """ Update a SAML configuration.
    Update an existing SAML configuration in the organization.

    Method: PUT
    Path:   /v1/saml/identityProviders/{saml_id}
    https://api.au.sumologic.com/docs/#operation/updateIdentityProvider
    """
    def update_identity_provider(self, saml_id, request_data):
        request_url = '{0}/v1/saml/identityProviders/{1}'.format(
            self.__endpoint,
            saml_id
        )
        return self.__execute_api(
            request_type        = 'PUT',
            request_url         = request_url,
            request_data        = request_data
        )


    """ Delete a SAML configuration.
    Delete a SAML configuration with the given identifier from the organization.

    Method: DELETE
    Path:   /v1/saml/identityProviders/{saml_id}
    https://api.au.sumologic.com/docs/#operation/deleteIdentityProvider
    """
    def delete_identity_provider(self, saml_id):
        request_url = '{0}/v1/saml/identityProviders/{1}'.format(
            self.__endpoint,
            saml_id
        )
        return self.__execute_api(
            request_type        = 'DELETE',
            request_url         = request_url
        )


    """ Get list of whitelisted users.
    Get a list of whitelisted users.

    Method: GET
    Path:   /v1/saml/whitelistedUsers
    https://api.au.sumologic.com/docs/#operation/getWhitelistedUsers
    """
    def get_whitelisted_users(self):
        request_url = '{0}/v1/saml/whitelistedUsers'.format(
            self.__endpoint
        )
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url
        )


    """ Whitelist a user.
    Whitelist a user from SAML lockdown allowing them to sign in using a password in addition to SAML.

    Method: POST
    Path:   /v1/saml/whitelistedUsers/{user_id}
    https://api.au.sumologic.com/docs/#operation/createWhitelistedUser
    """
    def create_whitelisted_user(self, user_id):
        request_url = '{0}/v1/saml/whitelistedUsers/{1}'.format(
            self.__endpoint,
            user_id
        )
        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url
        )


    """ Remove a whitelisted user.
    Remove a whitelisted user requiring them to sign in using SAML.

    Method: DELETE
    Path:   /v1/saml/whitelistedUsers/{user_id}
    https://api.au.sumologic.com/docs/#operation/deleteWhitelistedUser
    """
    def delete_whitelisted_user(self, user_id):
        request_url = '{0}/v1/saml/whitelistedUsers/{1}'.format(
            self.__endpoint,
            user_id
        )
        return self.__execute_api(
            request_type        = 'DELETE',
            request_url         = request_url
        )


    """ Require SAML for sign-in.
    Enabling SAML lockdown requires users to sign in using SAML preventing them from logging in with an email and
    password.

    Method: POST
    Path:   /v1/saml/lockdown/enable
    https://api.au.sumologic.com/docs/#operation/enableSamlLockdown
    """
    def enable_saml_lockdown(self):
        request_url = '{0}/v1/saml/lockdown/enable'.format(
            self.__endpoint
        )
        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url
        )


    """ Disable SAML lockdown.
    Disable SAML lockdown for the organization.

    Method: POST
    Path:   /v1/saml/lockdown/disable
    https://api.au.sumologic.com/docs/#operation/disableSamlLockdown
    """
    def disable_saml_lockdown(self):
        request_url = '{0}/v1/saml/lockdown/disable'.format(
            self.__endpoint
        )
        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url
        )



    # # #   ==================================================
    # # #
    # # #   SERVICE WHITELIST MANAGEMENT API
    # # #   https://api.au.sumologic.com/docs/#tag/serviceWhitelistManagement
    # # #
    # # #   Service Whitelist Settings allow you to explicitly grant access to specific IP addresses and/or CIDR
    # # #   notations for logins, APIs, and dashboard access. For more information see
    # # #   https://help.sumologic.com/?cid=5454.

    """ List all whitelisted CIDRs/IP addresses.
    Get a list of all whitelisted CIDR notations and/or IP addresses for the organization.

    Method: GET
    Path:   /v1/serviceWhitelist/addresses
    https://api.au.sumologic.com/docs/#operation/listWhitelistedCidrs
    """
    def list_whitelisted_cidrs(self):
        request_url = '{0}/v1/serviceWhitelist/addresses'.format(
            self.__endpoint
        )
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url
        )


    # # #
    # # #   TODO: Implement checking of parsed JSON structures VS documentation.
    # # #
    """ Whitelist CIDRs/IP addresses.
    Add CIDR notations and/or IP addresses to the whitelist of the organization if not already there. When service
    whitelisting functionality is enabled, CIDRs/IP addresses that are whitelisted will have access to Sumo Logic
    and/or content sharing.

    Method: POST
    Path:   /v1/serviceWhitelist/addresses/add
    https://api.au.sumologic.com/docs/#operation/addWhitelistedCidrs
    """
    def add_whitelisted_cidrs(self, request_data):
        request_url = '{0}/v1/serviceWhitelist/addresses/add'.format(
            self.__endpoint
        )
        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url,
            request_data        = request_data
        )


    """ Remove whitelisted CIDRs/IP addresses.
    Remove whitelisted CIDR notations and/or IP addresses from the organization. Removed CIDRs/IPs will immediately
    lose access to Sumo Logic and content sharing.

    Method: POST
    Path:   /v1/serviceWhitelist/addresses/remove
    https://api.au.sumologic.com/docs/#operation/deleteWhitelistedCidrs
    """
    def remove_whitelisted_cidrs(self, request_data):
        request_url = '{0}/v1/serviceWhitelist/addresses/remove'.format(
            self.__endpoint
        )
        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url,
            request_data        = request_data
        )


    """ Enable service whitelisting.
    Enable service whitelisting functionality for the organization. The service whitelisting can be for 1. Login: If
    enabled, access to Sumo Logic is granted only to CIDRs/IP addresses that are whitelisted. 2. Content: If enabled,
    dashboards can be shared with users connecting from CIDRs/IP addresses that are whitelisted without logging in.

    Method: POST
    Path:   /v1/serviceWhitelist/enable
    https://api.au.sumologic.com/docs/#operation/enableWhitelisting
    """
    def enable_whitelisting(self, whitelist_type):
        request_url = '{0}/v1/serviceWhitelist/enable'.format(
            self.__endpoint
        )

        # There are a specific set of whitelist types that can be executed.
        valid_types = ['Login', 'Content', 'Both']
        if whitelist_type not in valid_types:
            raise ValueError('enable_whitelisting: whitelist_type must be one of {0}.'.format(valid_types))

        request_params = {
            'whitelistType': whitelist_type
        }

        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url,
            request_params      = request_params
        )
        

    """ Disable service whitelisting.
    Disable service whitelisting functionality for login/API authentication or content sharing for the organization.

    Method: POST
    Path:   /v1/serviceWhitelist/disable
    https://api.au.sumologic.com/docs/#operation/disableWhitelisting
    """
    def disable_whitelisting(self, whitelist_type):
        request_url = '{0}/v1/serviceWhitelist/disable'.format(
            self.__endpoint
        )

        # There are a specific set of whitelist types that can be executed.
        valid_types = ['Login', 'Content', 'Both']
        if whitelist_type not in valid_types:
            raise ValueError('disable_whitelisting: whitelist_type must be one of {0}.'.format(valid_types))

        request_params = {
            'whitelistType': whitelist_type
        }

        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url,
            request_params      = request_params
        )


    """ Get the whitelisting status.
    Get the status of the service whitelisting functionality for login/API authentication or content sharing for the
    organization.

    Method: GET
    Post: /v1/serviceWhitelist/status
    https://api.au.sumologic.com/docs/#operation/getWhitelistingStatus
    """
    def get_whitelisting_status(self):
        request_url = '{0}/v1/serviceWhitelist/status'.format(
            self.__endpoint
        )
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url
        )



    # # #   ==================================================
    # # #   ----[BETA]----------------------------------------
    # # #   CONNECTION MANAGEMENT API
    # # #   https://api.au.sumologic.com/docs/#tag/connectionManagement
    # # #
    # # #   Set up connections to send alerts to other tools. For more information see
    # # #   https://help.sumologic.com/?cid=1044.

    """ Get a list of connections.
    Get a list of all connections in the organization. The response is paginated with a default limit of 100 connections per page.

    Method: GET
    Path:   /v1/connections
    https://api.au.sumologic.com/docs/#operation/listConnections
    """
    def list_connections(self, limit=None, token=None):
        request_url = '{0}/v1/connections'.format(
            self.__endpoint
        )
        request_params = {}
        if limit is not None:
            request_params['limit'] = limit
        if token is not None:
            request_params['token'] = token
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url,
            request_params      = request_params
        )


    """ Create a new connection.
    Create a new connection in the organization.

    Method: POST
    Path:   /v1/connections
    https://api.au.sumologic.com/docs/#operation/createConnection
    """
    def create_connection(self, request_data):
        request_url = '{0}/v1/connections'.format(
            self.__endpoint
        )
        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url,
            request_data        = request_data
        )


    """ Test a new connection url.
    Test a new connection url is valid and can connect.

    Method: POST
    Path:   /v1/connections/test
    https://api.au.sumologic.com/docs/#operation/testConnection
    """
    def test_connection(self, request_data):
        request_url = '{0}/v1/connections/test'.format(
            self.__endpoint
        )
        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url,
            request_data        = request_data
        )


    """ Get a connection.
    Get a connection with the given identifier.

    Method: GET
    Path:   /v1/connections/{connection_id}
    https://api.au.sumologic.com/docs/#operation/getConnection
    """
    def get_connection(self, connection_id, connection_type):
        request_url = '{0}/v1/connections/{1}'.format(
            self.__endpoint,
            connection_id
        )

        # There are a specific set of whitelist types that can be executed.
        valid_types = ['Login', 'Content', 'Both']
        if connection_type not in valid_types:
            raise ValueError('get_connection: connection_type must be one of {0}.'.format(valid_types))

        request_params = {
            'type': connection_type
        }
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url,
            request_params      = request_params
        )


    # # #
    # # #   TODO: Implement checking of parsed JSON structures VS documentation.
    # # #
    """ Update a connection.
    Update an existing connection.

    Method: PUT
    Path:   /v1/connections/{connection_id}
    https://api.au.sumologic.com/docs/#operation/updateConnection
    """
    def update_connection(self, connection_id, request_data):
        request_url = '{0}/v1/connections/{1}'.format(
            self.__endpoint,
            connection_id
        )
        return self.__execute_api(
            request_type        = 'PUT',
            request_url         = request_url,
            request_data        = request_data
        )


    """ Delete a connection.
    Delete a connection with the given identifier.

    Method: DELETE
    Path:   /v1/connections/{id}
    https://api.au.sumologic.com/docs/#operation/deleteConnection
    """
    def delete_connection(self, connection_id, connection_type):
        request_url = '{0}/v1/connections/{1}'.format(
            self.__endpoint,
            connection_id
        )

        # There are a specific set of whitelist types that can be executed.
        valid_types = ['Login', 'Content', 'Both']
        if connection_type not in valid_types:
            raise ValueError('get_connection: connection_type must be one of {0}.'.format(valid_types))

        request_params = {
            'type': connection_type
        }
        return self.__execute_api(
            request_type        = 'DELETE',
            request_url         = request_url,
            request_params      = request_params
        )



    # # #   ==================================================
    # # #   ----[BETA]----------------------------------------
    # # #   FIELD EXTRACTION RULE MANAGEMENT API
    # # #   https://api.au.sumologic.com/docs/#tag/extractionRuleManagement
    # # #
    # # #   Field Extraction Rules allow you to parse fields from your log messages at the time the messages are
    # # #   ingested eliminating the need to parse fields in your query. For more information see
    # # #   https://help.sumologic.com/?cid=5313.

    """ Get a list of field extraction rules.
    Get a list of all field extraction rules. The response is paginated with a default limit of 100 field extraction
    rules per page.

    Method: GET
    Path:   /v1/extractionRules
    https://api.au.sumologic.com/docs/#operation/listExtractionRules
    """
    def list_extraction_rules(self, limit=None, token=None):
        request_url = '{0}/v1/extractionRules'.format(
            self.__endpoint
        )
        request_params = {}
        if limit is not None:
            request_params['limit'] = limit
        if token is not None:
            request_params['token'] = token
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url,
            request_params      = request_params
        )


    # # #
    # # #   TODO: Implement checking of parsed JSON structures VS documentation.
    # # #
    """ Create a new field extraction rule.
    Create a new field extraction rule.

    Method: POST
    Path:   /v1/extractionRules
    https://api.au.sumologic.com/docs/#operation/createExtractionRule
    """
    def create_extraction_rule(self, request_data):
        request_url = '{0}/v1/extractionRules'.format(
            self.__endpoint
        )
        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url,
            request_data        = request_data
        )


    """ Get a field extraction rule.
    Get a field extraction rule with the given identifier.

    Method: GET
    Path:   /v1/extractionRules/{rule_id}
    https://api.au.sumologic.com/docs/#operation/getExtractionRule
    """
    def get_extraction_rule(self, rule_id):
        request_url = '{0}/v1/extractionRules/{1}'.format(
            self.__endpoint,
            rule_id
        )
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url
        )


    """ Update a field extraction rule.
    Update an existing field extraction rule. All properties specified in the request are replaced. Missing properties
    are set to their default values.

    Method: PUT
    Path:   /v1/extractionRules/{rule_id}
    https://api.au.sumologic.com/docs/#operation/updateExtractionRule
    """
    def update_extraction_rule(self, rule_id, request_data):
        request_url = '{0}/v1/extractionRules/{1}'.format(
            self.__endpoint,
            rule_id
        )
        return self.__execute_api(
            request_type        = 'PUT',
            request_url         = request_url,
            request_data        = request_data
        )


    """ Delete a field extraction rule.
    Delete a field extraction rule with the given identifier.

    Method: DELETE
    Path:   /v1/extractionRules/{rule_id}
    https://api.au.sumologic.com/docs/#operation/deleteExtractionRule
    """
    def delete_extraction_rule(self, rule_id):
        request_url = '{0}/v1/extractionRules/{1}'.format(
            self.__endpoint,
            rule_id
        )
        return self.__execute_api(
            request_type        = 'DELETE',
            request_url         = request_url
        )



    # # #   ==================================================
    # # #
    # # #   FIELD MANAGEMENT API
    # # #   https://api.au.sumologic.com/docs/#tag/fieldManagementV1
    # # #
    # # #   Fields allow you to reference log data based on meaningful associations. They act as metadata tags that
    # # #   are assigned to your logs so you can search with them. Each field contains a key-value pair, where the
    # # #   field name is the key. Fields may be referred to as Log Metadata Fields. For more information see
    # # #   https://help.sumologic.com/?cid=10116.

    """ Get a list of all custom fields.
    Request a list of all the custom fields configured in your account.

    Method: GET
    Path:   /v1/fields
    https://api.au.sumologic.com/docs/#operation/listCustomFields
    """
    def list_customer_fields(self):
        request_url = '{0}/v1/fields'.format(
            self.__endpoint
        )
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url
        )


    # # #
    # # #   TODO: Implement checking of parsed JSON structures VS documentation.
    # # #
    """ Create a new field.
    Adding a field will define it in the Fields schema allowing it to be assigned as metadata to your logs.

    Method: POST
    Path:   /v1/fields
    https://api.au.sumologic.com/docs/#operation/createField
    """
    def create_field(self, field_name):
        request_url = '{0}/v1/fields'.format(
            self.__endpoint
        )
        request_data = {
            'fieldName': field_name
        }
        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url,
            request_data        = request_data
        )


    """ Get a custom field.
    Get the details of a custom field.

    Method: GET
    Path:   /v1/fields/{field_id}
    https://api.au.sumologic.com/docs/#operation/getCustomField
    """
    def get_custom_field(self, field_id):
        request_url = '{0}/v1/fields/{1}'.format(
            self.__endpoint,
            field_id
        )
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url
        )


    """ Delete a custom field.
    Deleting a field does not delete historical data assigned with that field. If you delete a field by mistake and
    one or more of those dependencies break, you can re-add the field to get things working properly again. You should
    always disable a field and ensure things are behaving as expected before deleting a field.

    Method: DELETE
    Path:   /v1/fields/{field_id}
    https://api.au.sumologic.com/docs/#operation/deleteField
    """
    def delete_custom_field(self, field_id):
        request_url = '{0}/v1/fields/{1}'.format(
            self.__endpoint,
            field_id
        )
        return self.__execute_api(
            request_type        = 'DELETE',
            request_url         = request_url
        )


    """ Enable custom field with a specified identifier.
    Fields have to be enabled to be assigned to your data. This operation ensures that a specified field is enabled
    and Sumo Logic will treat it as safe to process. All manually created custom fields are enabled by default.

    Method: PUT
    Path:   /v1/fields/{field_id}/enable
    https://api.au.sumologic.com/docs/#operation/enableField
    """
    def enable_custom_field(self, field_id):
        request_url = '{0}/v1/fields/{1}/enable'.format(
            self.__endpoint,
            field_id
        )
        return self.__execute_api(
            request_type        = 'PUT',
            request_url         = request_url
        )


    """ Disable a custom field.
    After disabling a field Sumo Logic will start dropping its incoming values at ingest. As a result, they won't be
    searchable or usable. Historical values are not removed and remain searchable.

    Method: DELETE
    Path:   /v1/fields/{field_id}/disable
    https://api.au.sumologic.com/docs/#operation/disableField
    """
    def disable_custom_field(self, field_id):
        request_url = '{0}/v1/fields/{1}/disable'.format(
            self.__endpoint,
            field_id
        )
        return self.__execute_api(
            request_type        = 'DELETE',
            request_url         = request_url
        )


    """ Get a list of dropped fields.
    Dropped fields are fields sent to Sumo Logic, but are ignored since they are not defined in your Fields schema. In
    order to save these values a field must both exist and be enabled.

    Method: GET
    Path:   /v1/fields/dropped
    https://api.au.sumologic.com/docs/#operation/listDroppedFields
    """
    def get_dropped_fields(self):
        request_url = '{0}/v1/fields/dropped'.format(
            self.__endpoint
        )
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url
        )


    """ Get a list of built-in fields.
    Built-in fields are created automatically by Sumo Logic for standard configuration purposes. They include
    _sourceHost and _sourceCategory. Built-in fields can't be deleted or disabled.

    Method: GET
    Path:   /v1/fields/builtin
    https://api.au.sumologic.com/docs/#operation/listBuiltInFields
    """
    def get_builtin_fields(self):
        request_url = '{0}/v1/fields/builtin'.format(
            self.__endpoint
        )
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url
        )


    """ Get a built-in field.
    Get the details of a built-in field.

    Method: GET
    Path:   /v1/fields/builtin/{field_id}
    https://api.au.sumologic.com/docs/#operation/getBuiltInField
    """
    def get_builtin_field(self, field_id):
        request_url = '{0}/v1/fields/builtin/{1}'.format(
            self.__endpoint,
            field_id
        )
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url
        )


    """ Get capacity information.
    Every account has a limited number of fields available. This endpoint returns your account limitations and
    remaining quota.

    Method: GET
    Path:   /v1/fields/quota
    https://api.au.sumologic.com/docs/#operation/getFieldQuota
    """
    def get_field_quota(self):
        request_url = '{0}/v1/fields/quota'.format(
            self.__endpoint
        )
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url
        )



    # # #   ==================================================
    # # #   ----[BETA]----------------------------------------
    # # #   PARTITION MANAGEMENT API
    # # #   https://api.au.sumologic.com/docs/#tag/partitionManagement
    # # #
    # # #   Creating a Partition allows you to improve search performance by searching over a smaller number of
    # # #   messages. For more information see https://help.sumologic.com/?cid=5231.

    """ Get a list of partitions.
    Get a list of all partitions in the organization. The response is paginated with a default limit of 100 partitions
    per page.

    Method: GET
    Path:   /v1/partitions
    https://api.au.sumologic.com/docs/#operation/listPartitions
    """
    def list_partitions(self, limit=None, token=None):
        request_url = '{0}/v1/partitions'.format(
            self.__endpoint
        )
        request_params = {}
        if limit is not None:
            request_params['limit'] = limit
        if token is not None:
            request_params['token'] = token
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url,
            request_params      = request_params
        )


    # # #
    # # #   TODO: Implement checking of parsed JSON structures VS documentation.
    # # #
    """ Create a new partition.
    Create a new partition.

    Method: POST
    Path:   /v1/partitions
    https://api.au.sumologic.com/docs/#operation/createPartition
    """
    def create_partition(self, request_data):
        request_url = '{0}/v1/partitions'.format(
            self.__endpoint
        )
        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url,
            request_data        = request_data
        )


    """ Get a partition.
    Get a partition with the given identifier from the organization.

    Method: GET
    Path:   /v1/partitions/{partition_id}
    https://api.au.sumologic.com/docs/#operation/getPartition
    """
    def get_partition(self, partition_id):
        request_url = '{0}/v1/partitions/{1}'.format(
            self.__endpoint,
            partition_id
        )
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url
        )


    # # #
    # # #   TODO: Implement checking of parsed JSON structures VS documentation.
    # # #
    """ Update a partition.
    Update an existing partition in the organization.

    Method: PUT
    Path:   /v1/partitions/{partition_id}
    """
    def update_partition(self, partition_id, request_data):
        request_url = '{0}/v1/partitions/{1}'.format(
            self.__endpoint,
            partition_id
        )
        return self.__execute_api(
            request_type        = 'PUT',
            request_url         = request_url,
            request_data        = request_data
        )


    """ Decommission a partition.
    Decommission a partition with the given identifier from the organization.

    Method: POST
    Path:   /v1/partitions/{partition_id}/decommission
    https://api.au.sumologic.com/docs/#operation/decommissionPartition
    """
    def decommission_partition(self, partition_id):
        request_url = '{0}/v1/partitions/{1}/decommission'.format(
            self.__endpoint,
            partition_id
        )
        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url
        )


    """ Cancel a retention update for a partition
    Cancel update to retention of a partition for which retention was updated previously using
    reduceRetentionPeriodImmediately parameter as false

    Method: POST
    Path:   /v1/partitions/{id}/cancelRetentionUpdate
    https://api.au.sumologic.com/docs/#operation/cancelRetentionUpdate
    """
    def cancel_partition_retention_update(self, partition_id):
        request_url = '{0}/v1/partitions/{1}/cancelRetentionUpdate'.format(
            self.__endpoint,
            partition_id
        )
        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url
        )



    # # #   ==================================================
    # # #
    # # #   SCHEDULED VIEW MANAGEMENT API
    # # #   https://api.au.sumologic.com/docs/#tag/scheduledViewManagement
    # # #
    # # #   Scheduled Views speed the search process for small and historical subsets of your data by functioning as
    # # #   a pre-aggregated index. For more information see https://help.sumologic.com/?cid=5128.

    """ Get a list of scheduled views.
    Get a list of all scheduled views in the organization. The response is paginated with a default limit of 100
    scheduled views per page.

    Method: GET
    Path:   /v1/scheduledViews
    https://api.au.sumologic.com/docs/#operation/listScheduledViews
    """
    def list_scheduled_views(self, limit=None, token=None):
        request_url = '{0}/v1/scheduledViews'.format(
            self.__endpoint
        )
        request_params = {}
        if limit is not None:
            request_params['limit'] = limit
        if token is not None:
            request_params['token'] = token
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url,
            request_params      = request_params
        )


    # # #
    # # #   TODO: Implement checking of parsed JSON structures VS documentation.
    # # #
    """ Create a new scheduled view.
    Creates a new scheduled view in the organization.

    Method: POST
    Path:   /v1/scheduledViews
    https://api.au.sumologic.com/docs/#operation/createScheduledView
    """
    def create_scheduled_views(self, request_data):
        request_url = '{0}/v1/scheduledViews'.format(
            self.__endpoint
        )
        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url,
            request_data        = request_data
        )


    """ Get a scheduled view.
    Get a scheduled view with the given identifier.

    Method: GET
    Path:   /v1/scheduledViews/{scheduled_view_id}
    https://api.au.sumologic.com/docs/#operation/getScheduledView
    """
    def get_scheduled_view(self, scheduled_view_id):
        request_url = '{0}/v1/scheduledViews/{1}'.format(
            self.__endpoint,
            scheduled_view_id
        )
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url
        )


    # # #
    # # #   TODO: Implement checking of parsed JSON structures VS documentation.
    # # #
    """ Update a scheduled view.
    Update an existing scheduled view.

    Method: PUT
    Path:   /v1/scheduledViews/{scheduled_view_id}
    https://api.au.sumologic.com/docs/#operation/updateScheduledView
    """
    def update_scheduled_view(self, scheduled_view_id, request_data):
        request_url = '{0}/v1/scheduledViews/{1}'.format(
            self.__endpoint,
            scheduled_view_id
        )
        return self.__execute_api(
            request_type        = 'PUT',
            request_url         = request_url,
            request_data        = request_data
        )


    """ Disable a scheduled view.
    Disable a scheduled view with the given identifier.

    Method: DELETE
    Path:   /v1/scheduledViews/{scheduled_view_id}/disable
    https://api.au.sumologic.com/docs/#operation/disableScheduledView
    """
    def disable_scheduled_view(self, scheduled_view_id):
        request_url = '{0}/v1/scheduledViews/{1}/disable'.format(
            self.__endpoint,
            scheduled_view_id
        )
        return self.__execute_api(
            request_type        = 'DELETE',
            request_url         = request_url
        )


    """ Pause a scheduled view.
    Pause a scheduled view with the given identifier.

    Method: POST
    Path:   /v1/scheduledViews/{scheduled_view_id}/pause
    https://api.au.sumologic.com/docs/#operation/pauseScheduledView
    """
    def pause_scheduled_view(self, scheduled_view_id):
        request_url = '{0}/v1/scheduledViews/{1}/pause'.format(
            self.__endpoint,
            scheduled_view_id
        )
        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url
        )


    """ Start a scheduled view.
    Start a scheduled view with the given identifier.

    Method: POST
    Path:   /v1/scheduledViews/{scheduled_view_id}/start
    https://api.au.sumologic.com/docs/#operation/startScheduledView
    """
    def start_scheduled_view(self, scheduled_view_id):
        request_url = '{0}/v1/scheduledViews/{1}/start'.format(
            self.__endpoint,
            scheduled_view_id
        )
        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url
        )



    # # #   ==================================================
    # # #   ----[BETA]----------------------------------------
    # # #   TOKENS VIEW MANAGEMENT API
    # # #   https://api.au.sumologic.com/docs/#tag/tokensLibraryManagement
    # # #
    # # #   Tokens are associated with your organization to authorize specific operations. Currently, we support
    # # #   collector registration tokens, which can be used to register Installed Collectors. Managing tokens
    # # #   requires the Manage Tokens role capability. For more information see https://help.sumologic.com/?cid=0100.

    """ Get a list of tokens.
    Get a list of all tokens in the token library.

    Method: GET
    Path:   /v1/tokens
    https://api.au.sumologic.com/docs/#operation/listTokens
    """
    def list_tokens(self):
        request_url = '{0}/v1/tokens'.format(
            self.__endpoint
        )
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url
        )


    """ Create a token.
    Create a token in the token library.

    Method: POST
    Path:   /v1/tokens
    https://api.au.sumologic.com/docs/#operation/createToken
    """
    def create_token(self, request_data):
        request_url = '{0}/v1/tokens'.format(
            self.__endpoint
        )
        return self.__execute_api(
            request_type        = 'POST',
            request_url         = request_url,
            request_data        = request_data
        )


    """ Get a token.
    Get a token with the given identifier in the token library.

    Method: GET
    Path:   /v1/tokens/{token_id}
    https://api.au.sumologic.com/docs/#operation/getToken
    """
    def get_token(self, token_id):
        request_url = '{0}/v1/tokens/{1}'.format(
            self.__endpoint,
            token_id
        )
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url
        )


    """ Update a token.
    Update a token with the given identifier in the token library.

    Method: PUT
    Path:   /v1/tokens/{token_id}
    https://api.au.sumologic.com/docs/#operation/updateToken
    """
    def update_token(self, token_id, request_data):
        request_url = '{0}/v1/tokens/{1}'.format(
            self.__endpoint,
            token_id
        )
        return self.__execute_api(
            request_type        = 'GET',
            request_url         = request_url,
            request_data        = request_data
        )


    """ Delete a token.
    Delete a token with the given identifier in the token library.

    Method: DELETE
    Path:   /v1/tokens/{token_id}
    https://api.au.sumologic.com/docs/#operation/deleteToken
    """
    def delete_token(self, token_id):
        request_url = '{0}/v1/tokens/{1}'.format(
            self.__endpoint,
            token_id
        )
        return self.__execute_api(
            request_type        = 'DELETE',
            request_url         = request_url
        )