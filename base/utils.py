import itertools


def chunks(iterable, n):
    """Split iterable into chunks with n or fewer items."""
    it = iter(iterable)
    while True:
        chunk = itertools.islice(it, n)
        try:
            first_item = next(chunk)
        except StopIteration:
            return
        yield itertools.chain((first_item,), chunk)
