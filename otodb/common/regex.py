import re

RE_ALPHA = re.compile(r'^[a-zA-Z]*$')
RE_ALPHANUMERIC = re.compile(r'^[a-zA-Z0-9]*$')
RE_HEX_COLOR = re.compile(r'^(?=[0-9a-fA-F]*$)(?:.{3}|.{6})$')
