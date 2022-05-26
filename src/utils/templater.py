import os.path
from string import Template


class TemplateHash(Template):
    delimiter = "#"


def core(src_file: str, dest_file: str, values: dict):
    """
    content: string with template variables
    values: dictionary with template variables
    """

    if os.path.isfile(src_file):
        with open(src_file, "r") as file:
            content = file.read()
    else:
        content = src_file

    s = TemplateHash(content)

    content = s.safe_substitute(values)

    with open(dest_file, "w") as f:
        f.write(content)
