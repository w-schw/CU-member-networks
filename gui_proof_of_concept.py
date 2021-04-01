from tkinter import *
from tkinter import ttk
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
from member_subnetwork_functions import *

class graph_job:
    def __init__(self):
        self.G = None
        self.db_type = None
        self.n = None
        self.ind = None
        self.subgraph_count = [0]
        self.max_subgraph = 0

    def make_graph(self):
        self.G, self.ind = generate_member_graph(self.db_type)

    def count_subgraphs(self):
        S = [self.G.subgraph(c).copy() for c in nx.connected_components(self.G)]
        cc = []
        for subgraph in S:
            cc.append(len(nx.nodes(subgraph)))
        self.subgraph_count = cc
        self.max_subgraph = max(cc)

    def print_subgraph_histogram(self):
        fig = Figure(figsize=(5, 4), dpi=100)
        fig.add_subplot(xlabel = 'Number of Individuals/Memberships', ylabel='Count of Subgraphs').hist(self.subgraph_count, bins = 10, rwidth = .9)
        fig.suptitle('Number of Individuals/Memberships in Subgraphs', fontsize = 12)
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()
        #canvas.get_tk_widget().place(x=20, y = 570)
        canvas.get_tk_widget().grid(column=1, padx = 10, pady = 10)

    def print_histogram(self):
        degree = nx.degree(self.G)
        degrees = [node[1] for node in degree]
        fig = Figure(figsize=(5, 4), dpi=100)
        fig.add_subplot(xlabel = 'Number of Connections', ylabel='Count of Individuals/Memberships').hist(degrees, bins = 10, rwidth = .9)
        fig.suptitle('Connections per Membership/Individual', fontsize = 12)
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()
        #canvas.get_tk_widget().place(x=20, y = 150)
        canvas.get_tk_widget().grid(column = 1)

    def update_n_menu(self):
        n_selected['values'] = list(range(job.max_subgraph))

    def initialize_db_and_graph(self, event):
        selection = db_selected.current()
        label = db_selected['values'][selection]
        self.db_type = label
        self.make_graph()
        self.count_subgraphs()
        self.print_histogram()
        self.print_subgraph_histogram()
        self.update_n_menu()
        print(self.db_type, self.ind)

    def execute(self, event):
        self.n = n_selected.current()
        multi = get_subgraphs(self.G, self.n)

        subnetwork_df = []
        columns = ['Center', 'Nodes', 'Individuals', 'Memberships', 'Total Savings', 'Total Loans',
                   'PPM', 'Dividends Paid', 'Interest Received']
        timestamp = datetime.now().date().strftime("%b %d %Y ")

        for i in range(len(multi)):
            #specify subgraph
            graph = multi[i]
            colors = generate_color_map(graph,self.ind)

            # Set up graph visualization and get attributes
            center, title, node_count, fig1 = make_graph(graph, colors)

            # separate member nodes and individual nodes
            i,m = separate_members_individuals(graph)

            # calculate summary stats of membership attributes
            total_loan = sum(m['open_loan_bal'])
            total_saving = sum(m['open_sv_bal'])
            loan_count = sum(m['opn_ln_all_cnt'])
            saving_count = sum(m['opn_sv_all_cnt'])
            total_dividend = sum(m['div_ytd_amt'])
            total_interest = sum(m['int_ytd_amt'])

            products_per_member = (loan_count + saving_count) / len(m)

            plt.title(f'The {title} network')

            # make summary table formatted for display
            account_dict = {'Center':title,
                            'Nodes':node_count,
                            'Individuals':len(i),
                            'Memberships':len(m),
                            'Total Savings':f'${total_saving:,.2f}',
                            'Total Loans':f'${total_loan:,.2f}',
                            'PPM':f'{products_per_member:.2n}',
                            'Dividends Paid':f'${total_dividend:,.2f}',
                            'Interest received':f'${total_interest:,.2f}'}

            act_df = pd.DataFrame.from_dict(account_dict, orient='index').rename(columns={0:''})

            export_list = [f'=HYPERLINK("{title}.pdf")', node_count, len(i), len(m), total_saving, total_loan, products_per_member, total_dividend,
                          total_interest]

            # make the account summary table
            fig2 = make_table(act_df)

            # save graph and table as pdf
            make_pdf(fig1, fig2, title)

            subnetwork_df.append(export_list)

            # close the plot to save memory
            plt.close(fig1)
            plt.close(fig2)

        print('Graphics saved to current directory.')
        print('Generating spreadsheet...')

        # Export to an excel spreadsheet with links to pdfs
        d = pd.DataFrame(subnetwork_df, columns = columns)
        d.to_excel(f'Member subnetworks - {timestamp}.xlsx')

        print('done!')

################################################################
# THE GUI
###############################################################


# Initialize object
job = graph_job()

# Set up root object
root = Tk()
root.geometry('1000x1000')
db_frame = Frame(root)

################
# Second window code
#############

#second_window = Toplevel(root)
##second_window.geometry('1000x1000')
#label2 = Label(second_window, text = 'this is your second window')
#label2.pack()
#tb_frame = Frame(second_window)

#def redirector(inputStr):
#    textbox.insert(INSERT, inputStr)

#sys.stdout.write = redirector

# Database dropdown
db_message = Label(db_frame, text = '1) Select database')

db_available = StringVar()
db_selected = ttk.Combobox(db_frame, width = 20, textvariable = db_available)
db_selected['values']=('sqlite', 'datamart')
db_selected.current()

# Initialize button
initialize_button = Button(db_frame, text = '2) Initialize', bd = 5)
initialize_button.bind("<Button-1>", job.initialize_db_and_graph)

# Subgraph filter
n = StringVar()
select_n_message = Label(root, text = '3) Select minimum size of subgraph.\n How many connected individuals/memberships are required to be included in visualizations?')

n_selected = ttk.Combobox(root, width = 5, textvariable = n)
n_selected['values'] = list(range(job.max_subgraph))
n_selected.current()

# Exit buttons
exit_button = Button(root, text = 'Exit', bd = '5', command = root.destroy)

# EXECUTE
execute_button = Button(root, text = 'Execute', bd = '5')
execute_button.bind("<Button-1>", job.execute)

#############################################################################
# WIDGET LAYOUT
#############################################################################
db_frame.grid(row = 1, column = 1)
#tb_frame.pack()

#textbox.pack(expand = True, fill = 'both')#grid(row=2, column = 1)

db_message.grid(column = 1, row = 1)
db_selected.grid(column = 1, row = 2)
initialize_button.grid(column = 2, row = 2)

# histograms
#canvas.get_tk_widget().grid(column=1, padx = 10, pady = 10)
#canvas.get_tk_widget().grid(column = 1)

select_n_message.grid(column=3, row = 1, padx = 50, pady = 10)
n_selected.grid(column = 3, row = 2)
exit_button.grid(column = 3, row = 5)
execute_button.grid(column = 3, row = 4)

#db_message.place(x = 20, y = 60)
#db_selected.place(x = 20, y = 80)
#db_selected.pack(side = 'top', expand = True)

#initialize_button.pack(side = 'top', expand = True)#place(x = 20, y = 100)
#initialize_button.place(x = 20, y = 100)

#select_n_message.pack(side = 'right', expand = True)#place(x = 500, y = 60)
#select_n_message.place(x = 500, y = 60)

#n_selected.pack(side = 'right', expand = True)#place(x = 560, y = 100)
#n_selected.place(x = 560, y = 100)
#exit_button.pack(side = 'bottom')
#execute_button.pack(side = 'right', expand = True)
#execute_button.place(x = 560, y = 200)

root.mainloop()
