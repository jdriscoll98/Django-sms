from django.db import models
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.utils.text import slugify
import stripe


class Company(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    stripe_public = models.CharField(max_length=100)
    stripe_secret = models.CharField(max_length=100)
    slug = models.SlugField(max_length=200, unique=True, blank=True)

    class Meta:
        verbose_name_plural = 'Companies'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Company, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def create_stripe_customer(self, token, phone_number):
        stripe.api_key = self.stripe_secret
        stripe_customer = stripe.Customer.create(source=token)
        Customer.objects.create(
                                company=self,
                                phone_number=phone_number,
                                stripe_id=stripe_customer['id']
                                )
        return str(stripe_customer['id'])

    def charge_customer(self, id, amount):
        stripe.api_key = self.stripe_secret
        stripe.Charge.create(
            amount=amount,
            currency='usd',
            customer=id
        )

class Customer(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, unique=True)
    stripe_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return str(self.company) + ' ' + str(self.id)

    def get_absolute_url(self):
        return reverse_lazy('website:plaid_auth')
