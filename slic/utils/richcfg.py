from IPython import get_ipython

import rich
import rich.pretty


def richcfg():
    rich.pretty.install()
    replace_ipython_inspect()


def replace_ipython_inspect():
    ipy = get_ipython()
    if ipy is None:
        return

    def _inspect(obj, oname="", formatter=None, info=None, detail_level=0, enable_html_pager=True, omit_sections=()):
        if isinstance(obj, type):
            title = f"{obj.__module__}.{obj.__name__}"
        else:
            title = f"{oname} = {obj}"
        methods = (detail_level > 0)
        rich.inspect(obj, title=title, methods=methods)

    ipy.inspector.pinfo = _inspect



