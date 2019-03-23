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
import argparse

SIM_DT = 0.01
PLOT_DT = 0.00001
VERSION = "0.1.5"


class pyplotjuggler(ttk.Frame):

    def __init__(self, root, args):
        super().__init__(root)
        self.root = root
        self.figs = []
        self.data = None
        self.selected_fields = []
        self.time = 0
        self.max_time = 200
        self.args = args
        self.time_started = False
        self.initialize_widgets()

        self.root.title('PyPlotJuggler')
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.setup_with_args()

    def setup_with_args(self):
        self.idir = os.path.abspath("./")
        if self.args.dir:
            self.idir = self.args.dir

        if self.args.open:
            self.load_file()

        if self.args.file:
            self.setup_csv_file(self.args.file)

    def initialize_widgets(self):
        self.setup_field_list()
        self.setup_time_slider()
        self.setup_buttons()
        self.setup_status_bar()
        self.setup_menubar()

    def setup_menubar(self):
        self.menubar = tk.Menu(self.root)
        filemenu = tk.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="Load file", command=self.load_file)
        filemenu.add_command(label="Create figure",
                             command=self.create_new_figure)
        filemenu.add_command(label="Clear selection",
                             command=self.clear_selection)
        filemenu.add_command(label="start time",
                             command=self.start_time)
        filemenu.add_command(label="stop time",
                             command=self.stop_time)
        self.menubar.add_cascade(label="Action", menu=filemenu)
        helpmenu = tk.Menu(self.menubar, tearoff=0)
        helpmenu.add_command(label="About",
                             command=self.show_about_message)
        self.menubar.add_cascade(label="Help", menu=helpmenu)
        self.root.config(menu=self.menubar)

    def setup_field_list(self):
        self.field_table_label = tk.Label(
            text="Field table")
        self.field_table_label.pack()

        container = ttk.Frame()
        container.pack(fill='both', expand=True)
        header = ['field name', 'value']
        self.field_list = ttk.Treeview(columns=header, show="headings")
        vsb = ttk.Scrollbar(orient="vertical",
                            command=self.field_list.yview)
        hsb = ttk.Scrollbar(orient="horizontal",
                            command=self.field_list.xview)
        self.field_list.configure(yscrollcommand=vsb.set,
                                  xscrollcommand=hsb.set)
        self.field_list.grid(column=0, row=0, sticky='nsew', in_=container)
        vsb.grid(column=1, row=0, sticky='ns', in_=container)
        hsb.grid(column=0, row=1, sticky='ew', in_=container)
        container.grid_columnconfigure(0, weight=3)
        container.grid_rowconfigure(0, weight=1)

        for col in header:
            self.field_list.heading(col, text=col.title())
        self.update_selection_list(0.0)

    def setup_time_slider(self):
        self.slider_label_frame = tk.Frame(self.root, bd=2, relief="ridge")
        self.time_slider_label = tk.Label(
            self.slider_label_frame, text="Time index slider:")
        self.time_slider_label.pack(side="left")
        self.slider_label_frame.pack(fill="x", side="top")

        self.time_slider = tk.Scale(self.slider_label_frame,
                                    from_=0,
                                    to=self.max_time,
                                    orient=tk.HORIZONTAL)
        self.time_slider.bind("<ButtonRelease-1>", self.slider_changed)
        self.time_slider.pack(fill="x")

    def setup_buttons(self):
        self.btn_frame = tk.Frame(self.root, relief="ridge")
        self.btn_frame.pack(fill="x")

        self.new_fig_btn = tk.Button(self.btn_frame,
                                     text='Create figure',
                                     command=self.create_new_figure)
        self.new_fig_btn.pack(side="left")

        self.clear_list_btn = tk.Button(self.btn_frame, text="clear selection",
                                        command=self.clear_selection)
        self.clear_list_btn.pack(side="left")

        self.load_file_btn = tk.Button(self.btn_frame,
                                       text="Load file",
                                       command=self.load_file)
        self.load_file_btn.pack(side="left")

        self.start_time_btn = tk.Button(self.btn_frame,
                                        text="Start time",
                                        command=self.start_time)
        self.start_time_btn.pack(side="left")
        self.stop_time_btn = tk.Button(self.btn_frame,
                                       text="Stop time",
                                       command=self.stop_time)
        self.stop_time_btn.pack(side="left")

    def setup_status_bar(self):
        self.status_bar_str = tkinter.StringVar()
        self.status_bar = tkinter.Label(self.root,
                                        textvariable=self.status_bar_str,
                                        bd=1, relief=tkinter.SUNKEN,
                                        anchor=tkinter.W)
        self.status_bar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
        self.status_bar_str.set("")

    def start_time(self):
        if self.time_started:
            return
        self.time_started = True
        self.after(int(SIM_DT * 1000), self.proceed_time)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            # Close all matplotlib figure
            for figm in self.figs:
                plt.close(figm.fig)
            self.root.destroy()

    def load_file(self):
        ftyp = [("CSV", "*.csv")]
        fpath = tkinter.filedialog.askopenfilename(
            filetypes=ftyp, initialdir=self.idir)

        if not fpath:
            self.status_bar_str.set("Please select a file")
            return

        if "csv" in fpath:
            self.setup_csv_file(fpath)

    def setup_csv_file(self, csv_path):
        self.data = pd.read_csv(csv_path)
        self.setup_loaded_data()

    def setup_loaded_data(self):

        # insert data columns
        for name in self.data.columns:
            self.field_list.insert("", "end", values=(name, 0.0))
        self.field_list.bind('<<TreeviewSelect>>', self.on_select)
        self.update_selection_list(0.0)

        # Setting time slider limit with first key
        self.max_time = len(self.data.iloc[:, 0])
        self.time_slider.configure(to=self.max_time)

    def show_about_message(self):
        """show about"""
        msg = """
        pyplotjuggler
        by Atsushi Sakai(@Atsushi_twi)
        Ver.""" + VERSION + """\n
        GitHub:https://github.com/AtsushiSakai/pyplotjuggler
        """
        messagebox.showinfo("About", msg)

    def on_select(self, evt):
        """on_select"""
        wid = evt.widget
        self.selected_fields = []
        for ind in wid.selection():
            value = wid.item(ind)
            self.selected_fields.append(value["values"][0])
        self.status_bar_str.set("")

    def update_selection_list(self, time):
        for item in self.field_list.get_children():
            key = self.field_list.item(item)["values"][0]
            self.field_list.set(item, 1, self.data[key][time])

    def slider_changed(self, event):
        self.time = self.time_slider.get()  # update time
        self.update_selection_list(self.time)
        for fig in self.figs:
            fig.plot_time_line(self.time)
        plt.pause(PLOT_DT)

    def clear_selection(self):
        """clear list"""
        for ind in self.field_list.selection():
            self.field_list.selection_remove(ind)

    def stop_time(self):
        self.time_started = False

    def proceed_time(self):
        if not self.time_started:
            return
        self.time += 1
        if self.time >= self.max_time:
            self.stop_time()
            return
        self.time_slider.set(self.time)
        self.update_selection_list(self.time)
        for fig in self.figs:
            fig.plot_time_line(self.time)
        plt.pause(PLOT_DT)

        self.after(int(SIM_DT * 1000), self.proceed_time)

    def create_new_figure(self):
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
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig_num = fnum

        self.ax.grid(True)
        plt.pause(PLOT_DT)

    def on_click(self, event):

        if not self.parent.selected_fields:
            self.parent.status_bar_str.set("Please click field")
        else:
            self.set_data(self.parent.data,
                          self.parent.selected_fields)
            plt.pause(PLOT_DT)
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


def main():
    """main"""
    print("start!!")
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', type=str, help='file path')
    parser.add_argument('-d', '--dir', type=str,
                        help='file directory')
    parser.add_argument('-o', '--open', action='store_true',
                        default=False, help='Open with finder')
    args = parser.parse_args()

    root = tk.Tk()
    app = pyplotjuggler(root, args)
    root.mainloop()

    print("done!!")


if __name__ == '__main__':
    main()
