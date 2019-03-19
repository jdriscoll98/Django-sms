from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django_twilio.decorators import twilio_view
import json
from twilio.twiml.messaging_response import MessagingResponse

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


class SMS(TwillioViewMixin, View):
    def get(self, *args, **kwagrs):
        twiml = ('<Response><Message>Hello from your Django app!' +
                 '</Message></Response>')
        return HttpResponse(twiml, content_type='text/xml')

    def post(self, *args, **kwargs):
        name = self.request.POST.get('Body', '')
        msg = 'Hey %s, how are you today?' % (name)
        r = MessagingResponse()
        r.message(msg)
        return r
