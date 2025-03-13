from django import template
from datetime import datetime, date, time
from django.utils import timezone

register = template.Library()

@register.filter
def filter_future_sessions(sessions):
    """Filter sessions to only include those in the future."""
    now = timezone.now()
    future_sessions = []
    
    for session in sessions:
        # If your model has separate date and time fields
        if hasattr(session, 'date') and hasattr(session, 'time'):
            session_datetime = timezone.make_aware(
                datetime.combine(session.date, session.time)
            )
            if session_datetime > now:
                future_sessions.append(session)
        # If your model has a scheduled_time field (for the template)
        elif hasattr(session, 'scheduled_time'):
            if session.scheduled_time > now:
                future_sessions.append(session)
    
    return future_sessions