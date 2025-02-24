from django.utils.deprecation import MiddlewareMixin
from dashboard.models import Member

class CleanupTemporaryMembersMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.session.session_key:  # If session expired
            Member.objects.filter(temporary=True).delete()
