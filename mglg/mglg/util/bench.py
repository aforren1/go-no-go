import timeit

# from https://github.com/mosra/magnum-bindings/blob/master/src/python/magnum/test/benchmark_math.py#L39
# TODO: funky when importing from elsewhere?


def timethat(expr, number=int(1e5), setup='pass', globs=globals()):
    title = expr
    print('{:60} {:8.5f} µs'.format(title, timeit.timeit(expr, number=number, globals=globs, setup=setup)*1000000.0/number))
