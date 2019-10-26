import functools


def pipeline(data, fn_list):
    """ Runs all functions in `fn_list` on `data` .
    Each is expected to return a new copy of `data` .
    """
    return functools.reduce(
        lambda a, x: map(x, a),
        fn_list,
        data,
    )


def multifilter(filters, result):
    """ Applies multiple filters to `result` .

    Returns:
        list:
            result, reduced by each filter.
    """
    if not filters:
        return result
    for f in filters:
        result = filter(f, result)
    return result


if __name__ == '__main__':  # pragma: no cover
    def example():
        def above_ten(num):
            return num > 10

        def below_fifteen(num):
            return num < 15

        filters = [above_ten, below_fifteen]
        result = multifilter(filters, range(20))
        print(result)

    example()
