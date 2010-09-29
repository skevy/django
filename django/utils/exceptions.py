def format_exception(exception):
    return unicode(exception) or exception.__class__.__name__
