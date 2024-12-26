from django.db import models
from model_utils.managers import InheritanceManager

from ..work_source import WorkSource


class SourceWorkBase(models.Model):
    work_source = models.OneToOneField(WorkSource, on_delete=models.CASCADE)
    objects = InheritanceManager()
