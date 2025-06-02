# In your context_processors.py
from .models import Alert

def alerts_context(request):
    if request.user.is_authenticated:
        return {
            'unread_alerts_count': Alert.objects.filter(user=request.user, is_read=False).count(),
            'recent_alerts': Alert.objects.filter(user=request.user).order_by('-created_at')[:5]
        }
    return {}