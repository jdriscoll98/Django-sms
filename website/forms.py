from django import forms
from phonenumber_field.formfields import PhoneNumberField
from .models import Customer


class PhoneNumberForm(forms.Form):
    number = forms.RegexField(regex=r'^\+?1?\d{10}$',
                              error_messages={'required':
                                              "Phone number must be entered" +
                                              'in the format:' +
                                              ' 999999999.'})

class AuthCodeForm(forms.Form):
    code = forms.RegexField(regex=r'^\d{5}$')


class PaymentForm(forms.Form):
    amount = forms.IntegerField(min_value=0)
