from typing import Callable, List, Tuple, Type, TypeVar
from random import random
from time import sleep
from sys import maxsize as MAX_INT
import functools


P = TypeVar('P')
R = TypeVar('R')


def retry(func: Callable[P, R] = None, *,
          limit: int = MAX_INT,
          delay_fn: Callable[[int], float] = (lambda x: 0.0),
          sleep_fn: Callable[[float], None] = (lambda x: None),
          callback_fn: Callable[[Exception], bool] = (lambda x: False),
          logger_fn: Callable[[str], None] = (lambda x: None),
          exceptions: Tuple[Type[Exception]] = (Exception)) -> Callable[P, R]:
    """
    Decorator that implements retry logic for `func` when any of the
    Exceptions in `exceptions` happen.

    Arguments:
    func: function what will be retried

    Keyword arguments:
    limit: max number of retry attempts
    exceptions: tuple containing the types of exceptions we can catch and
        that trigger a retry
    callback_fn: function that takes as argument an exception caught a during
        the retry loop, it should return a bool indicating whether to abort 
        the loop or not; it will be called every time a member of `exceptions`
        is caught
    logger_fn: function that logs errors caught and not propagated during
        the retry loop; it will be called every time a member of `exceptions`
        is caught
    delay_fn: function that takes the current attempt as an argument and
        returns a float indicating the delay in seconds before calling `func`
        again
    sleep_fn: function that takes a float indicating a delay in seconds and
        waits for this specified time before executing `func` again; it's
        user's responsibility to make sure the sleep function is appropriate
        for their usage (e.g. use an async sleep in and async environment)
    """

    if func is None:
        # if this decorator is applied using the @ syntax, `func` will not
        # be defined correctly, so we must do a partial application to wrap
        # `func` correctly
        return functools.partial(retry,
                                 limit=limit,
                                 delay_fn=delay_fn,
                                 sleep_fn=sleep_fn,
                                 callback_fn=callback_fn,
                                 logger_fn=logger_fn,
                                 exceptions=exceptions)

    if limit <= 0:
        raise ValueError("The limit must be at least 1")

    @functools.wraps(func)
    def _retry(*args, **kwargs):
        retry_attempts = 0
        last_exception = None

        while retry_attempts < limit:
            if (retry_attempts > 0):
                # only sleep if we've already tried once
                sleep_fn(delay_fn(retry_attempts))

            try:
                return func(*args, **kwargs)
            except exceptions as e:
                last_exception = e
                retry_attempts += 1

                if callback_fn(e):
                    # stop early if callback says so, raise `e` immediately
                    raise e

                logger_fn(
                    f"@retry ({retry_attempts}/{limit}) `{func.__name__}`: {e}")

        # if we made it here, it means we ran the loop and couldn't get a
        # clean run, raise the last exception we caught and let the user
        # deal with it
        raise last_exception

    return _retry


def delay_random(min: float, max: float):
    """
    Returns a function that picks a random delay between `min` and `max`
    """
    if min < 0:
        raise ValueError("The minimum delay must be at least 0")
    if max <= min:
        raise ValueError("The maximum delay must be greater than the minimum")

    def _delay_random(_: int):
        return min + random() * (max - min)

    return _delay_random


def delay_exponential(delay_mult: float, exp_base: float, max_delay: float = float('inf')):
    """
    Returns a function that implements an exponential backoff with an upper
    limit based on the number of attempts made `n`, according to the following
    formula:
        min(`max_delay`, `delay_mult` * `exp_base`^`n`)
    """
    if delay_mult <= 0:
        raise ValueError("The delay multiplier must be greater than 0")
    if exp_base <= 1:
        raise ValueError("The exponential base must be greater than 1")
    if max_delay <= 0:
        raise ValueError("The maximum delay must be greater than 0")

    def _delay_exponential(attempt: int):
        return min(max_delay, delay_mult * (exp_base ** attempt))

    return _delay_exponential


"""
Example usage:

    @retry(
        limit=5,
        logger_fn=print,
        exceptions=(TypeError),
        sleep_fn=sleep,
        delay_fn=delay_exponential(1, 2)
    )
    def test_fn(val: int):
        return None + val  # this will raise TypeError

    try:
        test_fn(2)
    except TypeError as e:
        print(e)

This will attempt to run `test_fn` 5 times, will catch TypeError 4 times and
then it will let the exception propagate after executing the function for the
last time. Each time, it will take an exponentially longer amount of time to
run, making the total execution time around 30s (plus some small random delay
caused by the OS).
"""
