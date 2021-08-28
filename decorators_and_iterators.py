'''
https://realpython.com/primer-on-python-decorators/#decorators-with-arguments
'''

import random, functools

def retry(n, exceptions=[...]):
    def decorator_repeat(func):
        @functools.wraps(func)
        def wrapper_repeat(*args, **kwargs):
            for _ in range(n):
                value = func(*args, **kwargs)
            return value
        return wrapper_repeat
    return decorator_repeat


@retry(n=3, exceptions=[ZeroDivisionError, TypeError])
def f(x, y):
  if random.random() > 0.5:
    return 1 / 0
  return x + y + 99


class MyIterator:
    '''
    https://stackoverflow.com/questions/19151/build-a-basic-python-iterator
    '''
    def __init__(self, low, high):
        self.current = low - 2
        self.high = high

    def __iter__(self):
        return self

    def __next__(self):
        self.current += 2
        if self.current < self.high:
            return self.current
        raise StopIteration



if __name__ == '__main__':

    for x in MyIterator(2, 17):
        print(x)

    try:
        f(2, 100)
    except Exception as e:
        print(e)

    try:
        f('a', [])
    except Exception as e:
        print(e)
