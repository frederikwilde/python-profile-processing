# Python Profile Processing
This package helps with searching and extracting data within profiles created by the `cProfile` profiler in Python.
`ProfileStats` is a simple wrapper around the built-in `pstats.Stats` class in Python.

## Installation
The package can be locally pip installed via `pip install -e path/to/python-profile-processing`.

## Usage
Just as with `pstats.Stats`, the wrapping class `ProfileStats` can be instantiated by simply passing
the file path.

```Python
profile = profile_processing.ProfileStats('path/to/profile.prof')
profile.list_calls()
# Output:
#
# ["<method 'get' of 'dict' objects>",
# "<method 'items' of 'dict' objects>",
# ...
# '<module>']
```

The difference is you can search function calls with `search_calls()` and retrieve them with informative
dictionary keys (instead of a simple tuple) using `get_call()`.
The convencience function `get_call_stats()` allows you to extract a function call from a profile in only
one line of code:

```Python
call = profile_processing.get_call_stats(f'path/to/profile.prof', 'function_of_interest')
```

For more information have a look at the [demo notebook](https://github.com/frederikwilde/python-profile-processing/blob/main/demo/Python%20Profile%20Processing%20Demo.ipynb).
