from vcr_unittest import VCRTestCase
from canonicalwebteam.retry_utils import retry


LIMIT = 5


class Counter:
    """
    Simple class that implements a counter
    """

    def __init__(self, n: int = 0):
        self.counter = n

    def increment(self, *args):
        self.counter = self.counter + 1


class RetryDecoratorTest(VCRTestCase):
    def test_bad_limit(self):
        with self.assertRaises(ValueError):

            @retry(limit=-1)
            def noop():
                pass

    def test_no_exception(self):
        @retry()
        def noop():
            pass

        noop()  # this should never trigger an exception

    def test_callback_fn(self):
        def callback(e: Exception):
            self.assertIsInstance(e, TypeError)

        @retry(limit=LIMIT, callback_fn=callback)
        def wrapper():
            raise Exception("Exception")

        with self.assertRaises(Exception):
            # last execution will raise Exception
            wrapper()

    def test_logger_fn(self):
        def logger(e: str):
            self.assertIsInstance(e, str)
            self.assertTrue(e.startswith("@retry"))

        @retry(limit=LIMIT, logger_fn=logger)
        def wrapper():
            raise Exception("Exception")

        with self.assertRaises(Exception):
            # last execution will raise Exception
            wrapper()

    def test_retry_limit(self):
        c = Counter()

        @retry(limit=LIMIT, callback_fn=c.increment)
        def wrapper():
            raise Exception("Exception")

        with self.assertRaises(Exception):
            # last execution will raise Exception
            wrapper()

        self.assertEqual(c.counter, LIMIT)

    def test_good_exception_match(self):
        c = Counter()

        @retry(limit=LIMIT, callback_fn=c.increment, exceptions=(TypeError))
        def wrapper():
            raise TypeError("Exception")

        with self.assertRaises(TypeError):
            # last execution will raise TypeError
            wrapper()

        self.assertEqual(c.counter, LIMIT)

    def test_bad_exception_match(self):
        @retry(limit=LIMIT, exceptions=(TypeError))
        def wrapper():
            raise ValueError("Exception")

        with self.assertRaises(ValueError):
            # exception types don't match so ValueError is propagated
            wrapper()

    def test_delay_fn(self):
        c = Counter(1)

        def delay(x: int):
            self.assertEqual(x, c.counter)
            c.increment()
            return 0.0

        @retry(limit=LIMIT, delay_fn=delay, exceptions=(TypeError))
        def wrapper():
            raise Exception("Exception")

        with self.assertRaises(Exception):
            # last execution will raise TypeError
            wrapper()

    def test_sleep_fn(self):
        c = Counter()

        def sleep(x: float):
            c.increment()
            self.assertEqual(x, float(c.counter))

        @retry(
            limit=LIMIT,
            exceptions=(Exception),
            delay_fn=(lambda x: float(x)),
            sleep_fn=sleep,
        )
        def wrapper():
            raise Exception("Exception")

        with self.assertRaises(Exception):
            # last execution will raise TypeError
            wrapper()

        # sleep only happens *between* calls
        self.assertEqual(c.counter, LIMIT - 1)
