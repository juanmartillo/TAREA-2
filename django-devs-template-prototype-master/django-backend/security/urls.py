from django.urls import path
from security.login import LoginAuthView

urlpatterns = [
    path('login', LoginAuthView.as_view(), name='login'),
    #path('sign-up', SignUpView.as_view(), name='sign_up'),
    #path('logout', LogoutRedirectView.as_view(), name='logout'),
]
