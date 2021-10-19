import warnings


def exception_to_warning(exc, category=UserWarning, stacklevel=1, **kwargs):
    excname = type(exc).__name__
    message = f"{excname}: {exc}"

    # forward tb by stacklevel entries
    tb = exc.__traceback__
    for _ in range(stacklevel):
        tb = tb.tb_next

    lineno = tb.tb_lineno

    frame = tb.tb_frame
    code = frame.f_code

    module_globals = frame.f_globals
    registry = module_globals.setdefault("__warningregistry__", {}) # taken from warnings.warn source

    filename = code.co_filename
    module = code.co_name

    warnings.warn_explicit(message, category, filename, lineno, module=module, registry=registry, module_globals=module_globals, **kwargs)



