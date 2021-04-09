import pandas as pd
# import numpy as np
import networkx as nx
import pyodbc
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.gridspec as gridspec
from datetime import datetime
import os

import config.sql_queries as sql_queries  # sql_queries.py file
import config.server_details as server_details  # server_details.py file
from config.output_location import *  # ouput_location.py file

timestamp = datetime.now().date().strftime("%b %d %Y")


def generate_member_graph(db_type):
    """Generates the graph object using either sqlite or the datamart db.
    :param db_type: sqlite or datamart
    :return G: graph object
    :return ind: dataframe of the individuals, required to generate the color map.
    """
    # These variables should be updated in the server_details.py file
    # sqlite_location = 'demo_data.db'
    # MSSQL_server_name = 'xxxx'
    # datamart_name = 'xxxx'

    if db_type == 'sqlite':
        from sqlite3 import connect
        conn = sqlite3.connect(server_details.sqlite_location)
        ind = pd.read_sql(sql_queries.sqlite_node_individual_query, conn)
        mem = pd.read_sql(sql_queries.sqlite_member_individual_query, conn)
        edges = pd.read_sql(sql_queries.sqlite_edge_query, conn)

    elif db_type == 'datamart':
        try:
            conn = pyodbc.connect('Driver={SQL Server};'
                                  'Server=' + str(server_details.MSSQL_server_name) + ';'
                                  'Database=' + str(server_details.datamart_name) + ';'
                                  'Trusted_Connection=yes;')

        except:
            raise ValueError("Unable to connect to datamart")

        ind = pd.read_sql(sql_queries.ms_sql_node_individual_query, conn)
        mem = pd.read_sql(sql_queries.ms_sql_member_individual_query, conn)
        edges = pd.read_sql(sql_queries.ms_sql_edge_query, conn)

    else:
        raise ValueError("Please specify 'sqlite' or 'datamart'")

    # make attribute dictionary
    mem_dict = mem.set_index('MEMBER_NBR')
    mem_dict = mem_dict.to_dict('index')
    ind_dict = ind.set_index('INDIVIDUAL_ID')
    ind_dict = ind_dict.to_dict('index')

    mem_dict.update(ind_dict)

    # from pandas edgelist
    g = nx.from_pandas_edgelist(edges, edge_attr=True)
    nx.set_node_attributes(g, mem_dict)

    return g, ind


def generate_color_map(graph_object, individual_df):
    """ Generates a color map corresponding with whether a node represents an individual or membership
    :param graph_object: NetworkX graph object
    :param individual_df: DataFrame of the individual table query
    :return colors: A list of colors to be passed to the networkx.draw() function
    """
    individual_nodes = list(individual_df['INDIVIDUAL_ID'])

    for n in graph_object.nodes:
        graph_object.nodes[n]['color'] = 'c' if n in individual_nodes else 'm'

    colors = [node[1]['color'] for node in graph_object.nodes(data=True)]
    return colors


def separate_members_individuals(graph_object):
    """separates member nodes from individual nodes
    :param graph_object: The NetworkX graph object
    :return subgraph_individuals: A data frame of individual nodes and their attributes
    :return subgraph_members: A data frame of member nodes and their attributes
    """

    subgraph_individuals = {}
    subgraph_members = {}

    for node in graph_object.nodes.data():
        dic = {node[0]: node[1]}

        if node[1]['type'] == 'individual':
            subgraph_individuals.update(dic)

        if node[1]['type'] == 'membership':
            subgraph_members.update(dic)

    # convert to dataframe
    subgraph_individuals = pd.DataFrame.from_dict(subgraph_individuals, orient='index')
    subgraph_members = pd.DataFrame.from_dict(subgraph_members, orient='index')

    return subgraph_individuals, subgraph_members


def format_member_individuals_for_concat(subgraph_members, subgraph_individuals, center):
    """
    Takes the individual and member dataframes, and outputs lists of lists to be aggregated
    later.
    """
    group_name = f'group-{center}'
    subgraph_individuals['group'] = group_name
    subgraph_members['group'] = group_name
    m2 = subgraph_members[['label', 'group']]
    i2 = subgraph_individuals.reset_index().rename(columns={'index': 'individual_id'})
    i2 = i2[['individual_id', 'group']]
    i2 = i2.values.tolist()
    m2 = m2.values.tolist()
    return i2, m2


