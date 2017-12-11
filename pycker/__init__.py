# -*- coding: utf-8 -*-

"""
Pycker provides user-friendly routines to visualize seismic traces and pick
first break arrival times.

Author: Keurfon Luu <keurfon.luu@mines-paristech.fr>
License: MIT
"""

from .pick import Pick
from .quantity_error import QuantityError
from .wiggle import wiggle
from .read_stream import StreamReader
from .gui import PyckerGUI

__version__ = "1.1.1"
__all__ = [ "Pick", "QuantityError", "wiggle", "StreamReader", "PyckerGUI" ]