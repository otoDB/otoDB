from django.db import models

from otodb.account.models import Account
from otodb.common import utils

from .enums import Status


class Implication(models.Model):
    from_tag = models.ForeignKey("otodb.TagWork", default=None, on_delete=models.CASCADE, related_name="from_implications", help_text="Child")
    to_tag = models.ForeignKey("otodb.TagWork", default=None, on_delete=models.CASCADE, related_name="to_implications", help_text="Parent")
    author = models.ForeignKey(Account, null=True, on_delete=models.SET_NULL, related_name="authored_implications")
    approver = models.ForeignKey(Account, blank=True, null=True, default=None, on_delete=models.SET_NULL, related_name="approved_implications")
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)

    status = models.IntegerField(
        choices=Status.choices,
        default=Status.PENDING
    )

    def __str__(self) -> str:
        return f'{self.from_tag} -> {self.to_tag}'

    def save(self, *args, **kwargs):
        super(Implication, self).save(*args, **kwargs)
        utils.verify_and_perform_implications(self.from_tag)
