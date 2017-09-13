# -*- coding: utf-8 -*-

"""
Run Pycker Viewer to visualize seismic traces and/or pick first break arrival
times.

Author: Keurfon Luu <keurfon.luu@mines-paristech.fr>
License: MIT
"""

try:
    from pycker.gui import main
except ImportError:
    import sys
    sys.path.append("../")
    from pycker.gui import main


if __name__ == "__main__":
    main()