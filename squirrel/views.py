from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, View
from django.shortcuts import resolve_url
from django.core.urlresolvers import reverse
from django.contrib.auth.hashers import make_password

from squirrel.models import *

# Create your views here.
class InitView(View):
	def get(self, request, *args, **kwargs):
		test_user = User.create_user(username='test', password='1234')
		test_user.std_id='100409001'
		test_user.nick_name='TEST'
		test_user.save()
		return HttpResponse(test_user)

class LoginView(FormView):
    form_class = AuthenticationForm
    template_name = 'squirrel/login.html'
    def form_valid(self, form):
        auth_login(self.request, form.get_user())
        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()
        return HttpResponseRedirect(reverse('deer:runDep'))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    @method_decorator(sensitive_post_parameters('password'))
    def dispatch(self, request, *args, **kwargs):
        request.session.set_test_cookie()
        return super(LoginView, self).dispatch(request, *args, **kwargs)

class LogoutView(View):
    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return HttpResponseRedirect(reverse('deer:runDep'))
