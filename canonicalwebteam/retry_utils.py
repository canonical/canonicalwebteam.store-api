from typing import Callable, Tuple, Type, TypeVar
from random import uniform
from sys import maxsize as MAX_INT
import functools


P = TypeVar("P")
R = TypeVar("R")


def retry(
    func: Callable[P, R] = None,
    *,
    limit: int = MAX_INT,
    delay_fn: Callable[[int], float] = (lambda x: 0.0),
    sleep_fn: Callable[[float], None] = (lambda x: None),
    callback_fn: Callable[[Exception], bool] = (lambda x: False),
    logger_fn: Callable[[str], None] = (lambda x: None),
    exceptions: Tuple[Type[Exception]] = (Exception),
) -> Callable[P, R]:
    """
    Decorator that implements retry logic for `func` when any of the
    Exceptions in `exceptions` happen.

    Args:
        func (Callable[P, R], optional): The function that will be retried.
            Defaults to `None` when invoking the decorator using parameters,
            e.g. `@retry(limit=3)`).
        limit (int, optional): The maximum number of retry attempts.
            Defaults to `sys.maxsize`, allowing for a very large number of
            retries.
        delay_fn (Callable[[int], float], optional): A function that accepts
            the current attempt number (starting from 1) and returns a float
            representing the delay in seconds before the next call to `func`.
            Defaults to a function that always returns 0.0 (no delay).
        sleep_fn (Callable[[float], None], optional): A function that takes
            a float (delay in seconds) and pauses execution for that duration.
            Users are responsible for ensuring this function is appropriate
            for their environment (e.g., an async sleep for async contexts).
            Defaults to a function that performs no actual sleep.
        callback_fn (Callable[[Exception], bool], optional): A function that
            is called every time an exception from `exceptions` is caught
            during the retry loop. It receives the caught exception as an
            argument and should return `True` to abort the retry loop, or
            `False` to continue. Defaults to a function that always returns
            `False`.
        logger_fn (Callable[[str], None], optional): A function designed to
            log errors that are caught and handled (not propagated) during
            the retry loop. It's invoked each time an exception from
            `exceptions` is caught. Defaults to a function that performs no
            logging.
        exceptions (Tuple[Type[Exception]], optional): A tuple containing the
            types of exceptions that will trigger a retry. Defaults to
            `(Exception)`, meaning any standard exception will cause a retry.

    Returns:
        Callable[P, R]: A decorated version of the input function `func`
            that incorporates the defined retry logic. If `func` is initially
            `None` (when used as `@retry(...)`), it returns a decorator
            function ready to be applied to another callable.

    Raises:
        ValueError: if `limit` is less than 1
    """

    if func is None:
        # if the decorator is applied using parameters (e.g. @retry(limit=3)),
        # `func` will be None, so we must first do a partial application on
        # the decorator itself to actually wrap `func` correctly
        return functools.partial(
            retry,
            limit=limit,
            delay_fn=delay_fn,
            sleep_fn=sleep_fn,
            callback_fn=callback_fn,
            logger_fn=logger_fn,
            exceptions=exceptions,
        )

    if limit < 1:
        raise ValueError("The limit must be at least 1")

    @functools.wraps(func)
    def _retry(*args, **kwargs):
        retry_attempts = 0
        last_exception = None

        while retry_attempts < limit:
            if retry_attempts > 0:
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
                    f"@retry ({retry_attempts}/{limit}) `{func.__name__}`: {e}"
                )

        # if we made it here, it means we ran the loop and couldn't get a
        # clean run, raise the last exception we caught and let the user
        # deal with it
        raise last_exception

    return _retry


def delay_constant(d: float):
    """
    Create a constant delay function that always returns `d`.

    Args:
        d (float): The constant delay in seconds that the returned function
            will always provide.

    Returns:
        Callable[[int], float]: A function that takes an integer
            (representing the attempt number) and always returns the
            specified `d` float.

    Raises:
        ValueError: if `d` is negative
    """
    if d < 0:
        raise ValueError("The delay must be at least 0")

    def _delay_constant(_: int):
        return d

    return _delay_constant


def delay_random(min_delay: float, max_delay: float):
    """
    Create a random delay function that returns a random value between
    `min_delay` and `max_delay`.

    Args:
        min_delay (float): The minimum delay in seconds that the returned
            function will provide.
        max_delay (float): The maximum delay in seconds that the returned
            function will provide.

    Returns:
        Callable[[int], float]: A function that takes an integer
            (representing the attempt number) and returns a random float
            between `min_delay` and `max_delay`.

    Raises:
        ValueError: if `min` is negative
        ValueError: if `max` is less than or equal to `min`
    """

    if min_delay < 0:
        raise ValueError("The minimum delay must be at least 0")
    if max_delay <= min_delay:
        raise ValueError("The maximum delay must be greater than the minimum")

    def _delay_random(_: int):
        return uniform(min_delay, max_delay)

    return _delay_random


def delay_exponential(
    delay_mult: float, exp_base: float, max_delay: float = float("inf")
):
    """
    Create a function that implements an exponential backoff with an upper
    limit. The delay is calculated based on the number of attempts made `n`,
    according to the following formula:
        `min(max_delay, delay_mult * exp_base^n)`.

    Args:
        delay_mult (float): The multiplier for the exponential delay
            calculation. This value scales the base exponential growth.
        exp_base (float): The base of the exponent for the delay
            calculation. This determines how quickly the delay increases
            with each attempt.
        max_delay (float, optional): The upper limit for the delay in
            seconds. The calculated exponential delay will not exceed this
            value. Defaults to positive infinity.

    Returns:
        Callable[[int], float]: A function that takes an integer
            (representing the attempt number `n`) and returns a float
            indicating the calculated exponential delay.

    Raises:
        ValueError: if `delay_mult` is negative or zero
        ValueError: if `exp_base` is less than 1
        ValueError: if `max_delay` is negative
    """
    if delay_mult <= 0:
        raise ValueError("The delay multiplier must be greater than 0")
    if exp_base <= 1:
        raise ValueError("The exponential base must be greater than 1")
    if max_delay <= 0:
        raise ValueError("The maximum delay must be greater than 0")

    def _delay_exponential(attempt: int):
        return min(max_delay, delay_mult * (exp_base**attempt))

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
