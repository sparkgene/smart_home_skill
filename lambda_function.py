from __future__ import print_function

import json
import urllib2
from uuid import uuid4

AMAZON_API_USER_PROFILE = "https://api.amazon.com/user/profile"
AMAZON_OAUTH_HEADER = "x-amz-access-token"

ALEXA_REQUEST_DISCOVER = "Alexa.ConnectedHome.Discovery"
ALEXA_REQUEST_CONTROL = "Alexa.ConnectedHome.Control"
ALEXA_REQUEST_SYSYTEM = "Alexa.ConnectedHome.System"

CONTROL_TURN_ON = "TurnOnRequest"
CONTROL_TURN_OFF = "TurnOffRequest"
CONTROL_CONFIRMATION_TURN_ON = "TurnOnConfirmation"
CONTROL_CONFIRMATION_TURN_OFF = "TurnOffConfirmation"

def lambda_handler(event, context):
    print(event)

    if event['header']['namespace'] == ALEXA_REQUEST_DISCOVER:
        return discover_device(event)

    if event['header']['namespace'] == ALEXA_REQUEST_CONTROL:
        return control_device(event)

    if event['header']['namespace'] == ALEXA_REQUEST_SYSYTEM:
        return check_system(event)

    print('un supported control request')
    return None

def discover_device(event):
    print('discover_device')

    user_profile = describe_user_profile(event['payload']['accessToken'])

    discovered_appliances = {
        "discoveredAppliances": get_appliances(user_profile)
    }

    return build_discover_response(event['header'], discovered_appliances)

def get_appliances(user_profile):

    #####################################
    # do something to get users devices #
    #####################################

    return [
        {
            "applianceId": "my-device-unique-id",
            "manufacturerName": "sparkgene.com",
            "modelName": "my-device-model-1",
            "version": "1",
            "friendlyName": "awsome light",
            "friendlyDescription": "some awsome light description.",
            "isReachable": True,
            "actions": [
                "turnOn",
                "turnOff"
            ],
            "additionalApplianceDetails": {}
        }
    ]

def build_discover_response(event_header, discovered_appliances):
    header = {
        "payloadVersion": event_header['payloadVersion'],
        "namespace": event_header['namespace'],
        "name": "DiscoverAppliancesResponse",
        "messageId": str(uuid4())
    }
    response = {
        "header": header,
        "payload": discovered_appliances
    }

    print(response)
    return response

def control_device(event):
    print('control_device')
    user_profile = describe_user_profile(event['payload']['accessToken'])

    #########################################
    # do something to control users devices #
    #########################################

    if event['header']['name'] == CONTROL_TURN_ON:
        print('turn on ' + event['payload']['appliance']['applianceId'])
        return build_control_response(event['header'], CONTROL_CONFIRMATION_TURN_ON)

    if event['header']['name'] == CONTROL_TURN_OFF:
        print('turn on ' + event['payload']['appliance']['applianceId'])
        return build_control_response(event['header'], CONTROL_CONFIRMATION_TURN_OFF)

    return build_unsuported_control_response()

def build_control_response(event_header, name):
    response = {
        "header": {
            "messageId": str(uuid4()),
            "name": name,
            "namespace": event_header['namespace'],
            "payloadVersion": event_header['payloadVersion']
        },
        "payload": {}
    }

    print(response)
    return response

def build_unsuported_control_response():
    print('un supported control request')
    response = {
        "header": {
            "messageId": str(uuid4()),
            "name": "UnsupportedOperationError",
            "namespace": ALEXA_REQUEST_CONTROL,
            "payloadVersion": "2"
        },
        "payload": {}
    }

    print(response)
    return response

def describe_user_profile(access_token):

    req = urllib2.Request(AMAZON_API_USER_PROFILE)
    req.add_header(AMAZON_OAUTH_HEADER, access_token)
    response = urllib2.urlopen(req)
    if response.getcode() == 200:
        return json.loads(response.read())
    else:
        print(response.getcode())
        raise Exception(response.msg)
