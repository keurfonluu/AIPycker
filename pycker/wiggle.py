# -*- coding: utf-8 -*-

"""
Author: Keurfon Luu <keurfon.luu@mines-paristech.fr>
License: MIT
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes

__all__ = [ "wiggle" ]


def wiggle(X, perc = 1., taxis = None, norm = True, fill = True, axes = None,
           figsize = (12, 8)):
    """
    Wiggle plot.
    
    Parameters
    ----------
    X : ndarray
        Seismic traces. Each row corresponds to a seismic record.
    perc : int or float, default 1.
        Maximum amplitude percentile for clipping. Only used if norm is True.
    taxis : ndarray or None, default None
        Time axis.
    norm : bool, default True
        Normalize seismic traces.
    fill : bool, default True
        Fill with black positive lobes.
    axes : matplotlib axes or None, default None
        Axes used for plot.
    figsize : tuple, default (12, 8)
        Figure width and height if axes is None.
    
    Returns
    -------
    ax1 : matplotlib axes
        Axes used for plot.
    """
    if not isinstance(X, np.ndarray) or X.ndim != 2:
        raise ValueError("X must be a 2-D ndarray")
    if not isinstance(perc, (int, float)) or perc < 0. or perc > 1.:
        raise ValueError("perc must be a float in [ 0, 1 ]")
    if taxis is not None and (not isinstance(taxis, np.ndarray) or taxis.ndim != 1):
        raise ValueError("taxis must be a 1-D ndarray")
    if not isinstance(norm, bool):
        raise ValueError("norm must be either True or False")
    if not isinstance(fill, bool):
        raise ValueError("fill must be either True or False")
    if axes is not None and not isinstance(axes, Axes):
        raise ValueError("axes must be Axes")
    if not isinstance(figsize, (list, tuple)) or len(figsize) != 2:
        raise ValueError("figsize must be a tuple with 2 elements")
        
    if axes is None:
        fig = plt.figure(figsize = figsize, facecolor = "white")
        ax1 = fig.add_subplot(1, 1, 1)
    else:
        ax1 = axes
        
    nrcv, npts = X.shape
    if taxis is None:
        taxis = np.arange(npts)
    
    if norm and perc < 1.:
        clip = np.percentile(np.abs(X.ravel()), perc * 100.)
        X_clip = np.clip(X, -clip, clip)
    else:
        X_clip = np.array(X)
        
    if norm:
        ymax = np.max(np.abs(X_clip))
    
    for k, tr in enumerate(X_clip):
        if not norm:
            ymax = np.max(np.abs(tr))
        x = tr / ymax + k + 1
        ax1.plot(x, taxis, color = "black", linewidth = 0.5)
        if fill: 
            ax1.fill_betweenx(taxis, x, k + 1, where = (x > k + 1), color = "black")
    
    ax1.set_xlabel("Trace number")
    ax1.set_xlim(0, nrcv+1)
    ax1.set_ylim(taxis[0], taxis[-1])
    ax1.invert_yaxis()
    return ax1