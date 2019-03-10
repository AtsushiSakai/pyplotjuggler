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
        self.figs = []
        self.data = None
        self.selected_field = ""
        self.create_widgets()
        self.root.geometry('400x400')

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
        print('You selected item %d: "%s"' % (index, value))
        self.selected_field = value

    def create_widgets(self):
        """create_widgets"""
        self.languages = tk.StringVar(value=())
        self.left = tk.Listbox(listvariable=self.languages)
        self.left.pack()

        self.time_slider = tk.Scale(
            length=200, from_=0, to=200, orient=tk.HORIZONTAL)
        self.time_slider.pack()

        self.bt_new_fig = tk.Button(
            text='Create new figure', command=self.create_new_figure)
        self.bt_new_fig.pack()

    def create_new_figure(self):
        print("create_new_figure")

        fnum = len(self.figs) + 1
        self.figs.append(FigureManager(self, fnum))


class FigureManager():
    def __init__(self, parent, fnum):
        self.fig, self.ax = plt.subplots()
        self.parent = parent
        self.x = None
        self.y = None
        self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.fig_num = fnum

        plt.pause(0.0001)

    def onclick(self, event):
        print('event.button=%d,  event.x=%d, event.y=%d, event.xdata=%f, \
            event.ydata=%f' % (event.button, event.x, event.y, event.xdata, event.ydata))
        print(self.fig_num)
        print(self.parent.selected_field)
        self.plot(self.parent.data[self.parent.selected_field])

    def plot(self, data):
        print("plot")
        if self.x is None:
            self.x = data
            self.ax.plot(self.x)
        elif self.y is None:
            self.ax.cla()
            self.y = data
            self.ax.plot(self.x, self.y)
        plt.pause(0.01)


def main():
    """main"""
    print("start!!")
    root = tk.Tk()
    root.title('PyPlotJuggler')
    app = pyplotjuggler(root)
    root.mainloop()

    print("done!!")


if __name__ == '__main__':
    main()