def get_subgraphs(graph_object, min_nodes_in_subgraph):
    """Finds subgraphs and filters them for minimum number of desired nodes
    :param graph_object: The original big graph
    :param min_nodes_in_subgraph: The minimum number of nodes a subgraph should have
    :return multi: A list of the subgraphs
    """
    s = [graph_object.subgraph(c).copy() for c in nx.connected_components(graph_object)]
    n = min_nodes_in_subgraph
    multi = []

    for sub in s:
        if len(nx.nodes(sub)) >= n:
            multi.append(sub)

    print(f'{len(multi)} networks with at least {n} nodes')
    return multi


def get_subgraph_attributes(graph_object):
    """Returns some attributes about the subgraphs in a network"""

    node_counts = []
    s = [graph_object.subgraph(c).copy() for c in nx.connected_components(graph_object)]
    for sub in s:
        node_count = len(nx.nodes(sub))
        node_counts.append(node_count)

    attributes = {'Total Subgraphs': len(s),
                  'Min Nodes': min(node_counts),
                  'Max Nodes': max(node_counts),
                  'Average Nodes': sum(node_counts) / len(node_counts)
                  }

    print(f'Total Subgraphs: {len(s)}')
    print(f'Min Nodes: {min(node_counts)}')
    print(f'Max Nodes: {max(node_counts)}')
    print(f'Avg Nodes: {sum(node_counts) / len(node_counts)}')

    return attributes


def make_graph(graph_object, color_map):
    """Makes the graph and returns variables needed for further visualization
    :return center: center node
    :return title: the label of the center node used for titling visualizations
    :return node_count: the number of nodes
    :return fig1: the graph
    """

    fig1 = plt.figure()
    center = nx.center(graph_object)[0]
    title = graph_object.nodes[center]['label']

    # degrees = nx.degree(graph_object)
    node_count = len(nx.nodes(graph_object))

    # layout for display
    pos = nx.spring_layout(graph_object)

    # draw function
    nx.draw(graph_object, pos=pos, node_color=color_map, node_size=1000)

    # add node labels
    node_labels = nx.get_node_attributes(graph_object, 'label')
    nx.draw_networkx_labels(graph_object, pos=pos, labels=node_labels)

    # add edge labels
    edge_labels = nx.get_edge_attributes(graph_object, 'PARTICIPATION_TYPE')
    nx.draw_networkx_edge_labels(graph_object, pos, edge_labels)
    return center, title, node_count, fig1


def make_table(dataframe):
    """Format the attribute dataframe for printing"""
    fig2 = plt.figure(figsize=(4, 2))
    ax = fig2.add_subplot(111)

    ax.table(cellText=dataframe.values,
             rowLabels=dataframe.index,
             colLabels=dataframe.columns,
             loc="center"
             )
    ax.set_title("Summary")
    ax.axis("off")
    return fig2


def check_output():
    """Create output folder if it doesn't exist already"""
    pdf_output = f'{output_location}//pdfs'
    if os.path.isdir(output_location) == False:
        os.mkdir(output_location)
        os.mkdir(pdf_output)
    if os.path.isdir(output_location) == True:
        if os.path.isdir(pdf_output) == False:
            os.mkdir(pdf_output)


def make_pdf(fig1, fig2, title):
    """Export the graph image and the table to pdf"""
    pp = PdfPages(f'{output_location}//pdfs//{title}.pdf')
    pp.savefig(fig1, bbox_inches='tight')
    pp.savefig(fig2, bbox_inches='tight')
    pp.close()


