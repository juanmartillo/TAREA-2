from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import RedirectView
from rest_framework import status
from security.functions import addUserData


class LoginAuthView(LoginView):
    form_class = AuthenticationForm
    template_name = 'security/login.html'

    def get_form(self, form_class=None):
        form = super(LoginAuthView, self).get_form()
        form.fields['username'].widget.attrs = {
            'class': 'form-control form-control-md',
            'placeholder': 'Ingrese su username',
            'autofocus': True,
        }
        form.fields['password'].widget.attrs = {
            'class': 'form-control form-control-md',
            'placeholder': 'Ingrese su password',
            'autocomplete': 'off',
        }
        return form

    def get(self, request, *args, **kwargs):
        login_different = reverse_lazy('login')
        if request.user.is_authenticated and login_different != request.path:
            return redirect(reverse_lazy('login_authenticated'))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Inicio de Sesión'
        addUserData(self.request, context)
        return context


    def post(self, request, *args, **kwargs):
        data = {'errors': []}
        status_code = None
        try:
            cuenta = str(request.POST.get('username')).strip()
            password = str(request.POST.get('password')).strip()

            user = authenticate(username=cuenta, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    status_code = status.HTTP_200_OK
                    data['code'] = 'success'
                    data['message'] = 'Login user successful'
                else:
                    status_code = status.HTTP_400_BAD_REQUEST
                    data['message'] = 'Login user session failed'
                    data['errors'].append('Login Fallido!, usuario no esta habilitado')
            else:
                status_code = status.HTTP_400_BAD_REQUEST
                data['message'] = 'Login user session failed'
                data['errors'].append('Login Fallido!, credenciales incorrectas.')

        except Exception as e:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            data['message'] = 'Internal error in code'
            data['errors'].append(str(e))

        return JsonResponse(data, status=status_code)


class LogoutRedirectView(RedirectView):
    pattern_name = 'login'

    def dispatch(self, request, *args, **kwargs):
        logout(request)
        return super().dispatch(request, *args, **kwargs)
