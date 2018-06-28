# Import packs

import tkinter as tk
from tkinter.filedialog import askopenfilenames, askdirectory
from tkinter import ttk
import sys
import os
import pandas as pd

PAGES = []  # Fill with page objects
LARGE_FONT = ("Verdana", 11)  # Declare font style and size

# Define necessary functions


def defpage(classname):
    PAGES.append(classname)


def filters(df):
    df = df[df["PlanName"].str.startswith("B")]
    df = df[~df["PlanName"].str.contains("Hons")]
    df = df[~df["PlanName"].str.contains("HONS")]
    df = df[df["MinGrad"] > 2]
    df = df.sort_values("PlanName")
    dict_all = dict(zip(df["PlanCode"], df["PlanName"]))
    dict_mg = dict(zip(df["PlanCode"], df["MinGrad"]))
    return dict_all, dict_mg


def get_list(fnames):
    # Note: Can get mingradtime from files: (98,99)
    test = pd.DataFrame()
    for f in fnames:
        temp = pd.read_fwf(f,
                           colspecs=[(0, 15), (106, 171), (98, 99)],
                           names=["PlanCode", "PlanName", "MinGrad"])
        # print("Head for file: {}".format(f), temp.head(5))
        test = test.append(temp.drop_duplicates(["PlanCode"]))

    dict_all = dict(zip(test["PlanCode"], test["PlanName"]))
    ref_dict, mg_dict = filters(test)
    codelist = list(ref_dict.keys())
    namelist = list(ref_dict.values())

    return namelist, codelist, dict_all, mg_dict

# Define App class and page classes


class App(tk.Tk):
    # This is the base window, it will take as input other frames

    def __init__(self, *args, **kwargs):
        #        Initialise frame and pack, as well as inheritance from Tk()

        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.iconbitmap(self, default="logo.ico")
        tk.Tk.wm_title(self, "UP Sankey Generator")

        container = ttk.Frame(self)
        container.grid(row=0, column=0, rowspan=3, columnspan=2)
        self.resizable(width=False, height=False)

        menubar = tk.Menu(container)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Exit", command=self.exit_button)
        menubar.add_cascade(label="File", menu=filemenu)
        tk.Tk.config(self, menu=menubar)

        # Create lists to use in NextPage:
        self.list_pname = ["All"]
        self.list_pcode = ["All"]

        # Create instances of page classes:
        self.frames = {}
        for P in PAGES:
            frame = P(container, self)
            self.frames[P] = frame
            frame.grid(row=0, column=0, rowspan=frame.nrows, columnspan=frame.ncols, sticky="nsew")

        self.show_frame(StartPage)

    # Functions:
    def show_frame(self, cont):
        for frame in self.frames.values():
            frame.grid_remove()

        frame = self.frames[cont]
        frame.grid()

    def exit_button(self):
        if True:
            self.destroy()
            sys.exit(0)


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Variables:
        self.nrows = 3
        self.ncols = 2
        self.sfile = []
        self.pfile = []
        self.pdict = {}
        self.a = []
        self.b = []
        self.abdict = {"a": self.a, "b": self.b}
        self.mgdict = {}
        self.dir = os.path.dirname(os.path.realpath(__file__))
        self.output_dict = {"Studentfiles": self.sfile, "Planfiles": self.pfile, "uPlans": self.abdict,
                            "aPlans": self.pdict, "mingrad": self.mgdict}
        controller.start_out = self.output_dict
        self.control = controller

        # Labels:
        label = tk.Label(self, text="Please import necessary files, then click next", font=LARGE_FONT)
        label.grid(row=0, column=0, columnspan=self.ncols, sticky="nsew", padx=10, pady=10)

        # Buttons:
        button1 = ttk.Button(self, text="Select student files", command=self.student_files)
        button1.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        button2 = ttk.Button(self, text="Select plan files", command=self.program_files)
        button2.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        self.button3 = ttk.Button(self, state="disabled", text="Next")
        self.button3.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        button4 = ttk.Button(self, text="Quit", command=self.exit_button)
        button4.grid(row=2, column=1, sticky="nsew", padx=10, pady=10)

    # Local Functions:

    def student_files(self):
        self.sfile = list(askopenfilenames(initialdir=self.dir[0:-32]))
        self.output_dict["Studentfiles"] = self.sfile

    def program_files(self):
        self.pfile = list(askopenfilenames(initialdir=self.dir[0:-32]))
        self.output_dict["Planfiles"] = self.pfile
        if len(self.pfile) > 0:
            self.button3.config(state="normal", command=lambda: self.control.show_frame(NextPage))
            self.a, self.b, self.pdict, self.mgdict = get_list(self.pfile)
            self.control.list_pname = self.control.list_pname + self.a
            self.control.list_pcode = self.control.list_pcode + self.b
            self.control.frames[NextPage].e3.config(values=self.control.list_pname)
            self.control.frames[NextPage].e4.config(values=self.control.list_pcode)

            # Save inputs:
            self.output_dict["aPlans"] = self.pdict
            self.abdict["a"] = self.a
            self.abdict["b"] = self.b
            self.output_dict["uPlans"] = self.abdict
            self.output_dict["mingrad"] = self.mgdict

    def exit_button(self):
        if True:
            self.destroy()
            sys.exit(1)


