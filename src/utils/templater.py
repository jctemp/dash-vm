#!/usr/bin/python3
from string import Template


class TemplateHash(Template):
    delimiter = "#"


def core(content: str, dest_file, values: dict):
    """
    content: string with template variables
    values: dictionary with template variables
    """

    s = TemplateHash(content)
    content = s.safe_substitute(values)

    with open(dest_file, "w") as f:
        f.write(content)
