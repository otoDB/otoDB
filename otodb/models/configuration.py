from django.db import models


class Configuration(models.Model):
    code_name = models.CharField(max_length=127, blank=False)
    value = models.TextField(blank=True)

    def __str__(self) -> str:
        return f'{self.code_name}'

    class Meta:
        permissions = [
            ('manage_configuration', 'Can change the configurations of the application'),
        ]
