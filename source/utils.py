from dataclasses import dataclass, field, asdict
from functools import wraps

def move_to_utils(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        print(f"The object {f.__name__} should be moved to utils")
        return f(*args, **kwargs)
    return wrapper
    
