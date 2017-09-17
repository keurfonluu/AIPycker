# -*- coding: utf-8 -*-

"""
Author: Keurfon Luu <keurfon.luu@mines-paristech.fr>
License: MIT
"""

import os
from obspy import read

__all__ = [ "StreamReader" ]


class StreamReader:
    """
    Read streamer files.
    """
    
    FORMATS = [ "miniseed", "mseed", "reftek", "sac", "seg2", "sg2", "segy", "sgy", "su" ]
    
    def __init__(self):
        pass
    
    def format_ok(self, filename):
        """
        Check if file's format is compatible.
        
        Parameters
        ----------
        filename : str
            Path to file.
            
        Returns
        -------
        ok : bool
            True if file is compatible, False otherwise.
        """
        ext = os.path.splitext(filename)[1][1:].lower()
        if ext not in self.FORMATS:
            return False
        else:
            return True
        
    def read_dir(self, dirname):
        """
        Read directory.
        
        Parameters
        ----------
        dirname : str
            Path to directory containing stream files.
            
        Returns
        -------
        file_list : list
            List of filenames.
        """
        filenames = os.listdir(dirname)
        filenames.sort()
        file_list = []
        for filename in filenames:
            if os.path.isfile(dirname + filename) and self.format_ok(filename):
                file_list.append(filename)
        return file_list
    
    def read_file(self, filename):
        """
        Read file.
        
        Parameters
        ----------
        filename : str
            Path to file.
            
        Returns
        -------
        st : Stream
            List of Trace objects.
        """
        ext = os.path.splitext(filename)[1][1:].lower()
        if ext in [ "miniseed", "mseed" ]:
            st = read(filename, format = "MSEED")
        elif ext == "reftek":
            st = read(filename, format = "REFTEK130")
        elif ext == "sac":
            st = read(filename, format = "SAC")
        elif ext in [ "seg2", "sg2" ]:
            st = read(filename, format = "SEG2")
        elif ext in [ "segy", "sgy" ]:
            st = read(filename, format = "SEGY")
        elif ext == "su":
            st = read(filename, format = "SU")
        return st