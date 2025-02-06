from django.urls import path
from .views import signup, tenant_signup

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('tenant_signup/', tenant_signup, name='tenant_signup'),
]