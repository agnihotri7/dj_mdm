"""
"""
from plistlib import Data
from django.conf import settings


def get_command_data(command, device=None):
    data = None
    if command.name == 'DeviceLock':
        data = {
            'CommandUUID': command.uuid,
            'Command':{
                'RequestType': 'DeviceLock',
            }
        }
    elif command.name == 'CertificateList':
        data = {
            'CommandUUID': command.uuid,
            'Command': {
                'RequestType': 'CertificateList'
            }
        }
    elif command.name == 'InstalledApplicationList':
        data = {
            'CommandUUID': command.uuid,
            'Command': {
                'RequestType': 'InstalledApplicationList'
            }
        }
    elif command.name == 'Restrictions':
        data = {
            'CommandUUID': command.uuid,
            'Command': {
                'RequestType': 'Restrictions'
            }
        }
    elif command.name == 'DeviceInformation':
        data = {
            'CommandUUID': command.uuid,
            'Command': {
                'RequestType': 'DeviceInformation',
                'Queries': [
                    'AvailableDeviceCapacity', 'BluetoothMAC', 'BuildVersion',
                    'CarrierSettingsVersion', 'CurrentCarrierNetwork', 'CurrentMCC',
                    'CurrentMNC', 'DataRoamingEnabled', 'DeviceCapacity', 'DeviceName',
                    'ICCID', 'IMEI', 'IsRoaming', 'Model', 'ModelName',
                    'ModemFirmwareVersion', 'OSVersion', 'PhoneNumber', 'Product',
                    'ProductName', 'SIMCarrierNetwork', 'SIMMCC', 'SIMMNC', 'SerialNumber',
                    'UDID', 'WiFiMAC', 'UDID', 'UnlockToken', 'MEID', 'CellularTechnology',
                    'BatteryLevel', 'SubscriberCarrierNetwork', 'VoiceRoamingEnabled',
                    'SubscriberMCC', 'SubscriberMNC', 'JailbreakDetected',
                ]
            }
        }
    elif command.name == 'SecurityInfo':
        data = {
            'CommandUUID': command.uuid,
            'Command': {
                'RequestType': 'SecurityInfo',
                'Queries': [
                    'HardwareEncryptionCaps', 'PasscodePresent',
                    'PasscodeCompliant', 'PasscodeCompliantWithProfiles',
                ]
            }
        }
    elif command.name == 'ClearPasscode':
        data = {
            'CommandUUID': command.uuid,
            'Command': {
                'RequestType': 'ClearPasscode',
                'UnlockToken': command.unlock_token
            }
        }
    elif command.name == 'InstallApplication':
        data = {
            'CommandUUID': command.uuid,
            'Command': {
                'RequestType': 'InstallApplication',
                'ManagementFlags': 4,  # do not delete app while deleting MDM
                'iTunesStoreID': 336435697,  # iTune Movie test app
            }
        }
    elif command.name == 'HideApps':
        file = settings.BASE_DIR + '/hideApps.txt'
        f = open(file, 'rb')
        my_data = f.read()
        url = '<string>{0}/mdm/webclip-dashboard/{1}/</string>'.format(settings.MDM_SERVER_URL, device.udid)
        my_data = my_data.replace('<string>https://google.com</string>', url)
        data = {
            'CommandUUID': command.uuid,
            'Command': {
                'RequestType': 'InstallProfile',
                'Payload': Data(my_data)
            }
        }
        f.close()
    elif command.name == 'UnHideApps':
        file = settings.BASE_DIR + '/unhideApps.txt'
        f = open(file, 'rb')
        data = {
            'CommandUUID': command.uuid,
            'Command': {
                'RequestType': 'InstallProfile',
                'Payload': Data(f.read())
            }
        }
        f.close()

    return data
