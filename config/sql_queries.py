#########################################################
# SQLITE QUERIES
########################################################

sqlite_node_individual_query = '''
SELECT individual_id,
first_name ||' '||last_name||' '||individual_id [label],
first_name ||' '||last_name [name],
open_date,
'individual'[type]
from individual_today
'''

sqlite_member_individual_query = '''
SELECT *, member_nbr [label],
'membership'[type]
FROM agr_membertotal_today
'''

sqlite_edge_query = '''
select member_nbr [source], individual_id [target], participation_type
FROM membershipparticipant_today
'''

########################################################
# MS SQL (Data Explorer) QUERIES
# Need to add filter for real accounts!
#######################################################

ms_sql_node_individual_query = '''
SELECT individual_id,
first_name + space(1) + last_name + space(1) + str(individual_id) [label],
first_name + space(1) + last_name [name],
-- open date equivalent
'individual' type
FROM individual_today

'''

ms_sql_member_individual_query = '''
SELECT *, member_nbr [label], 'membership' [type]
FROM AGR_MEMBERTOTAL_TODAY

'''

ms_sql_edge_query = '''
SELECT member_nbr [source], individual_id [target], participation_type
FROM membershipparticipant_today
'''
