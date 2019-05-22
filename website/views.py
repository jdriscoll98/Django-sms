from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.template.loader import render_to_string
from django.views import View
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django_twilio.decorators import twilio_view
import json
from twilio.twiml.messaging_response import MessagingResponse
import random
from twilio.rest import Client as TwilioClient
from django.conf import settings
from .forms import PhoneNumberForm, AuthCodeForm, PaymentForm
from .models import Customer, Company
from plaid import Client as PlaidClient
from pprint import pprint

# -------------------------------------------------------------------------------
# Page Views
# -------------------------------------------------------------------------------


class TwillioViewMixin(object):
    # class based decorator for twilio view
    @method_decorator(twilio_view)
    def dispatch(self, *args, **kwargs):
        return super(TwillioViewMixin, self).dispatch(*args, **kwargs)

# make a payment page
@login_required
def homepage_view(request):
    context = {
        # this page will be used when using the service as a "point of sale" service
        # other wise a custom link will be put on their homepage witht their slug
        'company': Company.objects.get(owner=request.user)
    }
    return render(request, "website/homepage.html", context)


# First view the user reaches
class SMS(TwillioViewMixin, FormView):
    template_name = 'website/phone_form.html'
    form_class = PhoneNumberForm

    # if form is valid ->
    def form_valid(self, form):
        phone_number = self.request.POST.get('phone_number')
        code = random.randint(10000, 99999) # generate a random code to send to user
        client = TwilioClient(settings.TWILIO_ACCOUNT_SID,
                              settings.TWILIO_AUTH_TOKEN)
        # twilio way of sending messages
        client.messages.create(
                 body='Your secure access code is %s' % (str(code)),
                 to=phone_number, from_=settings.TWILIO_PHONE_NUMBER)
        self.request.session['code'] = code # store code in session for auth page
        self.request.session['phone_number'] = phone_number # store number in session to get/create customer once authenticated
        return HttpResponseRedirect(self.get_success_url()) # GO to auth_page

    def get_success_url(self, **kwargs):
        return reverse_lazy('website:auth_page', kwargs={'slug': self.kwargs.get('slug')})


class AuthPage(FormView):
    template_name = 'website/auth_page.html'
    form_class = AuthCodeForm

    # if form is valid
    def form_valid(self, form):
        auth_code = self.request.POST.get('code') # their submitted code
        if int(auth_code) == int(self.request.session['code']): # check if it matches the stored code
            # once authenticated, look for a customer
            customer = Customer.objects.filter(phone_number=self.request.session['number']).first()
            # i did filter().first, because there will only be one customer with that phone number but there may be none
            if customer:
                return HttpResponseRedirect(self.get_success_url()) # payment page
            else:
                # if no customer, go to plaid auth
                return HttpResponseRedirect(reverse_lazy('website:plaid_auth', kwargs={'slug': self.kwargs.get('slug')}))
        else:
            # wrong code, return to page again
            return HttpResponseRedirect(reverse_lazy('website:auth_page'))

    def get_success_url(self, **kwargs):
        return reverse_lazy('website:payment', kwargs={'slug': self.kwargs.get('slug')})

class PlaidAuth(View):
    def get(self, *args, **kwargs):
        # renders plaid Link
        context = {
            'slug': self.kwargs.get('slug')
        }
        return render(self.request, 'website/plaid_auth.html', context)

    def post(self, *args, **kwargs): # this needs cleaning up
        client = PlaidClient(
                            client_id=settings.PLAID_CLIENT_ID,
                            secret=settings.PLAID_SECRET,
                            public_key=settings.PLAID_PUBLIC_KEY,
                            environment=settings.PLAID_ENV,
                            )
        public_token = self.request.POST.get('public_token') # passed in ajax
        response = client.Item.public_token.exchange(public_token) # exchange token with plaid to get access_token
        auth_response = client.Auth.get(response['access_token']) # authenticate user
        account_id = auth_response['accounts'][0]['account_id']  # authed bank account id
        # get a stripe bank acocunt token to link to a customer
        stripe_response = client.Processor.stripeBankAccountTokenCreate(
                                                                access_token,
                                                                account_id
                                                                )
        bank_account_token = stripe_response['stripe_bank_account_token']
        company = Company.objects.get(slug=self.kwargs.get('slug')) # get company to use method
        phone_number = self.request.session['phone_number'] # retrieve number to create customer
        if company.create_stripe_customer(bank_account_token, phone_number):
            success = True
        else:
            success = False
        data = {
            'success': success,
            'url': reverse_lazy('website:payment', kwargs={'slug': company.slug})
        }
        return JsonResponse(data)


class PaymentView(FormView):
    template_name = 'website/payment_form.html'
    form_class = PaymentForm
    success_url = reverse_lazy('website:thanks')

    def form_valid(self, form):
        # gather information to charge customer
        phone_number = self.request.session['number']
        amount = int(self.request.POST.get('amount')) * 100
        customer_id = Customer.objects.get(phone_number=phone_number).stripe_id
        company = Company.objects.get(slug=self.kwargs.get('slug'))
        company.charge_customer(customer_id, amount)
        return HttpResponseRedirect(reverse_lazy('website:thanks')) #thank you page


class ThankYouPage(TemplateView):
    template_name = 'website/thanks.html'
