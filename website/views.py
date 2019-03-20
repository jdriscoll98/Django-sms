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
from plaid import Client as PlaidClient

# -------------------------------------------------------------------------------
# Page Views
# -------------------------------------------------------------------------------


class TwillioViewMixin(object):
    """
    Exempts the view from CSRF requirements.
    NOTE:
        This should be the left-most mixin of a view.
    """

    @method_decorator(twilio_view)
    def dispatch(self, *args, **kwargs):
        return super(TwillioViewMixin, self).dispatch(*args, **kwargs)


@login_required
def homepage_view(request):
    context = {}
    return render(request, "website/homepage.html", context)


class SMS(TwillioViewMixin, FormView):
    template_name = 'website/homepage.html'
    form_class = PhoneNumberForm
    success_url = reverse_lazy('website:auth_page')

    def form_valid(self, form):
        number = self.request.POST.get('number')
        code = random.randint(11111, 99999)
        client = TwilioClient(settings.TWILIO_ACCOUNT_SID,
                              settings.TWILIO_AUTH_TOKEN)
        response = client.messages.create(
                 body='Your secure access code is %s' % (str(code)),
                 to=number, from_=settings.TWILIO_PHONE_NUMBER)
        self.request.session['code'] = code
        self.request.session['number'] = number
        return HttpResponseRedirect(self.get_success_url())


class AuthPage(FormView):
    template_name = 'website/auth_page.html'
    form_class = AuthCodeForm
    success_url = reverse_lazy('website:payment')

    def form_valid(self, form):
        auth_code = self.request.POST.get('code')
        if int(auth_code) == int(self.request.session['code']):
            # customer = get_stripe_customer(self.request.session['number'])
            if False:
                return HttpResponseRedirect(self.get_success_url())
            return HttpResponseRedirect(reverse_lazy('website:plaid_auth'))
        else:
            return HttpResponseRedirect(reverse_lazy('website:auth_page'))


class PlaidAuth(View):
    def get(self, *args, **kwargs):
        return render(self.request, 'website/plaid_auth.html')

    def post(self, *args, **kwargs):
        client = PlaidClient(
                            client_id=settings.PLAID_CLIENT_ID,
                            secret=settings.PLAID_SECRET,
                            public_key=settings.PLAID_PUBLIC_KEY,
                            environment=settings.PLAID_ENV,
                            )
        public_token = self.request.POST.get('public_token')
        response = client.Item.public_token.exchange(public_token)
        access_token = response['access_token']
        data = {
            'success': True,
            'url': reverse_lazy('website:payment')
        }
        return JsonResponse(data)


class PaymentView(FormView):
    template_name = 'website/payment_form.html'
    form_class = PaymentForm
    success_url = reverse_lazy('website:thanks')


class ThankYouPage(TemplateView):
    template_name = 'website/thanks.html'