def subgraph_output(multi, ind):
    """Iterates through the subgraphs, produces pdfs, and returns summary
    dataframe """
    subnetwork_df = []
    columns = ['Group title (Center)', 'PDF link', 'Nodes', 'Individuals', 'Memberships', 'Total Savings',
               'Total Loans', 'PPM', 'Dividends Paid', 'Interest Received']

    igroup = []
    mgroup = []

    for i in range(len(multi)):
        # specify subgraph
        graph = multi[i]
        colors = generate_color_map(graph, ind)

        # Set up graph visualization and get attributes
        center, title, node_count, fig1 = make_graph(graph, colors)

        # separate member nodes and individual nodes
        i, m = separate_members_individuals(graph)

        # extract group and member/individual pairs
        i2, m2 = format_member_individuals_for_concat(m, i, center)

        # concat to list
        igroup += i2
        mgroup += m2

        # calculate summary stats of membership attributes
        total_loan = sum(m['OPN_LN_BAL'])
        total_saving = sum(m['OPN_SV_BAL'])
        loan_count = sum(m['OPN_LN_ALL_CNT'])
        saving_count = sum(m['OPN_SV_ALL_CNT'])
        total_dividend = sum(m['DIV_YTD_AMT'])
        total_interest = sum(m['INT_YTD_AMT'])

        products_per_member = (loan_count + saving_count) / len(m)

        plt.title(f'The {title} network')

        # make summary table formatted for display
        account_dict = {'Center': title,
                        'Nodes': node_count,
                        'Individuals': len(i),
                        'Memberships': len(m),
                        'Total Savings': f'${total_saving:,.2f}',
                        'Total Loans': f'${total_loan:,.2f}',
                        'PPM': f'{products_per_member:.2n}',
                        'Dividends Paid': f'${total_dividend:,.2f}',
                        'Interest received': f'${total_interest:,.2f}'}

        act_df = pd.DataFrame.from_dict(account_dict, orient='index').rename(columns={0: ''})

        export_list = [title, f'=HYPERLINK("pdfs/{title}.pdf")', node_count, len(i), len(m), total_saving, total_loan,
                       products_per_member, total_dividend,
                       total_interest]

        # make the account summary table
        fig2 = make_table(act_df)

        # save graph and table as pdf
        make_pdf(fig1, fig2, title)

        subnetwork_df.append(export_list)

        # close the plot to save memory
        plt.close(fig1)
        plt.close(fig2)
    return subnetwork_df, columns, igroup, mgroup


def output_csvs(individual_group, member_group):
    """Save the tables containing individual/member and subgraph id (group)"""
    individual_group = pd.DataFrame(individual_group, columns=['INDIVIDUAL_ID', 'GROUP_ID'])
    member_group = pd.DataFrame(member_group, columns=['MEMBER_NBR', 'GROUP_ID'])
    individual_group.to_csv(f'{output_location}//{individual_group_csv_filename}{timestamp}.csv', index=False)
    member_group.to_csv(f'{output_location}//{member_group_csv_filename}{timestamp}.csv', index=False)


def output_excel(subnetwork_df, columns):
    """Save summary excel file"""
    d = pd.DataFrame(subnetwork_df, columns=columns)
    d.to_excel(f'{output_location}//{summary_xls_filename}-{timestamp}.xlsx')


def cli():
    """Initiate and run the app via command line"""
    db = input('Sqlite or DataMart?').lower()

    n = int(input('Subgraph size filter? Enter an integer.'))

    check_output()

    g, ind = generate_member_graph(db)

    multi = get_subgraphs(g, n)

    print('#'*14)
    print('Beginning export...')
    print(f'Output folder: {output_location}')
    print(f'To change export location, edit output_locations.py in the config folder')
    print('Generating graphics..')

    subnetwork_df, columns, igroup, mgroup = subgraph_output(multi, ind)

    # Export member/individual/group to csv
    print('Generating member/individual and group tables...')
    output_csvs(igroup, mgroup)

    # Export summary spreadsheet
    print('Generating summary spreadsheet...')
    output_excel(subnetwork_df, columns)

    # Export gexf
    print('Generating gexf...')
    nx.write_gexf(g, f'{output_location}//{gephx_filename}{timestamp}.gexf')

    print('All done')


def main():
    """Main function to execute the whole thing. Accepts 'gui' or 'cli' as argv"""
    import sys

    # If no argument is passed, default to GUI
    if len(sys.argv) < 2:
        import member_net.gui as gooey
        gooey.root.mainloop()

    # If an argument is passed, evaluate it
    else:
        mode = str(sys.argv[1]).lower()

        if mode == 'cli':
            cli()

        if mode == 'gui':
            import member_net.gui as gooey
            gooey.root.mainloop()

        else:
            print(f'Please input \'cli\' or \'gui\' only')
