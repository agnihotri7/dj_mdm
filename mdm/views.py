"""
"""
import os
import uuid
import datetime
from plistlib import *

from django.http import Http404
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

from mdm.commands import get_command_data
from mdm.models import MDMDevice, DeviceCommand
from mdm.utils import replaceAll, notify_device


@csrf_exempt
def ssl_cert(request):
    if request.method == 'GET':
        # TODO: not required in production
        file_path = os.path.join(settings.MEDIA_ROOT, 'server-ssl.cer')

        if not os.path.isfile(file_path):
            from shutil import copyfile
            # copy mobileconfig to media forlder
            src = settings.BASE_DIR + '/server-ssl.cer'
            dst = settings.MEDIA_ROOT + '/server-ssl.cer'
            if not os.path.exists(dst):
                copyfile(src, dst)

        f = open(file_path, 'rb')
        data = f.read()
        f.close()
        response = HttpResponse(data, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename={filename}'.format(filename='server-ssl.cer')
        return response
    raise Http404


@csrf_exempt
def enroll(request):
    if request.method == 'GET':
        file_path = os.path.join(settings.MEDIA_ROOT, 'Enroll.mobileconfig')
        if not os.path.isfile(file_path):
            from shutil import copyfile
            # copy mobileconfig to media forlder
            src = settings.BASE_DIR + '/Enroll.mobileconfig'
            dst = settings.MEDIA_ROOT + '/Enroll.mobileconfig'
            if not os.path.exists(dst):
                copyfile(src, dst)

        f = open(file_path, 'rb')
        data = f.read()
        f.close()
        response = HttpResponse(data, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename={filename}'.format(filename='Enroll.mobileconfig')
        return response
    raise Http404


@csrf_exempt
def checkin(request):
    """
        To Save device information after enroll
    """
    try:
        pl = readPlistFromString(request.body)
        if pl.get('MessageType') == 'Authenticate':
            print (pl)
            SerialNumber = pl.get('SerialNumber', '')
            ProductName = pl.get('ProductName', '')
            OSVersion = pl.get('OSVersion', '')
            BuildVersion = pl.get('BuildVersion', '')
            Topic = pl.get('Topic', '')
            UDID = pl.get('UDID', '')
            device, created = MDMDevice.objects.get_or_create(udid=UDID)
            device.name = ProductName
            device.model = BuildVersion
            device.serial_number = SerialNumber
            device.last_checkin = datetime.datetime.now()
            device.save()

        elif pl.get('MessageType') == 'TokenUpdate':
            print ('UDID: ', pl.get('UDID'))
            print ('push: ', pl.get('PushMagic', ''))
            print ('Topic: ', pl.get('Topic', ''))
            print ('token: ', pl.get('Token', '').asBase64(maxlinelength=8000))
            print ('unlock token: ', pl.get('UnlockToken', '').asBase64(maxlinelength=8000))
            # save MDMDevice information
            udid = pl.get('UDID')
            device, created = MDMDevice.objects.get_or_create(udid=udid)
            device.push_magic = pl.get('PushMagic', '')
            device.device_token = pl.get('Token', '').asBase64(maxlinelength=8000)
            device.unlock_token = pl.get('UnlockToken', '').asBase64(maxlinelength=8000)
            device.save()

        elif pl.get('MessageType') == 'CheckOut':
            device_id = pl.get('UDID')
            reason = 'mdm_deleted'

        return HttpResponse()
    except Exception as e:
        print (e)
        return HttpResponse()


@csrf_exempt
def queue(request):
    """To register device command for execution
    """
    try:
        data = request.POST # {udid, command, uuid}
        udid = data.get('udid')
        name = data.get('cmd')
        uuid = data.get('uuid')
        device = MDMDevice.objects.get(udid=udid)
        command = DeviceCommand.objects.create(device=device, uuid=uuid, name=name, status=1)
        # send notification to IOS device
        notify_device(device)
        return HttpResponse(status=200)
    except Exception as e:
        print (e)
        return HttpResponseBadRequest()


@csrf_exempt
def server(request):
    """To execute the responses from IOS devices
    """
    data = readPlistFromString(request.body)
    print (data)
    if data.get('Status', None) == 'Idle':
        # device is idle - send command to execute
        try:
            device = MDMDevice.objects.get(udid=data.get('UDID'))
            command = device.get_command_to_execute()
            res_data = {}
            if command:
                res_data = get_command_data(command, device)
                if res_data:
                    command.status = 2 # running
                    command.attempts += 1
                    command.save()
                else:
                    res_data = {}
                    command.status = 4 # error
                    command.attempts += 1
                    command.save()
        except Exception as e:
            print (e)
            return HttpResponse()

    elif data.get('Status', None) == 'Acknowledged':
        # command successfully executed then update response
        res_data = {}
        try:
            uuid = data.get('CommandUUID', None)
            cmd = DeviceCommand.objects.get(uuid=uuid)
            # check if all responses contains QueryResponse obj - update same in DeviceCommand
            cmd.status = 3 # success
            cmd.completed_at = datetime.datetime.now()
            cmd.response = request.body
            cmd.save()
        except Exception as e:
            print (e)
            return HttpResponse()

    elif data.get('Status', None) == 'Error' or data.get('Status', None) == 'CommandFormatError':
        res_data = {}
        try:
            uuid = data.get('CommandUUID', None)
            cmd = DeviceCommand.objects.get(uuid=uuid)
            cmd.status = 4 # failed
            cmd.completed_at = datetime.datetime.now()
            cmd.response = request.body
            cmd.message = "critical error occured"
            cmd.save()
        except Exception as e:
            print (e)
            return HttpResponse()

    elif data.get('Status', None) == 'NotNow':
        res_data = {}
        cmd = DeviceCommand.objects.get(uuid=data.get('CommandUUID', None))
        cmd.status = 1 # pending
        cmd.attempts = 0
        cmd.save()

    elif data.get('MessageType', None) == 'Authenticate':
        res_data = {}

    elif data.get('MessageType', None) == 'CheckOut':
        res_data = {}
        device_id = data.get('UDID')
        reason = 'mdm_deleted'
    else:
        res_data = {}

    res = writePlistToString(res_data)
    response = HttpResponse(res, content_type='application/xml; charset=UTF-8')
    response['Content-Length'] = len(res)
    return response


def devices_list(request):
    devices = MDMDevice.objects.all()
    context = {'devices': devices}
    return render(request, 'device_list.html', context)


def device_detail(request, pk):
    if request.method == 'GET':
        device = MDMDevice.objects.get(id=pk)
        commands = DeviceCommand.objects.filter(device=device)
        context = {'device': device, 'commands': commands}
        return render(request, 'device_detail.html', context)
    elif request.method == 'POST':
        command_name = request.POST.get('commandList', None)
        if command_name:
            try:
                command_uuid = str(uuid.uuid4())
                device = MDMDevice.objects.get(pk=pk)
                command = DeviceCommand.objects.create(
                            device=device, uuid=command_uuid,
                            name=command_name, status=1)
                # send notification to IOS device
                notify_device(device)
            except Exception as e:
                raise e
        return redirect('device-detail', pk=pk)


def commands_list(request):
    commands = DeviceCommand.objects.all()
    context = {'commands': commands}
    return render(request, 'commands.html', context)
