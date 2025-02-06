from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls')),
    path('admin_portal/', include('apps.admin_portal.urls')),
    path('tenant_portal/', include('apps.tenant_portal.urls')),
    path('client_portal/', include('apps.client_portal.urls')),
    path('warehouse/', include('apps.warehouse.urls')),
#    path('login/', auth_views.LoginView.as_view(), name='login'),
#    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),  # Specify the custom template
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),  # Specify the next page
]