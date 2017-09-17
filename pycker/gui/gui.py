# -*- coding: utf-8 -*-

"""
Pycker Viewer provides a GUI to visualize seismic traces and manually pick
first break arrival times.

Author: Keurfon Luu <keurfon.luu@mines-paristech.fr>
License: MIT
"""

from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import FormatStrFormatter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

from obspy.signal.filter import lowpass, highpass

import numpy as np
from ..pick import Pick
from ..wiggle import wiggle
from ..read_stream import StreamReader

import os, sys
if sys.version_info[0] < 3:
    import Tkinter as tk
    import tkFileDialog as tkfile
    import tkMessageBox as tkmessage
    import ttk
    import tkFont as font
else:
    import tkinter as tk
    import tkinter.filedialog as tkfile
    import tkinter.messagebox as tkmessage
    import tkinter.ttk as ttk
    from tkinter import font
from .ttk_spinbox import Spinbox
    
try:
    import cPickle as pickle
except ImportError:
    import pickle
    
__all__ = [ "PyckerGUI", "main" ]


class PyckerGUI():
    """
    GUI for Pycker.
    
    Pycker Viewer provides a GUI to visualize seismic traces and manually pick
    first break arrival times. 
    
    Parameters
    ----------
    master : tkinter object
        tkinter root window.
    ncolumn : int, default 2
        Number of columns in non-gather plot.
    """
    
    master = None
    picks = None
    _first_import = True
    _current_file = None
    _current_index = None
    UNITS = [ "samples", "s", "ms", "us" ]
    
    def __init__(self, master, ncolumn = 2):
        self._ncolumn = ncolumn
        self.master = master
        master.title("Pycker Viewer")
        master.protocol("WM_DELETE_WINDOW", self.close_window)
        master.geometry("1200x700")
        master.minsize(1200, 700)
        
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family = "Helvetica", size = 9)
        master.option_add("*Font", default_font)
        
        self._stread = StreamReader()
        self.define_variables()
        self.trace_variables()
        self.init_variables()
        self.init_containers()
        self.menubar()
        self.init_frame1()
        self.init_frame2()
        self.init_frame3()
        self.footer()
    
    def about(self):
        about = "Pycker Viewer 1.0" + "\n" \
                + "A picker program for first break arrival times" + "\n\n" \
                + "Created by Keurfon Luu"
        tkmessage.showinfo("About", about)
        
    def menubar(self):
        menubar = tk.Menu(self.master)
        
        # File
        filemenu = tk.Menu(menubar, tearoff = 0)
        filemenu.add_command(label = "Import all picks", command = self.import_all_picks)
        filemenu.add_separator()
        filemenu.add_command(label = "Export current pick", command = self.export_current_pick)
        filemenu.add_command(label = "Export all picks", command = self.export_all_picks)
        filemenu.add_separator()
        filemenu.add_command(label = "Exit", command = self.close_window)
        
        # View
        viewmenu = tk.Menu(menubar, tearoff = 0)
        viewmenu.add_checkbutton(label = "Gather", onvalue = 1, offvalue = 0, variable = self.plot_type, command = self.plot)
        viewmenu.add_checkbutton(label = "Fill", onvalue = 1, offvalue = 0, variable = self.fill, command = self.plot)
        
        # Time axis
        taxismenu = tk.Menu(viewmenu, tearoff = 0)
        taxismenu.add_checkbutton(label = "Seconds", onvalue = 1, offvalue = 0, variable = self.taxis_seconds, command = self._set_taxis_seconds)
        taxismenu.add_checkbutton(label = "Samples", onvalue = 1, offvalue = 0, variable = self.taxis_samples, command = self._set_taxis_samples)
        
        # Help
        helpmenu = tk.Menu(menubar, tearoff = 0)
        helpmenu.add_command(label = "About", command = self.about)
        
        # Display menu bar
        menubar.add_cascade(label = "File", menu = filemenu)
        menubar.add_cascade(label = "View", menu = viewmenu)
        menubar.add_cascade(label = "Help", menu = helpmenu)
        viewmenu.add_cascade(label = "Time axis", menu = taxismenu)
        self.master.config(menu = menubar)
        
    def init_containers(self):
        self.root_container = ttk.Frame(self.master)
        self.root_container.place(relwidth = 1, relheight = 1, anchor = "nw")
        self.root_container.grid_rowconfigure(0, weight = 1)
        self.root_container.grid_columnconfigure(0, weight = 1)
        self.footer_container = ttk.Frame(self.root_container, width = 300, height = 35)
        self.footer_container.grid(row = 1, column = 0, sticky = "ew")
        self.main_container = ttk.Frame(self.root_container, width = 300, height = 300)
        self.main_container.grid(row = 0, column = 0, sticky = "nsew")
        self.main_container.grid_rowconfigure(0, weight = 1)
        self.main_container.grid_columnconfigure(1, weight = 1)
        self.data_container = ttk.Frame(self.main_container, width = 300, height = 300)
        self.data_container.grid(row = 0, column = 0, padx = 5, sticky = "ns")
        self.data_container.grid_rowconfigure(1, weight = 1)
        self.data_container.grid_columnconfigure(0, weight = 1)
        self.canvas_container = ttk.LabelFrame(self.main_container, text = "Traces", width = 300, height = 300)
        self.canvas_container.grid(row = 0, column = 1, padx = 5, sticky = "nsew")
        
    def init_frame1(self):
        self.frame1 = ttk.LabelFrame(self.data_container, text = "Data", borderwidth = 2, relief = "groove", width = 330, height = 250)
        self.frame1.grid_columnconfigure(0, weight = 1)
        self.frame1.grid_rowconfigure(0, weight = 1)
        self.frame1.grid(row = 0, column = 0)
        
        # directory
        data_label = ttk.Label(self.frame1, text = "Directory")
        data_entry = ttk.Entry(self.frame1, width = 25, textvariable = self.input_dirname,
                               takefocus = True)
        data_import_button = ttk.Button(self.frame1, text = "Import", command = self.import_traces,
                                        takefocus = False)
        
        # norm
        norm_button = ttk.Checkbutton(self.frame1, text = "Normalize", variable = self.normalize,
                                      takefocus = False)
        norm_spinbox = Spinbox(self.frame1, from_ = 0.01, to_ = 1., increment = 0.01, textvariable = self.perc,
                               width = 7, justify = "right", takefocus = True)
        
        # sampling_rate
        fs_button = ttk.Checkbutton(self.frame1, text = "Sampling rate (Hz)", variable = self.enforce_fs,
                                    takefocus = False)
        fs_entry = ttk.Entry(self.frame1, width = 10, textvariable = self.sampling_rate,
                             justify = "right", takefocus = True)  
        
        # low
        low_button = ttk.Checkbutton(self.frame1, text = "Lowpass (Hz)", variable = self.lowpass,
                                     takefocus = False)
        low_entry = ttk.Entry(self.frame1, width = 10, textvariable = self.lpcut,
                              justify = "right", takefocus = True)
        
        # high
        high_button = ttk.Checkbutton(self.frame1, text = "Highpass (Hz)", variable = self.highpass,
                                      takefocus = False)
        high_entry = ttk.Entry(self.frame1, width = 10, textvariable = self.hpcut,
                               justify = "right", takefocus = True)     
        
        # delay
        delay_button = ttk.Checkbutton(self.frame1, text = "Delay", variable = self.delay,
                                       takefocus = False)
        delay_entry = ttk.Entry(self.frame1, width = 6, textvariable = self.delay_val,
                                justify = "right", takefocus = True)
        delay_option_menu = ttk.OptionMenu(self.frame1, self.delay_unit, self.delay_unit.get(), *self.UNITS)
        delay_option_menu.config(width = 7)
        
        # apply
        apply_button = ttk.Button(self.frame1, text = "Apply", command = self.apply,
                                  takefocus = False)
        
        # Layout
        data_label.grid(row = 0, column = 0, padx = 5, sticky = "sw")
        data_entry.grid(row = 1, column = 0, columnspan = 2, padx = 5, pady = 5, sticky = "we")
        data_import_button.grid(row = 1, column = 2, padx = 5, pady = 5, sticky = "e")
        norm_button.grid(row = 2, column = 0, padx = 5, pady = 1, sticky = "w")
        norm_spinbox.grid(row = 2, column = 2, ipadx = 8, padx = 5, pady = 1)
        fs_button.grid(row = 3, column = 0, padx = 5, pady = 1, sticky = "w")
        fs_entry.grid(row = 3, column = 2, padx = 5, pady = 1)
        low_button.grid(row = 4, column = 0, padx = 5, pady = 1, sticky = "w")
        low_entry.grid(row = 4, column = 2, padx = 5, pady = 1)
        high_button.grid(row = 5, column = 0, padx = 5, pady = 1, sticky = "w")
        high_entry.grid(row = 5, column = 2, padx = 5, pady = 1)
        delay_button.grid(row = 6, column = 0, padx = 5, pady = 1, sticky = "w")
        delay_entry.grid(row = 6, column = 1, padx = 5, pady = 1)
        delay_option_menu.grid(row = 6, column = 2, padx = 5, pady = 1, sticky = "ew")
        apply_button.grid(row = 7, column = 2, padx = 5, pady = 5, sticky = "se")

    def init_frame2(self):
        self.frame2 = ttk.LabelFrame(self.data_container, text = "Files", borderwidth = 2, relief = "groove", width = 100, height = 100)
        self.frame2.grid(row = 1, column = 0, sticky = "nsew")
        
    def init_frame3(self):
        self.frame3 = ttk.Frame(self.canvas_container, borderwidth = 0)
        self.frame3.pack()
        self.fig = Figure(figsize = (12, 8), facecolor = "white", dpi = 150)
        self.canvas = FigureCanvasTkAgg(self.fig, master = self.frame3)
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.frame3)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack()
        self.toolbar.pack(side = "top", fill = "both", expand = 1)
        self.canvas.mpl_connect("pick_event", self.OnPick)

    def footer(self):
        # exit
        exit_button = ttk.Button(self.footer_container, text = "Exit", command = self.close_window)
        exit_button.place(width = 100, relx = 1, rely = 1, x = -5, y = -5, anchor = "se")

    def close_window(self):
        yes = tkmessage.askyesno("Exit", "Do you really want to exit?")
        if yes:
            self.close()

    def import_traces(self):
        dirname = tkfile.askdirectory(title = "Open data directory",
                                      initialdir = os.getcwd(),
                                      )
        if len(dirname) > 0:
            dirname += "/"
            self.input_dirname.set(dirname)
            self.fig.clear()
            self.canvas.draw()
            
            if not self._first_import:
                self.frame2.forget()
                self._current_file = None
                self._current_index = None
            else:
                self._first_import = False
            self.init_frame2()
            
            # List all files in data directory
            self._filenames = self._stread.read_dir(dirname)
            nsrc = len(self._filenames)
            self.picks = [ None ] * nsrc
            
            if nsrc < 1:
                tkmessage.showerror("Error", "Chosen directory is empty or contains incompatible files.")
                self.input_dirname.set("")
                pass
            else:
                # Scrollbar
                scrollbar = ttk.Scrollbar(self.frame2)
                scrollbar.pack(side = "right", fill = "y")        
                
                # Listbox
                event_list = tk.Listbox(self.frame2, yscrollcommand = scrollbar.set)
                for item in self._filenames:
                    event_list.insert(tk.END, item)
                event_list.bind("<Double-Button-1>", self.OnDoubleClick)
                event_list.bind("<Down>", self.OnEntryDown)
                event_list.bind("<Up>", self.OnEntryUp)
        
                # Layout
                event_list.pack(expand = "y", fill = "both")
                scrollbar.config(command = event_list.yview)

    def apply(self):
        if self._current_file is None:
            tkmessage.showerror("Error", "No event chosen yet.")
        else:
            self._read_traces()
            self._filter_traces()
            self.plot()
    
    def plot(self):
        if self._current_index is not None:
            self._axlines = [ None ] * self._shape[0]
            self.view_seismogram()
            self.view_pick()
    
    def view_seismogram(self):
        self.fig.clear()
        nrcv, npts = self._shape
        if self.delay.get():
            tmin = -self._delay2samples()
            t = np.linspace(tmin, npts+tmin-1, npts)
        else:
            tmin = 0.
            t = np.arange(npts, dtype = float)
        if self.taxis_seconds.get():
            t /= self.sampling_rate.get()
            ylabel = "Time (s)"
        else:
            ylabel = "Time (samples)"
        if self.plot_type.get() == 0:
            nr = int(np.ceil(nrcv/self._ncolumn))
            gs = GridSpec(nr, self._ncolumn)
            self.ax1 = [ self.fig.add_subplot(gs[k%nr,k//nr]) for k in range(nrcv) ]
            if self.normalize.get() and self.perc.get() < 1.:
                clip = np.percentile(np.abs(self._traces.ravel()), self.perc.get() * 100.)
                X_clip = np.clip(self._traces, -clip, clip)
            else:
                X_clip = np.array(self._traces)
            if self.normalize.get():
                ymax = np.max(np.abs(X_clip))
            for k, (ax, tr) in enumerate(zip(self.ax1, X_clip)):
                if not self.normalize.get():
                    ymax = np.max(np.abs(tr))
                ax.plot(t, tr, color = "black", linewidth = 0.5)
                if self.fill.get():
                    ax.fill_between(t, tr, 0, where = (tr > 0), color = "black")
                ax.text(0, 1, "Receiver " + str(k+1), fontsize = 6, ha = "left", va = "bottom", transform = ax.transAxes)
                ax.set_xlim(max(tmin, 0.), t[-1])
                ax.get_xaxis().set_visible(False)
                ax.set_ylim(-ymax, ymax)
                ax.set_yticks([ -ymax, 0, ymax ])
                ax.set_yticklabels([ -ymax, 0, ymax ], fontsize = 6)
                ax.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
                ax.set_picker(True)
        else:
            self.ax1 = self.fig.add_subplot(1, 1, 1)
            self.ax1 = wiggle(self._traces, perc = self.perc.get(), taxis = t,
                              norm = self.normalize.get(), fill = self.fill.get(),
                              axes = self.ax1)
            self.ax1.set_ylabel(ylabel)
            self.ax1.set_ylim(max(tmin, 0.), t[-1])
            self.ax1.invert_yaxis()
            self.ax1.set_picker(True)
        self.fig.suptitle(self._starttime, fontsize = 8, va = "bottom", ha = "left", position = (0.01, 0.01))
        self.fig.tight_layout()
        self.canvas.draw()
        
    def view_pick(self):
        if self.plot_type.get() == 0:
            for k, pick in enumerate(self.picks[self._current_index]):
                if pick is not None and pick.index is not None:
                    idx = (pick.time - self._starttime) * pick.sampling_rate + pick.shift
                    if self.delay.get():
                        idx -= self._delay2samples()
                    if self.taxis_seconds.get():
                        idx /= self.sampling_rate.get()
                        title = "Pick = %s" % self._tobs2str(idx)
                    else:
                        title = "Pick = %s" % self._tobs2str(idx / self.sampling_rate.get())
                    if self._axlines[k] is None:
                        self._axlines[k] = self.ax1[k].axvline(idx, color = "red", linewidth = 0.5)
                    else:
                        self._axlines[k].set_xdata([idx, idx])
                        self._axlines[k].set_visible(True)
                    if len(self.ax1[k].patches) != 0:
                        self.ax1[k].patches = []
                    self.ax1[k].set_title(title, fontsize = 6, va = "top", ha = "right", position = (1, 1.05))
        else:
            for k, pick in enumerate(self.picks[self._current_index]):
                if pick is not None and pick.index is not None:
                    idx = (pick.time - self._starttime) * pick.sampling_rate + pick.shift
                    if self.delay.get():
                        idx -= self._delay2samples()
                    if self.taxis_seconds.get():
                        idx /= self.sampling_rate.get()
                    if self._axlines[k] is None:
                        self._axlines[k], = self.ax1.plot([k+0.5, k+1.5], [idx, idx], color = "red", linewidth = 0.5)
                    else:
                        self._axlines[k].set_ydata([idx, idx])
                        self._axlines[k].set_visible(True)
        self.canvas.draw()
        
    def export_current_pick(self):
        if self.picks is not None and self._current_index is not None \
            and self.picks[self._current_index] is not None:
            filename = tkfile.asksaveasfilename(title = "Export current pick",
                                                initialdir = os.getcwd(),
                                                filetypes = [ ("ASCII", ".txt") ],
                                                defaultextension = ".txt",
                                                )
            if len(filename) > 0:
                idx = [ pick.index if (pick is not None and pick.index is not None) else -5e-3 \
                       for pick in self.picks[self._current_index] ]
                np.savetxt(filename, idx, fmt = "%.3f")
        else:
            tkmessage.showerror("Error", "No pick to export.")
    
    def export_all_picks(self):
        if self.picks is not None and not np.all([ pick is None for pick in self.picks ]):
            filename = tkfile.asksaveasfilename(title = "Export all picks",
                                                initialdir = os.getcwd(),
                                                filetypes = [ ("Pickle", ".pickle") ],
                                                defaultextension = ".pickle",
                                                )
            if len(filename) > 0:
                with open(filename, "wb") as f:
                    pickle.dump(self.picks, f, protocol = pickle.HIGHEST_PROTOCOL)
        else:
            tkmessage.showerror("Error", "No pick to export.")
    
    def import_all_picks(self):
        if self.picks is not None:
            filename = tkfile.askopenfilename(title = "Import all picks",
                                              initialdir = os.getcwd(),
                                              filetypes = [ ("Pickle", ".pickle") ],
                                              defaultextension = ".pickle",
                                              )
            if len(filename) > 0:
                with open(filename, "rb") as f:
                    picks = pickle.load(f)
                if len(self.picks) == len(picks):
                    self.picks = picks
                    self.plot()
                else:
                    tkmessage.showerror("Error", "Picks does not match imported data.")
        else:
            tkmessage.showerror("Error", "No data imported.")
    
    def OnDoubleClick(self, event):
        widget = event.widget
        selection = widget.curselection()
        filename = widget.get(selection[0])
        self._read(filename)
        
    def OnEntryDown(self, event):
        if self._current_index is not None and self._current_index < len(self._filenames)-1:
            self._current_index += 1
            self._current_file = self._filenames[self._current_index]
            self._read(self._current_file)
        
    def OnEntryUp(self, event):
        if self._current_index is not None and self._current_index > 0:
            self._current_index -= 1
            self._current_file = self._filenames[self._current_index]
            self._read(self._current_file)
    
    def OnPick(self, event):
        nrcv = self._shape[0]
        if self.plot_type.get() == 0:
            for k in range(nrcv):
                if event.artist == self.ax1[k]:
                    break
        else:
            rcv = np.arange(nrcv+1)
            idx = max(min(nrcv, np.argmin(np.abs(event.mouseevent.xdata - rcv))), 1)
            k = int(rcv[int(idx)] - 1)
        if event.mouseevent.button == 1:
            if self.plot_type.get() == 0:
                self._man_pick(k, event.mouseevent.xdata)
            else:
                self._man_pick(k, event.mouseevent.ydata)
            self.view_pick()
        elif event.mouseevent.button == 2:
            self.picks[self._current_index][k] = None
            self._axlines[k].set_visible(False)
            if self.plot_type.get() == 0:
                self.ax1[k].set_title("")
                if len(self.ax1[k].patches) != 0:
                    self.ax1[k].patches = []
        elif event.mouseevent.button == 3:
            if self.plot_type.get() == 0:
                idx = event.mouseevent.xdata
            else:
                idx = event.mouseevent.ydata
            if self.taxis_seconds.get():
                string = "%d %.3f %s" % (k+1, idx * self.sampling_rate.get(), idx)
            else:
                string = "%d %.3f %s" % (k+1, idx, idx / self.sampling_rate.get())
            print(string)
        self.canvas.draw()
    
    def _read_traces(self):
        st = self._stread.read_file(self.input_dirname.get() + self._current_file)
        self._starttime = st[0].stats.starttime
        self._traces = np.array([ tr.detrend("constant") for tr in st.traces ])
        self._shape = self._traces.shape
        if not self.enforce_fs.get():
            self.sampling_rate.set(st[0].stats.sampling_rate)
        if self.picks[self._current_index] is None:
            self.picks[self._current_index] = [ None ] * self._shape[0]
        
    def _filter_traces(self):
        if self.lpcut.get() > self.sampling_rate.get():
            tkmessage.showerror("Error", "Lowpass cutoff frequency greater than sampling rate.")
        elif self.hpcut.get() > self.sampling_rate.get():
            tkmessage.showerror("Error", "Highpass cutoff frequency greater than sampling rate.")
        else:
            for k, tr in enumerate(self._traces):
                if self.lowpass.get():
                    self._traces[k,:] = lowpass(tr, self.lpcut.get(), self.sampling_rate.get())
                if self.highpass.get():
                    self._traces[k,:] = highpass(tr, self.hpcut.get(), self.sampling_rate.get())
    
    def _read(self, filename):
        self._current_file = filename
        self._current_index = self._filenames.index(filename)
        self._read_traces()
        self._filter_traces()
        self.plot()
        
    def _man_pick(self, k, index):
        if self.delay.get():
            shift = self._delay2samples()
        else:
            shift = 0
        if self.taxis_seconds.get():
            index *= self.sampling_rate.get()
        time = self._starttime + index / self.sampling_rate.get()
        fs = self.sampling_rate.get()
        self.picks[self._current_index][k] = Pick(time, index, fs, shift = shift)
        
    def _tobs2str(self, tobs):
        base = np.floor(np.log10(tobs))
        string = ""
        if base >= 0.:
            string = "%.2f s" % tobs
        elif -3 <= base < 0:
            string = "%.2f ms" % (tobs / 10**(base-1))
        elif -6 <= base < -3:
            string = "%.2f us" % (tobs / 10**(base-1))
        elif -9 <= base < -6:
            string = "%.2f ns" % (tobs / 10**(base-1))
        return string
    
    def _delay2samples(self):
        delay_val = self.delay_val.get()
        delay_unit = self.delay_unit.get()
        fs = self.sampling_rate.get()
        if delay_unit == "samples":
            return delay_val
        elif delay_unit == "s":
            return delay_val * fs
        elif delay_unit == "ms":
            return delay_val * fs * 1e-3
        elif delay_unit == "us":
            return delay_val * fs * 1e-6
        
    def _set_taxis_seconds(self):
        self.taxis_seconds.set(True)
        self.taxis_samples.set(False)
        self.plot()
        
    def _set_taxis_samples(self):
        self.taxis_samples.set(True)
        self.taxis_seconds.set(False)
        self.plot()
        
    def define_variables(self):
        self.input_dirname = tk.StringVar(self.master)
        self.sampling_rate = tk.DoubleVar(self.master)
        self.enforce_fs = tk.BooleanVar(self.master)
        self.lowpass = tk.BooleanVar(self.master)
        self.highpass = tk.BooleanVar(self.master)
        self.lpcut = tk.DoubleVar(self.master)
        self.hpcut = tk.DoubleVar(self.master)
        self.year = tk.IntVar(self.master)
        self.month = tk.IntVar(self.master)
        self.day = tk.IntVar(self.master)
        self.hour = tk.IntVar(self.master)
        self.minute = tk.IntVar(self.master)
        self.second = tk.IntVar(self.master)
        self.plot_type = tk.IntVar(self.master)
        self.fill = tk.BooleanVar(self.master)
        self.delay = tk.BooleanVar(self.master)
        self.delay_val = tk.DoubleVar(self.master)
        self.delay_unit = tk.StringVar(self.master)
        self.normalize = tk.BooleanVar(self.master)
        self.perc = tk.DoubleVar(self.master)
        self.taxis_seconds = tk.BooleanVar(self.master)
        self.taxis_samples = tk.BooleanVar(self.master)
    
    def trace_variables(self):
        self.input_dirname.trace("w", self.callback)
        self.sampling_rate.trace("w", self.callback)
        self.enforce_fs.trace("w", self.callback)
        self.lowpass.trace("w", self.callback)
        self.highpass.trace("w", self.callback)
        self.lpcut.trace("w", self.callback)
        self.hpcut.trace("w", self.callback)
        self.year.trace("w", self.callback)
        self.month.trace("w", self.callback)
        self.day.trace("w", self.callback)
        self.hour.trace("w", self.callback)
        self.minute.trace("w", self.callback)
        self.second.trace("w", self.callback)
        self.plot_type.trace("w", self.callback)
        self.fill.trace("w", self.callback)
        self.delay.trace("w", self.callback)
        self.delay_val.trace("w", self.callback)
        self.delay_unit.trace("w", self.callback)
        self.normalize.trace("w", self.callback)
        self.perc.trace("w", self.callback)
        self.taxis_seconds.trace("w", self.callback)
        self.taxis_samples.trace("w", self.callback)

    def init_variables(self):
        self.enforce_fs.set(False)
        self.lowpass.set(False)
        self.highpass.set(False)
        self.plot_type.set(1)
        self.fill.set(False)
        self.delay.set(False)
        self.delay_val.set(0.)
        self.delay_unit.set("samples")
        self.normalize.set(False)
        self.perc.set(1.)
        self.taxis_seconds.set(False)
        self.taxis_samples.set(True)

    def close(self):
        self.master.quit()
        self.master.destroy()

    def callback(self, *args):
        pass
    
    
def main():
    """
    Start Pycker Viewer window.
    """
    import matplotlib
    matplotlib.use("TkAgg")
    from sys import platform as _platform
    
    root = tk.Tk()
    root.max_width, root.max_height = root.maxsize()
    PyckerGUI(root)
    s = ttk.Style()
    if _platform == "win32":
        s.theme_use("vista")
    elif _platform in [ "linux", "linux2" ]:
        s.theme_use("alt")
    elif _platform == "darwin":
        s.theme_use("aqua")
    root.mainloop()