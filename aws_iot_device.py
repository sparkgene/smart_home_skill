from __future__ import print_function

import json
import urllib2
from uuid import uuid4
import boto3
import time

AMAZON_API_USER_PROFILE = "https://api.amazon.com/user/profile"
AMAZON_OAUTH_HEADER = "x-amz-access-token"

ALEXA_REQUEST_DISCOVER = "Alexa.ConnectedHome.Discovery"
ALEXA_REQUEST_CONTROL = "Alexa.ConnectedHome.Control"
ALEXA_REQUEST_SYSYTEM = "Alexa.ConnectedHome.System"

CONTROL_TURN_ON = "TurnOnRequest"
CONTROL_TURN_OFF = "TurnOffRequest"
CONTROL_CONFIRMATION_TURN_ON = "TurnOnConfirmation"
CONTROL_CONFIRMATION_TURN_OFF = "TurnOffConfirmation"

APPLIANCE_ID_LIGHT = "my-living-light"
MODEL_NAME_LIGHT = "my-living-light 1"
APPLIANCE_ID_FAN = "my-living-fan"
MODEL_NAME_FAN = "my-living-fan 1"
APPLIANCE_ID_AC = "my-living-ac"
MODEL_NAME_AC = "my-living-ac 1"

LIGHT_ACTION_MAP = {
    "TurnOnRequest": "light_all",
    "TurnOffRequest": "light_off"
}
FAN_ACTION_MAP = {
    "TurnOnRequest": "fan_low",
    "TurnOffRequest": "fan_stop"
}
AC_ACTION_MAP = {
    "TurnOnRequest": "ac_on",
    "TurnOffRequest": "ac_off"
}

iot_client = boto3.client('iot-data', region_name='ap-northeast-1')


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
            "applianceId": APPLIANCE_ID_LIGHT,
            "manufacturerName": "sparkgene.com",
            "modelName": MODEL_NAME_LIGHT,
            "version": "1",
            "friendlyName": "living light",
            "friendlyDescription": "Living center light.",
            "isReachable": True,
            "actions": [
                "turnOn",
                "turnOff"
            ],
            "additionalApplianceDetails": {}
        },
        {
            "applianceId": APPLIANCE_ID_FAN,
            "manufacturerName": "sparkgene.com",
            "modelName": MODEL_NAME_FAN,
            "version": "1",
            "friendlyName": "living fan",
            "friendlyDescription": "Living ceiling fan.",
            "isReachable": True,
            "actions": [
                "turnOn",
                "turnOff"
            ],
            "additionalApplianceDetails": {}
        },
        {
            "applianceId": APPLIANCE_ID_AC,
            "manufacturerName": "sparkgene.com",
            "modelName": MODEL_NAME_AC,
            "version": "1",
            "friendlyName": "air con",
            "friendlyDescription": "Living air conditioner.",
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
    # get user profile if you need
    # user_profile = describe_user_profile(event['payload']['accessToken'])


    response_name = None
    if event['header']['name'] == CONTROL_TURN_ON:
        response_name = CONTROL_CONFIRMATION_TURN_ON
    elif event['header']['name'] == CONTROL_TURN_OFF:
        response_name = CONTROL_CONFIRMATION_TURN_OFF
    else:
        return build_error_response("UnsupportedOperationError")

    command = None
    if event['payload']['appliance']['applianceId'] == APPLIANCE_ID_LIGHT:
        command = LIGHT_ACTION_MAP[event['header']['name']]
    elif event['payload']['appliance']['applianceId'] == APPLIANCE_ID_FAN:
        command = FAN_ACTION_MAP[event['header']['name']]
    elif event['payload']['appliance']['applianceId'] == APPLIANCE_ID_AC:
        command = AC_ACTION_MAP[event['header']['name']]
    else:
        return build_error_response("NoSuchTargetError")

    send_command(command)

    return build_control_response(event['header'], response_name)

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

def build_error_response(name):
    print('return error response')
    response = {
        "header": {
            "messageId": str(uuid4()),
            "name": name,
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

def send_command(command):
    shadow = {
        'state': {
            'desired': {
                'command': command,
                'counter': int(time.time())
            }
        }
    }
    payload = json.dumps(shadow)

    response = iot_client.update_thing_shadow(
        thingName='alexa_home',
        payload= payload
    )
    return True
