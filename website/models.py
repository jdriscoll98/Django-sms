from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=100)
    stripe_public = models.CharField(max_length=100)
    stripe_secret = models.CharField(max_length=100)

    def __str__(self):
        return self.name
