from datetime import datetime, timedelta
from time import sleep

from collections.abc import Sequence
from functools import update_wrapper

from .pbar import pbar


class MatMulTrick:

    def __init__(self, func):
        self.func = func
        update_wrapper(self, datetime)

    def __repr__(self):
        return repr(self.func)

    def __matmul__(self, other):
        if isinstance(other, str):
            other = [int(i) for i in other.split(":")]
        if isinstance(other, Sequence):
            return self.func(*other)
        else:
            return self.func(other)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)



@MatMulTrick
def tomorrow(*args, **kwargs):
    return today(*args, **kwargs) + timedelta(days=1)

@MatMulTrick
def yesterday(*args, **kwargs):
    return today(*args, **kwargs) - timedelta(days=1)

@MatMulTrick
def today(*args, **kwargs):
    now = datetime.now()
    return datetime(now.year, now.month, now.day, *args, **kwargs)



def run_later(time, func, *args, **kwargs):
    """
    Runs func(*args, **kwargs) later
    time may be a datetime  object, which is forwarded to run_at
    time may be a timedelta object, which is forwarded to run_in
    if time is neither of the above, it is treated as seconds in a timedelta
    """

    if isinstance(time, datetime):
        return run_at(time, func, *args, **kwargs)
    else:
        if not isinstance(time, timedelta):
            time = timedelta(seconds=time)
        return run_in(time, func, *args, **kwargs)


def run_in(delta, func, *args, **kwargs):
    """
    Runs func(*args, **kwargs) in delta
    delta is assumed to be a timedelta object
    """

    assert isinstance(delta, timedelta)

    now = datetime.now()
    when = now + delta

    return run_at(when, func, *args, **kwargs)


def run_at(when, func, *args, **kwargs):
    """
    Runs func(*args, **kwargs) at when
    when is assumed to be a datetime object
    """

    assert isinstance(when, datetime)
    assert callable(func)

    now = datetime.now()
    print("it is currently   ", now)

    if now > when:
        print("it is already past", when)
        print("this was", now - when, "ago")
        return # raise NotImplementedError("time travel module missing")

    print("will run at       ", when)
    print("this will be in", when - now)

    start = datetime.now()
    total = when - start
    total_secs = total.total_seconds()

    with pbar(total=total_secs, description="Waiting to run later") as pb:
        while True:
            now = datetime.now()
            delta = now - start
            delta_secs = delta.total_seconds()
            pb.set(delta_secs)
            if now >= when:
                break
            sleep(0.1) # update bar at 10 Hz

    return func(*args, **kwargs)





if __name__ == "__main__":

    def fexample(a, b="default"):
        print("start!")
        print(a, b)
        sleep(0.5)
        print("done!")
        return "result!"


    res = run_later(11, fexample, 123, b=456)
    print(res)


    delta = -timedelta(minutes=1)
    res = run_in(delta, fexample, 123, b=456)
    print(res)

    delta = timedelta(minutes=0.2)
    res = run_in(delta, fexample, 123, b=456)
    print(res)


    when = yesterday(17, 25)
    res = run_at(when, fexample, 123, b=456)
    print(res)

    when = datetime.now() + timedelta(minutes=0.2)
    res = run_at(when, fexample, 123, b=456)
    print(res)

    when = tomorrow(7, 30)
    res = run_at(when, fexample, 123, b=456)
    print(res)



