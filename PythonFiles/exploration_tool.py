# Commentary:
#     First and foremost the exploration tool should be used to fetch and return additional components of information
#     relevant to the selections that the existing visualization generates. For example, if a user requests top occupations
#     within a Career Area, and one of those occupations seems to need more context, the user can rely on the exploration 
#     tool to deliver interesting and relevant data on that occupation to help the user understand why the visualization
#     looks as it does. An empirical example from our research so far comes from the occupation "Research Associate"
#     generating a significant amount of jobs that ask for maintenance and repair; by using the exploration tool to search
#     job titles or expand skill names, the user comes to understand that that skill request is actually relevant to 
#     managing sophisticated scientific equipment. As of now this tool can only access the data within the main_table but
#     in the future we would expect that all available data columns would be available to the user to explore. In the 
#     short run, however, we will have to omit the salary and geography based data for confidentiality reasons. 
#     It is important that the tool is agnostic to what the user might want to retrieve from the visualization. The tool 
#     will make the user aware of the available options and axes in which they can dig deeper into the available subset.
    
# Design goals:
#     We would like the user to be able to re-run the exploration tool if the bucket they have returned to them ends
#     up being too large in size. This of course would mean that the tool would need to somehow store the current 
#     filters and states. We assume that it would be fastest and easiest to have a tool that can branch from existing 
#     visualizations, since each of these narrow down and structure the data. However, ideally the long run goal such a 
#     tool would be to allow the user to begin exploration from scratch with the entire 4 million postings.

# User Experience:
#     In terms of UX we have developed a command line here for its simplicity and ease of implementation for proof of concept,
#     but the end goal would be to not remove the user from their visualization based experience so far. We do not 
#     envision the command-line style as the end goal of the UX for this tool.    

##############################################################################################################################

import os
import math
import pandas as pd
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 2000)
import numpy as np
from IPython.display import clear_output

# Import relevant dataframes:

main_table = pd.read_csv(r"C:\Users\bob65\Documents\Summer2019_Research\PythonFiles\_Data\Latest_Version\Main_Data\Main_Table_07122019.csv")
print(len(main_table))

'''
This function allows the user to chose from a pre-defined number of possible filters
and decide which column they would like to restrict. Potential restrictions are determined
by the 'category_names' list above and are passed into this function.
'''
def assisted_breakdowns(input_categories):
    print('Which fields would you like to define?')
    running = True
    first_run = True
    filters = []
    possible_avenues = input_categories.copy()
    while(running):
        if(not(first_run)):
            print('You have Chosen:', filters)
        print('Type one number at a time and press enter,' + 
          ' then when done type "/done"\nChoose one of these categories:')
        breakdowns = dict()
        size = len(possible_avenues)
        for i in range(len(possible_avenues)):
            print(i + 1, ':', possible_avenues[i])
            breakdowns[i + 1] = possible_avenues[i] 
        has_input = False
        print()
        while(not(has_input)):
            try:
                print()
                user_in = input('\tEnter number: ')
                user_in = int(user_in)
                filters.append(breakdowns[user_in])
                possible_avenues.remove(breakdowns[user_in])
                has_input = True
            except ValueError:
                if(user_in == '/done'):
                    running = False
                    break
                elif(user_in == '/stop'):
                    sys.exit("User Terminated Thread")
                else:
                    print('Please enter a number or "/done" if done')
            except KeyError:
                print('Number must be in the range displayed')
#         This line had some issues where it would prevent the user from inputing the next filter
#         clear_output(wait=True)
        first_run = False
        print()
    return(filters)

def restrict_categories(filters):
    full_table = main_table.copy()
    for column in filters:
        choices = pd.DataFrame(full_table[column].value_counts()).reset_index()['index'].values
        dictionary = dict()
        i = 1
        print('Selecting from', column)
        has_input = False
        while(not(has_input)):
            for option in choices:
                dictionary[i] = option
                print(i, ':', option)
                i+=1
#             The code below was an attempt to add a paging system for the results of a query. Some career areas have
#             hundreds of occupations within them, and therefore are a little much to scroll through at once.

#             print('Displaying %d to %d out of %d: (type "/next" for next 20, and "/prev" for previous 20)' % (1, 20, 20))
#             for q in range(20):
#                 print(q + 1, ':', dictionary[q+1])
            try:
                user_in = input('Choose a category and type its corresponding number: ')
                if(user_in == "/stop"):
                    sys.exit("User Terminated Thread")
                user_in = int(user_in)
                has_input = True
            except ValueError:
                print('Please enter a number.')
        print()
        full_table = full_table[full_table[column]==dictionary[user_in]]
    return(full_table)

# current_filters = []
category_names =['Career Area', 'Occupation', 'IPEDS Institution Name', 'Year', 'Metropolitan Statistical Area', 
                   'R1', '2-year', '4-year']
print('Welcome to the Exploration Tool!')
print('At any time type /stop to exit!\n')

out = assisted_breakdowns(category_names)
table = restrict_categories(out)
table