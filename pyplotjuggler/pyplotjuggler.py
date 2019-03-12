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
from tkinter import messagebox

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 300


class pyplotjuggler(ttk.Frame):
    """pyplotjuggler"""

    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.figs = []
        self.data = None
        self.selected_field = ""
        self.create_widgets()
        self.root.geometry(str(WINDOW_WIDTH) + "x" + str(WINDOW_HEIGHT))

        # Menu bar setting
        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Load", command=self.load_file)
        menubar.add_cascade(label="File", menu=filemenu)
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.show_about_message)
        menubar.add_cascade(label="Help", menu=helpmenu)

        root.config(menu=menubar)
        root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """ on closing widget"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            # Close all matplotlib figure
            for figm in self.figs:
                plt.close(figm.fig)
            self.root.destroy()

    def load_file(self):
        """load_file"""
        ftyp = [("CSV", "*.csv")]
        idir = os.path.abspath(os.path.dirname(__file__) + "../")
        fpath = tkinter.filedialog.askopenfilename(
            filetypes=ftyp, initialdir=idir)

        self.data = pd.read_csv(fpath)

        # insert data columns
        for i, name in enumerate(self.data.columns):
            self.left.insert(i, name)
            self.left.bind('<<ListboxSelect>>', self.on_select)

        # Setting time slider limit with first key
        self.time_slider.configure(to=len(self.data.iloc[:, 0]))

    def show_about_message(self):
        """show about"""
        msg = """
        pyplotjuggler
        by Atsushi Sakai(@Atsushi_twi)
        Ver. 0.1
        GitHub:https://github.com/AtsushiSakai/pyplotjuggler
        """
        messagebox.showinfo("About", msg)

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
            length=WINDOW_WIDTH, from_=0, to=200, orient=tk.HORIZONTAL)
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
