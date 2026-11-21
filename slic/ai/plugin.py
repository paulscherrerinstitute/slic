from importlib.resources import files

from yokai import Plugin, read_instance_dict, read_markdown
from yokai import YokAI as CoreYokAI


FAQ_FILE = files(__package__) / "FAQ.md"

PARAGRAPH = read_markdown(files(__package__) / "paragraph.md")


class YokAI(CoreYokAI):
    """
    YokAI for slic sessions
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, plugins=[SlicPlugin()], **kwargs)



class SlicPlugin(Plugin):
    """
    Tells YokAI about slic:
    The session of an endstation, slic's FAQ, READMORE.md,
    and slic objects, identified by slic name and ID.
    """

    module_prefix = "slic"
    faq_file = FAQ_FILE
    paragraph = PARAGRAPH

    def identification(self, obj):
        attrs = read_instance_dict(obj)
        return {"name": attrs.get("name"), "ID": attrs.get("ID")}



