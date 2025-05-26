import time
from functools import wraps
from logging import Logger
from typing import Any, Callable, TypeVar

FuncT = TypeVar("FuncT", bound=Callable[..., Any])


def timeit(logger: Logger) -> Callable[[FuncT], FuncT]:
    """
    Decorator that logs the execution time of a function to the log stream.
    """

    def decorate(func: FuncT) -> FuncT:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            result = func(*args, **kwargs)
            end = time.perf_counter()
            logger.info(f"{func.__name__} took {end - start:.6f} seconds to complete")
            return result

        return wrapper

    return decorate
