"""
"""
from django.db import models


class MDMDevice(models.Model):
    """
    """
    udid = models.CharField(max_length=100, unique=True, db_index=True)
    device_token = models.CharField(max_length=100)
    push_magic = models.TextField(blank=True, null=True)
    unlock_token = models.TextField(blank=True, null=True)
    last_checkin = models.DateTimeField(null=True)
    last_notification = models.DateTimeField(null=True)
    name = models.CharField(max_length=128, blank=True, default="")
    model = models.CharField(max_length=32, blank=True, default="")
    serial_number = models.CharField(max_length=32, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'mdm_device'
        ordering = ['-created_at']

    def __str__(self):
        return str(self.udid) + ' : ' + self.name

    def get_pending_requests(self):
        commands = DeviceCommand.objects.filter(device=self, status=1) # pending
        return commands

    def get_command_to_execute(self):
        command = DeviceCommand.objects.filter(device=self, status=1).first() # pending
        return command

    def get_running_requests(self):
        commands = DeviceCommand.objects.filter(device=self, status=2) # running
        return commands

    def get_success_requests(self):
        commands = DeviceCommand.objects.filter(device=self, status=3) # success
        return commands

    def get_failed_requests(self):
        commands = DeviceCommand.objects.filter(device=self, status=4) # error
        return commands


class DeviceCommand(models.Model):
    """
    """
    PENDING, RUNNING, SUCCESS, FAILED = 1, 2, 3, 4
    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (RUNNING, 'Running'),
        (SUCCESS, 'Success'),
        (FAILED, 'Failed'),
    )
    device = models.ForeignKey(MDMDevice)
    uuid = models.CharField(max_length=36, db_index=True)
    name = models.CharField(max_length=128) # RequestType in command data
    payload = models.TextField(null=True, blank=True)
    queries = models.TextField(null=True, blank=True)
    unlock_token = models.CharField(max_length=128)
    status = models.IntegerField(choices=STATUS_CHOICES, default=PENDING)
    is_cron = models.BooleanField(default=True)
    message = models.TextField(blank=True, null=True)
    attempts = models.IntegerField(default=0)
    requested_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'mdm_device_command'
        ordering = ['created_at']

    def __str__(self):
        return str(self.id) + ' : ' + self.name
