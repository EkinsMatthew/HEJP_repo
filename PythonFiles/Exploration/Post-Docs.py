import pandas as pd
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 2000)
pd.set_option('display.max_colwidth', -1)
import numpy as np
import matplotlib.pyplot as plt
import probscale
import scipy
import scipy.stats as stats
import math

# Feel free to use any of the matplot styles that fit your fancy
# link to the doc: https://matplotlib.org/gallery/style_sheets/style_sheets_reference.html
plt.style.use('fivethirtyeight')

# Import relevant dataframes:
main_table = pd.read_csv(r"INSERT MAIN TABLE LOCATION HERE")
print(len(main_table))
faculty_table = pd.read_csv(r"INSERT FACULTY TABLE LOCATION HERE")
print(len(faculty_table))
skill_table = pd.read_csv(r"INSERT SKILL TABLE LOCATION HERE")
print(len(skill_table))


# Series of post-doc IDs useful for isolating all ['Post-Doctoral' = 1] postings by Job ID
mask = faculty_table[faculty_table['Post-Doctoral']==1][['Job ID']]
print(len(mask))
# This can then be used to perform a natural join on any of the above tables and extract
# post-doc only data. It is far simpler than trying to isolate the post-doc data using the
# faculty table each time; it saves memory and time as well!

############################################################
# General Functions
############################################################

def breakout(df, year, category):
    '''
    Generalized breakout for obtaining sizes of categories within a data column.
    
    Parameters:
    df (DataFrame): Full Pandas DataFrame used as the source for the breakout
    year (int): The year to which df will be restricted
    category (string): The cateogry by which the user would like to break out
    
    Returns:
    DataFrame with 
    '''
    cat = pd.DataFrame(df[category].value_counts()).reset_index()
    cat = cat.rename(columns={category:'count'})
    cat['inc'] = np.true_divide(cat['count'], num)
    
    return cat.sort_values(by='count', ascending=False)

def growth(df1, df2):
    df = df1.merge(df2, on='index', how='outer', indicator=True)
    df = df[df['_merge']=='both']
#     df['growth'] = np.true_divide(df['inc_y'] - df['inc_x'], df['inc_x'])
    df['growth'] = np.true_divide(df['count_y'] - df['count_x'], df['count_x'])
    return df.sort_values('growth', ascending=False).reset_index(drop=True)
    
############################################################
# Visualization 1)
# Post-Doc vs HEJP baseline by BEA Zone
############################################################    

# Use mask to obtain main_table subset that contains strictly post-doc postings
post = main_table.merge(mask, on='Job ID', how='inner')
post = post[~post['IPEDS Institution Name'].isnull()]

# Store the complement of this subset (all non-post-doc postings)
main = main_table.drop(post.index)
main = main[main['BEA_zone']!='Territories']

year1 = 2007
year2 = 2017

main_zone1 = breakout(main, year1, 'Institution_BEA_zone')
main_zone2 = breakout(main, year2, 'Institution_BEA_zone')

main_zone_g = growth(main_zone1, main_zone2, num1, num2)

zone1 = breakout(post, year1, 'Institution_BEA_zone')
zone2 = breakout(post, year2, 'Institution_BEA_zone')

zone_g = growth(zone1, zone2, num1, num2)

# Superimposed Categorical growth:
#     Two dataframes are used to graph categorical changes across two datasets and
#     two time periods. An example of this is postings within the post-doc bucket being
#     comapared to postings in HEJP as a whole in 2007 and 2017.
def super_graph_growth(df1, df2, category, years, title, type1, type2, colors1, colors2, scale1=1, scale2=1, top=10):
    '''
    Don't worry about this method. This is simply matplot code to generate the visual 
    for your convenience.
    
    If you choose to fiddle with it, do so by modifying the input arguments of the function.
    '''
    
    comb = df1.merge(df2, on='index', how='inner')
    comb = comb.sort_values(by='growth_y', ascending=False)
    comb = comb[:top]
    
