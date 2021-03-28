from member_subnetwork_functions import *

db = input('Sqlite or DataMart?')

n = int(input ('Subgraph size filter? Enter an interger.'))

G, ind = generate_member_graph(db)

multi = get_subgraphs(G, n)

print('Generating graphics..')

subnetwork_df = []
columns = ['Center', 'Nodes', 'Individuals', 'Memberships', 'Total Savings', 'Total Loans',
           'PPM', 'Dividends Paid', 'Interest Received']
timestamp = datetime.now().date().strftime("%b %d %Y ")

for i in range(8):
        #specify subgraph
    graph = multi[i]
    colors = generate_color_map(graph,ind)

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

print('Graphics saved to current directory.')
print('Generating spreadsheet...')

# Export to an excel spreadsheet with links to pdfs
d = pd.DataFrame(subnetwork_df, columns = columns)
d.to_excel(f'Member subnetworks - {timestamp}.xlsx')

print(f'Spreadsheet saved as Member subnetworks - {timestamp}.xlsx in the current directory.')
