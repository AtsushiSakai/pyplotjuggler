"""

Pyplotjuggler


author: Atsushi Sakai

"""

import os
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class pyplotjuggler(ttk.Frame):
    """pyplotjuggler"""

    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.create_widgets()
        self.data = None

        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Load", command=self.load_file)
        menubar.add_cascade(label="File", menu=filemenu)

        root.config(menu=menubar)

    def load_file(self):
        """load_file"""
        ftyp = [("CSV", "*.csv")]
        idir = os.path.abspath(os.path.dirname(__file__))
        fpath = tkinter.filedialog.askopenfilename(
            filetypes=ftyp, initialdir=idir)

        self.data = pd.read_csv(fpath)

        # insert data columns
        for i, name in enumerate(self.data.columns):
            self.left.insert(i, name)
            self.left.bind('<<ListboxSelect>>', self.on_select)

    def on_select(self, evt):
        # Note here that Tkinter passes an event object to onselect()
        wid = evt.widget
        index = int(wid.curselection()[0])
        value = wid.get(index)
        # print('You selected item %d: "%s"' % (index, value))

        self.ax.plot(self.data[value])
        self.canvas.draw()

    def create_widgets(self):
        """create_widgets"""
        self.languages = tk.StringVar(value=())
        self.left = tk.Listbox(self, listvariable=self.languages)

        self.left.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.right = self.canvas.get_tk_widget()
        self.right.grid(column=1, row=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)


def main():
    """main"""
    print("start!!")
    root = tk.Tk()
    root.title('PyPlotJuggler')
    app = pyplotjuggler(root)
    app.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W))
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.mainloop()

    print("done!!")


if __name__ == '__main__':
    main()
