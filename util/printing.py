# Convenience utilities for printing

def pnd(n, duration, prefix=''):
    """Print an integer and a time duration, with an optional prefix."""
    prefix2 = prefix if len(prefix) == 0 else prefix+' '
    print('{:s}n: {:2d}, duration: {:6.3f} seconds'.format(prefix2, n, duration))

def pd(duration, prefix=''):
    """Print a time duration, with an optional prefix."""
    prefix2 = prefix if len(prefix) == 0 else prefix+' '
    print('{:s}duration: {:6.3f} seconds'.format(prefix2, duration))

