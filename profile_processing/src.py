'''
Search profiles created by cProfile and extract data from them.
The class `ProfileStats` is a thin wrapper around the built-in `pstats.Stats` class implementing
some additional methods for searching and extraction.
'''
import re
from pstats import Stats
from functools import lru_cache
from typing import Sequence, Tuple


class ProfileStats(Stats):
    '''A convenience wrapper around `pstats.Stats`.'''

    @lru_cache
    def list_calls(self, *, full_info=False):
        '''A list of all functions in the profile.
        
        Kwargs:
            full_info (bool): If True, returns a list of keys, being tuples containing
                the file path, line number, and function name of each function call.
                If False only a list of function names is returned.
        '''
        if full_info:
            return list(self.stats.keys())
        else:
            return [k[2] for k in self.stats.keys()]

    def search_calls(
            self,
            name_pattern: str,
            line_number: int = None,
            path_pattern: str = None,
            *,
            unique_or_fail = False
        ) -> Sequence[Tuple]:
        '''A list of keys of the `stats` attribute, which match the given patterns.

        Args:
            name_pattern (str): matches the function name in `stats`. Can be a regex.
            line_number (int): matches the line number in `stats`.
            path_pattern (str): matches the file path in `stats`. Can be a regex.

        Kwargs:
            unique_or_fail (bool): If set to True an error is raised if the list of matching keys
                does not contain exactly one element.

        Returns:
            list[tuple]: A list of keys for the `stats` attribute.
        '''
        key_list = []
        for (path, line, name) in self.stats.keys():
            if not _matches(name_pattern, name):
                continue
            if line_number and line_number != line:
                continue
            if not _matches(path_pattern, path):
                continue
            key_list.append((path, line, name))

        if unique_or_fail and len(key_list) != 1:
            raise ValueError(f'More or less than one matching key was found: {key_list = }')

        return key_list

    def get_call(self, *, key=None, index=None):
        '''Retrieve a call from the profile either by providing the key for
        `stats` or by providing the index in the list of all calls. Instead of
        returning a tuple, as given in `stats`, a dictionary with informative
        key names is returned.

        Explanation of the keys:
            ncalls_prim: Number of primitive calls to the function (excluding recursive calls).
            ncalls: Number of all calls to the function.
            tottime: Total time spent within the function, across all calls.
            cumtime: Total time spent within the function and all subcalls, across all calls.
            callers: A dictionary of call keys and corresponding values of all functions that call
                the function. Note that keys again consist of length-three tuples, corresponding to
                file path, line number, and function name. The values consist of length-four tuples
                corresponding to number of primitive calls, number of calls, total time, and
                cumulative time.

        Kwargs:
            key (tuple): A valid key to `stats`.
            index (int): an index corresponding to the list of all calls.

        Note, that exactly one kwarg has to be specified!
        '''
        if not key and index is not None:
            keys = self.list_calls(full_info=True)
            key = keys[index]
        elif key and index is None:
            pass
        else:
            raise ValueError('Specify exactly one kwarg. Either key or index.')

        ncalls_prim, ncalls, tottime, cumtime, callers = self.stats[key]
        call_value = dict(
            ncalls_prim=ncalls_prim,
            ncalls=ncalls,
            tottime=tottime,
            cumtime=cumtime,
            callers=callers
        )
        return call_value


def get_call_stats(
    profile_path: str,
    name_pattern: str,
    line_number: int = None,
    path_pattern: str = None
    ):
    '''Quickly extract data from a specific call in a given profile.
    An error is raised if there was not a unique match for the patterns provided.

    Args:
        profile_path (str): path to the profile file to extract from.
        name_pattern (str): matches the function name in `stats`. Can be a regex.
        line_number (int): matches the line number in `stats`.
        path_pattern (str): matches the file path in `stats`. Can be a regex.
    
    Returns:
        dict: The statistics of the call. See `ProfileStats.get_call` for detailed information.
    '''
    profile = ProfileStats(profile_path)
    key = profile.search_calls(name_pattern, line_number, path_pattern, unique_or_fail=True)[0]
    return profile.get_call(key=key)


def _matches(pattern: str | None, string: str) -> bool:
    '''Whether pattern is contained in string. `None` always successfully matches.'''
    if not pattern:
        return True
    else:
        return bool(re.search(pattern, string))