#     display(comb)
    
    labels = comb['index'].values
    ind = np.arange(len(labels))
    width = 0.4
    
    first1 = comb['count_x_x'].values/scale1
    first2 = comb['count_y_x'].values/scale1
    
    second1 = comb['count_x_y'].values/scale2
    second2 = comb['count_y_y'].values/scale2
    
    top_y = max(max(np.amax(first1), np.amax(first2)), max(np.amax(second1), np.amax(second2))) * 1.1
    
    fig, ax2 = plt.subplots(figsize=(12, 6))
    
    bar3 = ax2.bar(ind-width/2, second1, width, color=colors2[0], label=str(years[0]) + ' ' + type2)
    bar4 = ax2.bar(ind+width/2, second2, width, color=colors2[1], label=str(years[1]) + ' ' + type2)
    
    ax2.set_ylim(top=top_y)
    ax2.set_ylabel('Number of ' + type2 + ' Jobs in ' + category + '\nScale Factor: ' + str(scale2))
    
    ax1 = ax2.twinx()
    ax1.grid(False)
    
    bar1 = ax1.bar(ind-width/2, first1, width/2, color=colors1[0], label=str(years[0]) + ' ' + type1)
    bar2 = ax1.bar(ind+width/2, first2, width/2, color=colors1[1], label=str(years[1]) + ' ' + type1)
    
    ax1.set_ylim(top=top_y)
    ax1.set_ylabel('Number of ' + type1 + ' Jobs in ' + category + '\nScale Factor: ' + str(scale1))
    
    plt.xticks(ind, labels, rotation=45, ha='right')
    plt.xlabel(category)
    
    bars = [bar1, bar3, bar2, bar4]
    labs = [b.get_label() for b in bars]
    plt.legend(bars, labs, loc='best')
    
    plt.title(title)
    
    plt.show()

    return None

# Graph Post-Doc vs HEJP baseline superimposed
super_graph_growth(zone_g, main_zone_g, 'BEA Zone', (2007, 2017), 'Post-Doc BEA Zone Growth vs HEJP Baseline\n2007 to 2017', 
                   'Post-Docs', 'HEJP', ('royalblue', 'goldenrod'), ('cornflowerblue', 'gold'), scale2=100)

############################################################
# Visualization 2)
# Overall Categorical Size Changes 2007-2017
############################################################  

# Total Categorical Size Changes

year1 = 2007
year2 = 2017

post = main_table.merge(mask, on='Job ID', how='inner')
main = main_table.drop(post.index)

post1 = post[post['Year']==year1]['Job ID'].nunique()
main1 = main[main['Year']==year1]['Job ID'].nunique()

post2 = post[post['Year']==year2]['Job ID'].nunique()
main2 = main[main['Year']==year2]['Job ID'].nunique()


table = pd.DataFrame([['Post-Doc', post1, post2], ['HEJP\n(No PD)', main1, main2]], columns=['Type', year1, year2])

table['growth'] = np.true_divide(table[year2]-table[year1], table[year1])

display(table)
                      
############################################################
# Visualization 3 & 4)
# Number of Post-Docs per region every year 2007-2010
############################################################ 
                      
post = main_table.merge(mask, on='Job ID', how='inner')
post = post[~post['IPEDS Institution Name'].isnull()]
years = [2007, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]
# Take the first 8 to avoid 'Territories'
zones = list(post['Institution_BEA_zone'].unique())[:8]
# zones = ['Plains', 'Mideast', 'New England']
tensor = np.zeros((len(years), 3, 0))

post = pd.DataFrame(post.groupby(['Institution_BEA_zone', 'Year', 'IPEDS Institution Name']).count()['Job ID']).reset_index()

# This loop composes a 3d array that has this structure
# (Year number, 1 of 3 metrics [Post-Doc counts, institution counts, post-docs per institution], BEA_zones)
for zone in zones:
    DF = post[post['Institution_BEA_zone']==zone]
    tuples = np.zeros((0, 3))
    for year in years:
        df = DF[DF['Year']==year]
        
#         df = df[df['Job ID']>=6]
    
        jobs = df['Job ID'].sum()
        inst = df['IPEDS Institution Name'].nunique()

        per = jobs/inst

        tuples = np.vstack((tuples, np.array((jobs, inst, per))))
    
    tensor = np.dstack((tensor, tuples))

ind = np.arange(len(years))
colors = ['royalblue', 'limegreen', 'firebrick', 'c', 'indigo', 'gold', 'deeppink', 'grey']
titles = ['Post-Doc Counts', 'Number of Institutions', 'Post per Institution']

# This makes line graphs of all three metrics, but in the presentation we only used the first in a line graph
for i in range(3):
    fig, ax = plt.subplots(figsize=(12,9))
    for j in range(len(zones)):
        ax.plot(tensor[:,i,j], color=colors[j], label=zones[j])
    plt.title(titles[i])
    plt.xticks(ind, years)
    plt.legend(loc='best')
    plt.show()
    
# Isolate Institution and per capita numbers in the most recent year (2017)
df = pd.DataFrame(tensor[8,1:,:])

# Make the columns readable
for i in range(len(zones)):
    df = df.rename(columns={i:zones[i]})

display(df)

############################################################
# Visualization 5)
# Top States with postings outside their borders
############################################################ 

cat1 = 'Institution_State'
cat2 = 'State'

# cat1 = 'Institution_BEA_zone'
# cat2 = 'BEA_zone'

