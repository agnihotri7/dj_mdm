"""
"""
import sys
import uuid
import base64
import fileinput
import datetime

from django.utils import timezone
from django.conf import settings
from django.shortcuts import get_object_or_404
from urlparse import urlparse, parse_qs
from APNSWrapper import *

from mdm.models import MDMDevice, DeviceCommand


def replaceAll(file, searchExp, replaceExp):
    for line in fileinput.input(file, inplace=1):
        if searchExp in line:
            line = line.replace(searchExp, replaceExp)
        sys.stdout.write(line)


def notify_device(device):
    device_token = base64.b64decode(device.device_token)
    cert = settings.APNS_CERT
    wrapper = APNSNotificationWrapper(cert, False)
    message = APNSNotification()
    message.token(device_token)
    message.appendProperty(APNSProperty('mdm', str(device.push_magic)))
    wrapper.append(message)
    wrapper.notify()
