"""Custom template tags for DJGramm."""

import re

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def linkify_hashtags(text):
    """
    Convert hashtags in text to links.

    Example:
        "Check #travel photos" -> "Check <a href='/tag/travel'>#travel</a> photos"

    Args:
        text: Text containing hashtags

    Returns:
        HTML string with clickable hashtag links
    """
    if not text:
        return text

    pattern = r"#(\w+)"

    def replace_hashtag(match):
        tag_name = match.group(1)
        slug = tag_name.lower()
        return (
            f'<a href="/tag/{slug}/" '
            f'class="text-secondary hover:underline">#{tag_name}</a>'
        )

    return mark_safe(re.sub(pattern, replace_hashtag, text))
