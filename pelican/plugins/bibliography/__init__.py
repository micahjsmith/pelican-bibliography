from .bibliography import register  # NOQA

try:
    from importlib.metadata import version
    __version__ = version(__name__)
except:
    __version__ = '<unknown>'
