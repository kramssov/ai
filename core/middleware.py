from django.http import HttpResponseForbidden

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Extract tenant from subdomain or URL path
        tenant_name = request.META.get('HTTP_X_TENANT', 'default')
        request.tenant = tenant_name  # Add tenant to request
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        user = request.user
        if user.is_authenticated:
            if user.role == 'client' and not user.tenant:
                return HttpResponseForbidden("You do not have a tenant assigned.")
        return None