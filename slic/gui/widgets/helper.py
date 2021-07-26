import warnings


def exception_to_warning(exc, *args, **kwargs):
    excname = type(exc).__name__
    message = f"{excname}: {exc}"
    warnings.warn(message, *args, **kwargs)