defpage(StartPage)


class NextPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Variables:
        self.nrows = 4
        self.ncols = 4
        self.ys = tk.StringVar(self)
        self.pname = tk.StringVar(self)
        self.pcode = tk.StringVar(self)
        self.cohort = tk.StringVar(self)
        self.dir = os.path.dirname(os.path.realpath(__file__))
        self.savefile = self.dir
        self.dict = {"ystart": self.ys, "pname": self.pname,
                     "pcode": self.pcode, "cohort": self.cohort,
                     "saveloc": self.savefile}
        controller.next_out = self.dict
        self.control = controller
        self.list1 = controller.list_pname
        self.list2 = controller.list_pcode

        # Labels:
        label = tk.Label(self, text="Select academic plan and year range for Sankey graph", font=LARGE_FONT)
        label.grid(row=0, column=0, columnspan=self.ncols, sticky="nsew", padx=10, pady=10)

        lab1 = ttk.Label(self, text="Start Year (files)")
        lab1.grid(row=1, column=0, sticky="ns", padx=10, pady=10)

        lab2 = ttk.Label(self, text="Cohort")
        lab2.grid(row=1, column=2, sticky="ns", padx=10, pady=10)

        lab3 = ttk.Label(self, text="Program")
        lab3.grid(row=2, column=0, sticky="ns", padx=10, pady=10)

        lab4 = ttk.Label(self, text="Program Code")
        lab4.grid(row=2, column=2, sticky="ns", padx=10, pady=10)

        # Buttons:
        button1 = ttk.Button(self, text="Back", command=lambda: controller.show_frame(StartPage))
        button1.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)

        button2 = ttk.Button(self, text="Clear All", command=self.clear_button)
        button2.grid(row=3, column=1, sticky="nsew", padx=10, pady=10)

        self.button4 = ttk.Button(self, text="Save & Finish", command=self.finish_button)
        self.button4.grid(row=3, column=2, columnspan=2, sticky="nsew", padx=10, pady=10)

        # Entries:
        self.e1 = ttk.Entry(self, textvariable=self.ys)
        self.e1.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        self.e1.insert(0, "2011")

        self.e2 = ttk.Entry(self, textvariable=self.cohort)
        self.e2.grid(row=1, column=3, sticky="nsew", padx=10, pady=10)
        self.e2.insert(0, "2011")

        # Drop down list:
        self.e3 = ttk.Combobox(self, textvariable=self.pname, values=self.list1)
        self.e3.grid(row=2, column=1, sticky="nsew", padx=10, pady=10)
        self.e3.insert(0, self.e3.current(newindex=0))
        self.e3.bind('<<ComboboxSelected>>', self.combo_select1)

        self.e4 = ttk.Combobox(self, textvariable=self.pcode, value=self.list2)
        self.e4.grid(row=2, column=3, sticky="nsew", padx=10, pady=10)
        self.e4.insert(0, self.e4.current(newindex=0))
        self.e4.bind('<<ComboboxSelected>>', self.combo_select2)
        

    # Functions:
    def clear_button(self):
        e_list = [self.e1, self.e2, self.e3, self.e4]
        for e in e_list:
            e.delete(0, "end")

    def finish_button(self):
        self.savefile = askdirectory(initialdir=self.dir[0:-32])
        self.dict["ystart"] = self.ys.get()
        self.dict["pname"] = self.pname.get()
        self.dict["pcode"] = self.pcode.get()
        self.dict["cohort"] = self.cohort.get()
        self.dict["saveloc"] = self.savefile
        
        if len(self.savefile)>0:
            self.control.destroy()
        else:
            pass

    def combo_select1(self, event):
        index_selected = self.e3.current()
        while index_selected != self.e4.current():
            self.e4.current(newindex=index_selected)

    def combo_select2(self, event):
        index_selected = self.e4.current()
        while index_selected != self.e3.current():
            self.e3.current(newindex=index_selected)


defpage(NextPage)


class ProgBar(tk.Tk):
    # This is the final window, it will open when all is done

    def __init__(self, *args, **kwargs):
        #        Initialise frame and pack, as well as inheritance from Tk()

        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.iconbitmap(self, default="logo.ico")
        tk.Tk.wm_title(self, "UP Sankey Generator")

        container = ttk.Frame(self)
        container.grid(row=0, column=0, rowspan=3, columnspan=4)
        self.grid_columnconfigure(0, weight=1)
        self.resizable(width=False, height=False)

        self.pvar = tk.DoubleVar()

        label = tk.Label(self, text="Progress", font=LARGE_FONT)
        label.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)

        labe2 = tk.Label(self, text="                 ")
        labe2.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        progressbar = ttk.Progressbar(self, variable=self.pvar, maximum=100)
        progressbar.grid(row=1, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)

        self.button = ttk.Button(self, state="disabled", text="Done")
        self.button.grid(row=2, column=3, sticky="nsew", padx=10, pady=10)

    def finish_button(self):
        self.destroy()