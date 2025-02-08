from django.db import models
from otodb.account.models import Account

class Vote(models.Model):
    user = models.ForeignKey(Account, blank=False, null=False, on_delete=models.CASCADE)
    score = models.FloatField(null=False, blank=False)
