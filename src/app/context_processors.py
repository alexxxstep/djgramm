"""Context processors for DJGramm."""


def unread_news_count(request):
    """Add unread news count to template context."""
    if request.user.is_authenticated:
        return {"unread_news_count": request.user.get_unread_news_count()}
    return {"unread_news_count": 0}
