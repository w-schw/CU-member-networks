import pandas as pd
import numpy as np
import networkx as nx
import pyodbc
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.gridspec as gridspec
from datetime import datetime

def generate_member_graph(db_type):
    '''Generates the graph object using either sqlite or the datamart db.
    :param db_type: sqlite or datamart
    :return G: graph object
    :return ind: dataframe of the individuals, required to generate the color map.
    '''
    import sql_queries #sql_queries.py file

    # Including inside function for now, handle server name input and sqlite filepath input later
    sqlite_location = 'demo_data.db'
    MSSQL_server_name = 'XXXX'
    datamart_name = 'XXXX'

    if db_type == 'sqlite':
        from sqlite3 import connect
        conn = sqlite3.connect(sqlite_location)
        ind = pd.read_sql(sql_queries.sqlite_node_individual_query, conn)
        mem = pd.read_sql(sql_queries.sqlite_member_individual_query, conn)
        edges= pd.read_sql(sql_queries.sqlite_edge_query, conn)

    elif db_type == 'datamart':
        try:
            conn = pyodbc.connect('Driver={SQL Server};'
                          'Server='+str(MSSQL_server_name)+';'
                          'Database='+str(datamart_name)+';'
                          'Trusted_Connection=yes;', timeout=3)
        except:
            raise ValueError("Unable to connect to datamart")

        ind = pd.read_sql(sql_queries.ms_sql_node_individual_query, conn)
        mem = pd.read_sql(sql_queries.ms_sql_member_individual_query, conn)
        edges= pd.read_sql(sql_queries.ms_sql_edge_query, conn)

    else:
        raise ValueError("Please specify 'sqlite' or 'datamart'")

    # make attribute dictionary
    mem_dict = mem.set_index('member_nbr')
    mem_dict = mem_dict.to_dict('index')
    ind_dict = ind.set_index('individual_id')
    ind_dict = ind_dict.to_dict('index')

    mem_dict.update(ind_dict)

    # from pandas edgelist
    G = nx.from_pandas_edgelist(edges, edge_attr = True)
    nx.set_node_attributes(G, mem_dict)

    return G, ind

def generate_color_map(graph_object, individual_df):
    ''' Generates a color map corresponding with whether a node represents an individual or membership
    :param graph_object: NetworkX graph object
    :param individual_df: DataFrame of the individual table query
    :return colors: A list of colors to be passed to the networkx.draw() function
    '''
    individual_nodes = list(individual_df['individual_id'])

    for n in graph_object.nodes:
        graph_object.nodes[n]['color'] = 'c' if n in individual_nodes else 'm'

    colors = [node[1]['color'] for node in graph_object.nodes(data = True)]
    return(colors)

def separate_members_individuals(graph_object):
    '''separates member nodes from individual nodes
    :param graph_object: The NetworkX graph object
    :return subgraph_individuals: A data frame of individual nodes and their attributes
    :return subgraph_members: A data frame of member nodes and their attributes
    '''

    subgraph_individuals = {}
    subgraph_members = {}

    for node in graph_object.nodes.data():
        dic = {node[0]:node[1]}

        if node[1]['type']== 'individual':
            subgraph_individuals.update(dic)

        if node[1]['type']=='membership':
            subgraph_members.update(dic)

    # convert to dataframe
    subgraph_individuals = pd.DataFrame.from_dict(subgraph_individuals, orient='index')
    subgraph_members = pd.DataFrame.from_dict(subgraph_members, orient='index')

    return(subgraph_individuals, subgraph_members)

def get_subgraphs(graph_object, min_nodes_in_subgraph):
    '''Finds subgraphs and filters them for minimum number of desired nodes
    :param graph_object: The original big grah
    :param min_nodes_in_subgraph: The minimum number of nodes a subgraph should have
    :return multi: A list of the subgraphs
    '''
    S = [graph_object.subgraph(c).copy() for c in nx.connected_components(graph_object)]
    n = min_nodes_in_subgraph
    multi=[]

    for sub in S:
        if len(nx.nodes(sub))>=n:
            multi.append(sub)

    print(f'{len(multi)} networks with at least {n} nodes')
    return(multi)

def get_subgraph_attributes(graph_object):
    '''Returns some attribtues about the subgraphs in a network'''

    node_counts = []
    S = [graph_object.subgraph(c).copy() for c in nx.connected_components(graph_object)]
    for sub in S:
        node_count = len(nx.nodes(sub))
        node_counts.append(node_count)

    attributes = {'Total Subgraphs':len(S),
                  'Min Nodes':min(node_counts),
                  'Max Nodes':max(node_counts),
                  'Average Nodes': sum(node_counts)/len(node_counts)
                 }

    print(f'Total Subgraphs: {len(S)}')
    print(f'Min Nodes: {min(node_counts)}')
    print(f'Max Nodes: {max(node_counts)}')
    print(f'Avg Nodes: {sum(node_counts)/len(node_counts)}')

    return (attributes)

def make_graph(graph_object, color_map):
    '''Makes the graph and returns variables needed for further visualization
    :return center: center node
    :return title: the label of the center node used for titling visulizations
    :return node_count: the number of nodes
    :return fig1: the graph
    '''

    fig1=plt.figure()
    center = nx.center(graph_object)[0]
    title = graph_object.nodes[center]['label']
    degrees = nx.degree(graph_object)
    node_count = len(nx.nodes(graph_object))

    #layout for display
    pos = nx.spring_layout(graph_object)

    #draw function
    nx.draw(graph_object, pos=pos, node_color=color_map, node_size=1000)

    #add node labels
    node_labels = nx.get_node_attributes(graph_object,'label')
    nx.draw_networkx_labels(graph_object, pos=pos, labels = node_labels )

    #add edge labels
    edge_labels = nx.get_edge_attributes(graph_object, 'participation_type')
    nx.draw_networkx_edge_labels(graph_object, pos, edge_labels)
    return center, title, node_count, fig1

def make_table(dataframe):
    '''Format the attribute dataframe for printing'''
    fig2 = plt.figure(figsize = (4, 2))
    ax = fig2.add_subplot(111)

    ax.table(cellText = dataframe.values,
              rowLabels = dataframe.index,
              colLabels = dataframe.columns,
              loc = "center"
             )
    ax.set_title("Summary")
    ax.axis("off")
    return fig2

def make_pdf(fig1, fig2, title):
    '''Export the graph image and the table to pdf'''
    pp = PdfPages(f'{title}.pdf')
    pp.savefig(fig1, bbox_inches='tight')
    pp.savefig(fig2, bbox_inches='tight')
    pp.close()
