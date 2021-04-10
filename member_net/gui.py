from tkinter import *
from tkinter import ttk
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg)  # , NavigationToolbar2Tk
from matplotlib.figure import Figure
from member_net.member_net_functions import *


class GraphJob:
    def __init__(self):
        self.G = None
        self.db_type = None
        self.n = None
        self.ind = None
        self.subgraph_count = [0]
        self.max_subgraph = 0
        self.max_degree = 0
        self.min_degree = 1
        self.min_connections = 2
        self.canvas = None
        self.top = None
        self.degree = None
        self.degrees = None

    def make_graph(self):
        self.G, self.ind = generate_member_graph(self.db_type)

    def count_subgraphs(self):
        s = [self.G.subgraph(c).copy() for c in nx.connected_components(self.G)]
        cc = []
        for subgraph in s:
            cc.append(len(nx.nodes(subgraph)))
        self.subgraph_count = cc
        self.max_subgraph = max(cc)

    def count_degrees(self):
        self.degree = nx.degree(self.G)
        self.degrees = [node[1] for node in self.degree]
        self.max_degree = max(self.degrees)

    def print_both_histograms(self):
        # New window
        self.top = Toplevel(root)

        # two frames so the graphs don't print on top of eachother
        f1 = Frame(self.top)
        f2 = Frame(self.top)

        # filter histogram by min specified in menu
        print_degrees = [d for d in self.degrees if d >= self.min_degree]
        print_subgraph = [s for s in self.subgraph_count if s>= self.min_connections]

        ###############################################################
        # DEGREES
        ###############################################################
        self.fig1 = Figure(figsize=(5, 4), dpi=100)
        self.fig1.add_subplot(xlabel='Degrees (number of connections)', ylabel='Count').hist(
            print_degrees,
            bins=10,
            rwidth=.9)
        self.fig1.suptitle('Degrees (connections) per Membership/Individual', fontsize=12)
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=self.top)
        self.canvas1.draw_idle()

        ########################################################################
        # SUBGRAPHS
        #######################################################################
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.fig.add_subplot(xlabel='Size (total individuals/memberships in a network)', ylabel='Count').hist(
            print_subgraph, bins=10, rwidth=.9)
        self.fig.suptitle('Network Sizes', fontsize=12)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.top)
        self.canvas.draw_idle()

        # display
        self.canvas1.get_tk_widget().grid(column = 1, row=1)
        self.canvas.get_tk_widget().grid(column=2, row=1)

    def update_histograms(self):
        # Destroy window and recreate
        self.top.destroy()

        # Update min selections
        self.min_degree = h1_select.current()
        self.min_connections = h2_select.current()

        # rerun histogram
        self.print_both_histograms()

    def update_menus(self):
        n_selected['values'] = list(range(self.max_subgraph))
        h1_select['values'] = list(range(self.max_degree))
        h2_select['values'] = list(range(self.max_subgraph))

    def initialize_db_and_graph(self, event):
        selection = db_selected.current()
        label = db_selected['values'][selection]
        self.db_type = label
        self.make_graph()
        self.count_subgraphs()
        self.count_degrees()
        self.print_both_histograms()
        self.update_menus()
        print(self.db_type, self.ind)

    def execute(self, event):
        self.n = n_selected.current()
        multi = get_subgraphs(self.G, self.n)
        check_output()

        # Message
        print('#'*30)
        print('Beginning export...')
        print(f'Output folder: {output_location}')
        print(f'To change export location, edit output_locations.py in the config folder')
        print('#'*30)
        print('Generating graphics..')

        subnetwork_df, columns, igroup, mgroup = subgraph_output(multi, self.ind)

        # Export member/individual/group to csv
        print('Generating member/individual and group tables...')
        output_csvs(igroup, mgroup)

        # Export summary spreadsheet
        print('Generating summary spreadsheet...')
        output_excel(subnetwork_df, columns)

        # Export gexf
        print('Generating gexf...')
        nx.write_gexf(self.G, f'{output_location}//{gephx_filename}{timestamp}.gexf')

        print(f'Spreadsheet saved as Member subnetworks - {timestamp}.xlsx in the output directory:{output_location}.')
        print(f'GEXF file saved as Total membership networks - {timestamp}.gexf in the output directory:{output_location}.')
        print('Done!')

################################################################
# THE GUI
###############################################################

# Initialize object
job = GraphJob()

# Set up root object
root = Tk()
root.title('Credit Union Member Network Analyzer')
root.geometry('400x350')
db_frame = Frame(root)
hist_frame = Frame(root)
last_frame = Frame(root)
welcome_frame = Frame(root)
optional_frame = Frame(root)
select_n_frame = Frame(root)

# Welcome message
welcome_message = Label(welcome_frame, text = 'See terminal for status and error messages.')

# Database dropdown
db_message = Label(db_frame, text='1) Select database')

db_available = StringVar()
db_selected = ttk.Combobox(db_frame, width=20, textvariable=db_available)
db_selected['values'] = ('sqlite', 'datamart')
db_selected.current()

# Initialize button
initialize_button = Button(db_frame, text='2) Initialize', bd=5)
initialize_button.bind("<Button-1>", job.initialize_db_and_graph)

# Histogram filters
h1 = StringVar()
h2 = StringVar()

histogram_message = Label(optional_frame, text='Optional: Improve chart readability by setting x axis minimum')
h1_label = Label(hist_frame, text='Degrees (connections)')
h1_select = ttk.Combobox(hist_frame, width=3, textvariable=h1)
h1_select['values'] = list(range(job.max_degree))
h1_select.current()

h2_label = Label(hist_frame, text='Network size')
h2_select = ttk.Combobox(hist_frame, width=3, textvariable=h2)
h2_select['values'] = list(range(job.max_subgraph))
h2_select.current()

hist_update = Button(hist_frame, text='Update', bd='5', command=job.update_histograms)

# Subgraph filter
n = StringVar()
select_n_message = Label(select_n_frame,
                         text='3) Select min subgraph size for export')

n_selected = ttk.Combobox(last_frame, width=5, textvariable=n)
n_selected['values'] = list(range(job.max_subgraph))
n_selected.current()

# Exit buttons
exit_button = Button(last_frame, text='        Exit        ', bd='5', command=root.destroy)

# Execute
execute_button = Button(last_frame, text='4) Execute', bd='5')
execute_button.bind("<Button-1>", job.execute)

#############################################################################
# WIDGET LAYOUT
#############################################################################

welcome_frame.grid(row=1, column=1)
db_frame.grid(row=2, column=1)
optional_frame.grid(row=3, column=1)
hist_frame.grid(row=4, column=1)
select_n_frame.grid(row=5, column=1)
last_frame.grid(row=6, column=1)

# top third
welcome_message.grid(column=1, row=1, sticky=W)
db_message.grid(column=1, row=2, sticky=W)
db_selected.grid(column=1, row=3, sticky=W)
initialize_button.grid(column=2, row=3, sticky=W)

# middle third
histogram_message.grid(column=1, row=1, sticky=W, padx = 10, pady=10)
h1_label.grid(column=1, row=2, sticky=W)
h1_select.grid(column=2, row=2, sticky=W)
h2_label.grid(column=1, row=3, sticky=W)
h2_select.grid(column=2, row=3, sticky=W)
hist_update.grid(column=3, row=3, sticky=W)

# last third
select_n_message.grid(column=1, row=1, pady=10)
n_selected.grid(column=1, row=1, sticky=W)
execute_button.grid(column=2, row=1, sticky=W)
exit_button.grid(column=1, row=9, sticky=W, pady=30)