# Get all combinations of institution state and state
diff = pd.DataFrame(post.groupby(['Year', cat1, cat2]).count()[['Job ID']]).reset_index()
# Throw out observations in the same state
diff = diff[diff[cat1]!=diff[cat2]]

# Regroup by the Institution state
diff = pd.DataFrame(diff.groupby([cat1]).sum()).reset_index()

diff.sort_values(by='Job ID', ascending=False)[:10]

############################################################
# Visualization 6)
# Skill Changes backed in from 2017
############################################################ 

# Obtain isolated post-doctoral skill dataframe
skill_p = skill_table.drop(columns=['Unnamed: 0', 'Unnamed: 0.1']).merge(mask, on='Job ID', how='inner')
# skill_f = skill_table.drop(columns=['Unnamed: 0', 'Unnamed: 0.1']).merge(faculty_table[faculty_table['Faculty']==1][['Job ID']], 
#                                                                          on='Job ID', how='inner')

# Method for isolating the skills in a year
def skill_break(df, year, NSF=None):
    df = df[df['Year']==year]
    s_df = df[df['Is Specialized Skill?']==1]
    
    if NSF is not None:
        mask = faculty_table[faculty_table[NSF]==1][['Job ID']]
        df = df.merge(mask, on='Job ID', how='inner')
        s_df = s_df.merge(mask, on='Job ID', how='inner')
    
    skills = pd.DataFrame(df['Skill Name'].value_counts()).reset_index()
    skills = skills.rename(columns={'Skill Name':'count'})
    skills['inc'] = np.true_divide(skills['count'], df['Job ID'].nunique())
    
    s_skills = pd.DataFrame(s_df['Skill Name'].value_counts()).reset_index()
    s_skills = s_skills.rename(columns={'Skill Name':'count'})
    s_skills['inc'] = np.true_divide(s_skills['count'], s_df['Job ID'].nunique())
    
    return skills, s_skills

# Method for graphing the raw ranks of the skills
def s_graph_rank(df, title, color='blue', top=10):
    
    df = df[:top]
    
    fig, ax = plt.subplots(figsize=(12,6))
    
    labels = df['index'].values
    counts = df['count'].values
    
    ind = np.arange(len(labels))
    
    ax.bar(ind, counts, color=color)
    
    plt.xticks(ind, labels, rotation=45, ha='right')
    plt.xlabel('Skill Name')
    plt.ylabel('Number with Skill')
#     plt.legend(loc='upper right')
    plt.title(title)
    
    plt.show()

# Define NSF fields of intrest
nsfs = ['Economics', 'Chemistry', 'Biological and biomedical sciences']
colors = [('royalblue', 'cornflowerblue'),('maroon', 'firebrick'),('goldenrod', 'gold'),('darkgreen', 'forestgreen'),
          ('indigo', 'rebeccapurple')]
year1 = 2010
year2 = 2017

def s_graph_growth(df, title, color='blue', top=10):
    
    df = df[:top]
    
    fig, ax = plt.subplots(figsize=(6,12))
    
    labels = df['index'].values
    counts = df['change'].values
    
    ind = np.arange(len(labels))
    
    ax.barh(ind, counts, color=color)
    
    plt.yticks(ind, labels, rotation=45, ha='right')
    plt.ylabel('change')
    plt.xlabel('Change in Demand')
#     plt.legend(loc='upper right')
    plt.title(title)
    
    plt.show()

def get_diffs(df):
    df['change'] = df['inc_y'] - df['inc_x']
    df['growth'] = np.true_divide(df['inc_y'] - df['inc_x'], df['inc_x'])
    return df.sort_values(by='change', ascending=False)

for i in range(len(nsfs)):
    nsf = nsfs[i]
    color = colors[i]
    
    print(nsf)
    
    # Faculty dataframes are commneted out
    
    skills1, s_skills1 = skill_break(skill_p, year1, NSF=nsf)
#     main_skills1, main_s_skills1 = skill_break(skill_f, year1, NSF=nsf)

    skills2, s_skills2 = skill_break(skill_p, year2, NSF=nsf)
#     main_skills2, main_s_skills2 = skill_break(skill_f, year2, NSF=nsf)

#     fac_s = main_s_skills1.merge(main_s_skills2[:10], on='index', how='right')
#     fac_s = get_diffs(fac_s)
    
    post_s = s_skills1.merge(s_skills2[:10], on='index', how='right')
    post_s = get_diffs(post_s)
    
    display(post_s)
    
    s_graph_rank(s_skills2, 'Top Ranked Skills for ' + nsf + '\nPost-Docs in 2017', color=color[1])
    s_graph_growth(post_s, 'Change in Demanding Percentage for Top\n' + nsf + ' Post-Doc Skills in 2017', color=color[1])
    