"""Version declaration"""

__version__ = "0.2.1"


def parse_version(version):
    """
    '0.1.2.dev1' -> (0, 1, 2, 'dev1')
    '0.1.2' -> (0, 1, 2)
    """
    v = version.split(".")
    ret = []
    for p in v:
        if p.isdigit():
            ret.append(int(p))
        else:
            ret.append(p)
    return tuple(ret)


VERSION = parse_version(__version__)


def __getattr__(name):
    """Allow `from django_dump_die import dd, dump`, without importing Django until they are used."""
    if name in ("dd", "dump"):
        from django_dump_die import functions  # noqa: PLC0415

        return getattr(functions, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
