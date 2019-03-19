from django import forms
from phonenumber_field.formfields import PhoneNumberField


class PhoneNumberForm(forms.Form):
    number = forms.IntegerField()


class AuthCodeForm(forms.Form):
    code = forms.IntegerField()

class PaymentForm(forms.Form):
    amount = forms.IntegerField()
