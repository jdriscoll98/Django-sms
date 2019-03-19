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
from twilio.rest import Client
from django.conf import settings
from .forms import PhoneNumberForm, AuthCodeForm, PaymentForm

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
        try:
            to = self.request.POST.get('number')
            code = random.randint(11111, 99999)
            client = Client(settings.TWILIO_ACCOUNT_SID,
                            settings.TWILIO_AUTH_TOKEN)
            response = client.messages.create(
                     body='Your secure access code is %s' % (str(code)),
                     to=to, from_=settings.TWILIO_PHONE_NUMBER)
            self.request.session['code'] = code
            print('hello')
        except Exception as e:
            print(e)
        return HttpResponseRedirect(self.get_success_url())


class AuthPage(FormView):
    template_name = 'website/auth_page.html'
    form_class = AuthCodeForm
    success_url = reverse_lazy('website:payment')

    def form_valid(self, form):
        auth_code = self.request.POST.get('code')
        print(auth_code)
        print(self.request.session['code'])
        if int(auth_code) == int(self.request.session['code']):
            return HttpResponseRedirect(self.get_success_url())
        else:
            return HttpResponseRedirect(reverse_lazy('website:auth_page'))


class PaymentView(FormView):
    template_name = 'website/payment_form.html'
    form_class = PaymentForm
    success_url = reverse_lazy('website:thanks')

class ThankYouPage(TemplateView):
    template_name = 'website/thanks.html'
