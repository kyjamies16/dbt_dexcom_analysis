from datetime import datetime

def format_pretty_date(date_obj):
    """Formats a date like '2025-05-10' into 'May 10th 2025' (no comma)."""
    return date_obj.strftime("%B {S} %Y").replace('{S}', str(date_obj.day) + suffix(date_obj.day))


def suffix(day):
    return "th" if 11 <= day <= 13 else {1:"st",2:"nd",3:"rd"}.get(day % 10, "th")