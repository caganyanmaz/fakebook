def init():
    pass


def true_func(x):
    return True


def first(iterable, cond=true_func):
    for i in iterable:
        if cond(i):
            return i
    return None


def modify(iterable, func):
    for item in iterable:
        yield(func(item))
