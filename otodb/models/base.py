import random

from django.db import models

class MediaBaseManager(models.Manager):
    def random(self):
        random_work = None
        work_ids = self.values_list('pk', flat=True)
        if work_ids:
            random_work = self.get(pk=random.choice(work_ids))
            return random_work
