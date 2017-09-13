# -*- coding: utf-8 -*-

"""
Author: Keurfon Luu <keurfon.luu@mines-paristech.fr>
License: MIT
"""

from obspy.core.utcdatetime import UTCDateTime
from .quantity_error import QuantityError

__all__ = [ "Pick" ]


class Pick:
    """
    A pick is the observation of an amplitude anomaly in a seismogram at a
    specific point in time. It is not necessarily related to a seismic event.
    
    Parameters
    ----------
    time : scalar or None, default None
        Observed onset time of signal (“pick time”).
    index : int or float or None, default None
        Corresponding index on trace.
    time_errors : QuantityError
        Observed onset time of signal uncertainties.
    phase_hint : str or None, default None
        Tentative phase identification as specified by the picker.
    """
    
    _ATTRIBUTES = [ "time", "index", "time_errors", "phase_hint" ]
    
    def __init__(self, time = None, index = None, time_errors = QuantityError(),
                 phase_hint = None):
        if time is not None and not isinstance(time, (float, UTCDateTime)):
            raise ValueError("time must be a float or UTCDateTime")
        else:
            self._time = time
        if index is not None and not isinstance(index, (int, float)):
            raise ValueError("index must be an integer or float")
        else:
            self._index = index
        if not isinstance(time_errors, QuantityError):
            raise ValueError("time_errors must be QuantityError")
        else:
            self._time_errors = time_errors
        if phase_hint is not None and not isinstance(phase_hint, str):
            raise ValueError("phase_hint must be a string")
        else:
            self._phase_hint = phase_hint
            
    def __repr__(self):
        attributes = [ "%s: %s" % (attr.rjust(13), self._print_attr(attr))
                        for attr in self._ATTRIBUTES ]
        return "\n".join(attributes) + "\n"        
            
    def _print_attr(self, attr):
        if attr not in self._ATTRIBUTES:
            raise ValueError("error_type should be either 'time', 'index', 'time_errors' or 'phase_hint'")
        else:
            if attr == "time":
                return self._time
            elif attr == "index":
                return self._index
            elif attr == "time_errors":
                return self._time_errors
            elif attr == "phase_hint":
                return self._phase_hint
        
    @property
    def time(self):
        """
        scalar or None
        Observed onset time of signal (“pick time”).
        """
        return self._time
    
    @time.setter
    def time(self, value):
        self._time = value
    
    @property
    def index(self):
        """
        int or None
        Corresponding index on trace.
        """
        return self._index
    
    @index.setter
    def index(self, value):
        self._index = value
    
    @property
    def time_errors(self):
        """
        QuantityError
        Observed onset time of signal uncertainties.
        """
        return self._time_errors
    
    @time_errors.setter
    def time_errors(self, value):
        self._time_errors = value
        
    @property
    def phase_hint(self):
        """
        str or None
        Tentative phase identification as specified by the picker.
        """
        return self._phase_hint
    
    @phase_hint.setter
    def phase_hint(self, value):
        self._phase_hint = value