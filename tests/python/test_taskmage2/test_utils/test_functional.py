from taskmage2.utils import functional


class Test_pipeline:
    def test_single_item(self):
        pipeline = [lambda x: x + 1]
        result = list(functional.pipeline([1, 2, 3], pipeline))
        assert result == [2, 3, 4]

    def test_multiple_item(self):
        pipeline = [lambda x: x + 1, lambda x: x - 1]
        result = list(functional.pipeline([1, 2, 3], pipeline))
        assert result == [1, 2, 3]



class Test_multifilter:
    def test_single_filter(self):
        filters = [lambda x: x == 1]
        result = list(functional.multifilter(filters, [1, 2, 3]))
        assert result == [1]

    def test_multiple_filters(self):
        filters = [lambda x: x > 1, lambda x: x < 5]
        result = list(functional.multifilter(filters, [1, 2, 3, 4, 5]))
        assert result == [2, 3, 4]

