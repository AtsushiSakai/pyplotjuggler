"""

Pyplotjuggler

author: Atsushi Sakai

"""

import os
from tkinter import messagebox
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog
import pandas as pd
import matplotlib.pyplot as plt

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 300


class pyplotjuggler(ttk.Frame):
    """pyplotjuggler"""

    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.figs = []
        self.data = None
        self.selected_fields = []
        self.time = 0
        self.create_widgets()
        self.root.geometry(str(WINDOW_WIDTH) + "x" + str(WINDOW_HEIGHT))

        self.setup_menubar()

        root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_menubar(self):
        self.menubar = tk.Menu(self.root)
        filemenu = tk.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="Load", command=self.load_file)
        self.menubar.add_cascade(label="File", menu=filemenu)
        helpmenu = tk.Menu(self.menubar, tearoff=0)
        helpmenu.add_command(label="About",
                             command=self.show_about_message)
        self.menubar.add_cascade(label="Help", menu=helpmenu)
        self.root.config(menu=self.menubar)

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
            self.field_list.insert(i, name)
            self.field_list.bind('<<ListboxSelect>>', self.on_select)

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
        """on_select"""
        wid = evt.widget

        self.selected_fields = []
        for ind in wid.curselection():
            value = wid.get(int(ind))
            self.selected_fields.append(value)
        self.status_bar_str.set("")

    def slider_changed(self, event):
        self.time = self.time_slider.get()  # update time

        for f in self.figs:
            f.plot_time_line(self.time)

    def clear_selection(self):
        """clear list"""
        self.field_list.selection_clear(0, tkinter.END)

    def create_widgets(self):
        """create_widgets"""

        container = ttk.Frame()
        container.pack(fill='both', expand=True)
        header = ['field name', 'value']
        # create a treeview with dual scrollbars
        self.tree = ttk.Treeview(columns=header, show="headings")
        vsb = ttk.Scrollbar(orient="vertical",
                            command=self.tree.yview)
        hsb = ttk.Scrollbar(orient="horizontal",
                            command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set,
                            xscrollcommand=hsb.set)
        self.tree.grid(column=0, row=0, sticky='nsew', in_=container)
        vsb.grid(column=1, row=0, sticky='ns', in_=container)
        hsb.grid(column=0, row=1, sticky='ew', in_=container)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=3)
        container.grid_rowconfigure(0, weight=1)

        for col in header:
            self.tree.heading(col, text=col.title())

        self.languages = tk.StringVar(value=())
        self.field_list = tk.Listbox(listvariable=self.languages,
                                     selectmode='multiple')
        self.field_list.pack(side="top")

        self.slider_label_frame = tk.Frame(self.root, bd=2, relief="ridge")
        self.time_slider_label = tk.Label(
            self.slider_label_frame, text="Time index slider:")
        self.time_slider_label.pack(side="left")
        self.slider_label_frame.pack(fill="x", side="top")

        self.time_slider = tk.Scale(self.slider_label_frame,
                                    length=WINDOW_WIDTH, from_=0, to=200,
                                    orient=tk.HORIZONTAL)
        self.time_slider.bind("<ButtonRelease-1>", self.slider_changed)
        self.time_slider.pack(fill="x")

        self.btn_frame = tk.Frame(self.root, relief="ridge")
        self.btn_frame.pack(fill="x")
        self.new_fig_btn = tk.Button(self.btn_frame,
                                     text='Create figure',
                                     command=self.create_new_figure)
        self.new_fig_btn.pack(side="left")
        self.clear_list_btn = tk.Button(self.btn_frame, text="clear selection",
                                        command=self.clear_selection)
        self.clear_list_btn.pack(side="left")
        # button3 = tk.Button(self.frame, text="終了")
        # button3.pack(side="right")

        self.setup_status_bar()

    def setup_status_bar(self):
        self.status_bar_str = tkinter.StringVar()
        self.status_bar = tkinter.Label(self.root,
                                        textvariable=self.status_bar_str,
                                        bd=1, relief=tkinter.SUNKEN, anchor=tkinter.W)
        self.status_bar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
        self.status_bar_str.set("")

    def create_new_figure(self):
        print("create_new_figure")

        fnum = len(self.figs) + 1
        self.figs.append(FigureManager(self, fnum))


class FigureManager():
    def __init__(self, parent, fnum):
        self.fig, self.ax = plt.subplots()
        self.parent = parent
        self.x = []
        self.x_field_names = []
        self.y = []
        self.y_field_names = []
        self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.fig_num = fnum

        plt.pause(0.0001)

    def onclick(self, event):

        if not self.parent.selected_fields:
            self.parent.status_bar_str.set("Please click field")
        else:
            self.set_data(self.parent.data,
                          self.parent.selected_fields)
        self.parent.clear_selection()
        self.parent.selected_fields = []

    def set_data(self, data, field_names):

        if not self.x:
            for fn in field_names:
                self.x.append(data[fn])
                self.x_field_names.append(fn)
        elif not self.y:
            for fn in field_names:
                self.y.append(data[fn])
                self.y_field_names.append(fn)
        self.plot()

    def plot(self):
        self.ax.cla()

        if not self.y:
            for i in range(len(self.x)):
                time = [t for t in range(len(self.x[i]))]
                self.ax.plot(time, self.x[i],
                             label=self.x_field_names[i])
            self.ax.set_xlabel("Time index")
            self.ax.legend()
        elif len(self.x) == 1:
            self.ax.plot(self.x[0], self.y[0], "-r")
            self.ax.set_xlabel(self.x_field_names[0])
            self.ax.set_ylabel(self.y_field_names[0])

        self.ax.grid(True)
        plt.pause(0.01)

    def plot_time_line(self, time):
        self.plot()
        if not self.y:
            self.ax.axvline(x=time)

            for i in range(len(self.x)):
                self.ax.plot(time, self.x[i][time], "xk")
                self.ax.text(time, self.x[i][time],
                             '{:.3f}'.format(self.x[i][time]) +
                             ":" + self.x_field_names[i])
        else:
            self.ax.plot(self.x[0][time], self.y[0][time], "xk")
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
