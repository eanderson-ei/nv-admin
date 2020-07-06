"""
Name:     plotting.py
Author:   Erik Anderson
Created:  May 7, 2020
Revised:  May 7, 2020
Version:  Created using Python 2.7.10, Arc version 10.4.1
Requires: ArcGIS version 10.1 or later, Basic (ArcView) license or better

Copyright 2017-2020 Environmental Incentives, LLC.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

import pandas
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import Normalize
import matplotlib.patheffects as path_effects
import matplotlib.gridspec as gridspec
from matplotlib.font_manager import FontProperties

# TODO: Add switch to import arcpy.mp in Pro
from arcpy.mapping import PDFDocumentOpen
from arcpy import Delete_management as Delete

plt.rcParams['font.sans-serif'] = 'Tahoma'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 5

# def create_and_save_plots(workspace, current_data, proj_data, fakedata, projcredits):
###autolabels
def autolabel(rects, ax):
    '''
    creates & places labels for horizontal bar charts
    '''
    (x_left, x_right) = ax.get_xlim()
    x_width = x_right - x_left
    for rect in rects:
        width = rect.get_width()
        if width > x_width * 0.2:
            xy = (0, rect.get_y() + 0.3)
            color = 'white'
        else:
            xy = (width * 1.1, rect.get_y() + 0.3)
            color = 'black'
        ax.annotate('{:,.1f}'.format(width),
                    xy=xy,
                    xytext=(3, rect.get_height()/2),  
                    textcoords="offset points",
                    ha='left', 
                    va='center',
                    color=color,
                    fontsize=5)


def figure_one_ea(current_data, proj_data):
    # rename columns in projected and current data
    proj_data = proj_data[['map_unit_id', 'saleable_credits']]\
        .rename(columns = {'saleable_credits': 'proj_credits'})

    current_data = current_data[['map_unit_id', 'saleable_credits', 'map_unit_area', 'map_unit_name', 'meadow']]\
        .rename(columns = {'saleable_credits': 'current_credits'})
    
    # merge current and projected
    df = pd.merge(current_data, proj_data, on='map_unit_id')
    
    # replace nan with 0
    df.fillna(0, inplace=True)
    
    # sort by total credits
    df['total_credits'] = df[['current_credits', 'proj_credits']].sum(axis=1)
    df.sort(columns=['total_credits'], ascending=True, na_position='first', inplace=True)
    
    # drop 0 and na
    filt = (df['total_credits'] > 0) | (df['total_credits'].isnull())
    df = df.loc[filt, :].copy()
    
    # shorten map unit names to 45 characters
    df['map_unit_name'] = df['map_unit_name'].str[:45]
    
    # FIGURE
    # define figure
    fig, (tax, ax1, ax2) = plt.subplots(1,3, 
                                        sharey= True, 
                                        figsize = (7.5, 10.5),
                                        gridspec_kw={'width_ratios': [2, 1, 1]})
    
    # constants for this plot
    bar_height = .7
    font_size = 5
    
    # ACRES BAR CHART
    # left subplot shows map unit area
    plot1 = ax1.barh(
        bottom=np.arange(len(df.index)), 
        width=df['map_unit_area'],
        color='green',
        align='center',
        height=bar_height,
        edgecolor='none'
        )

    # label features
    autolabel(plot1, ax1)
    
    # # Configure ax1
    # ax1.set_xlabel('Map Unit Area \n(acres)')  # if x axis label is needed
    # ax1.xaxis.set_major_locator(plt.MaxNLocator(3))
    # ax1.xaxis.set_major_formatter(plt.FuncFormatter('{:,.0f}'.format))
    ax1.get_xaxis().set_visible(False)
    # Remove Axes ticks
    ax1.tick_params(axis='both', which='both', 
                    bottom=True, top=False, left=False, right=False)
    
    # y-axes
    ax1.get_yaxis().set_visible(False)
    ax1.set_ylim(-.5, len(df.index))
    
    for spine in ['right', 'top', 'bottom', 'left']:
        ax1.spines[spine].set_visible(False)
        
    # Add title above chart
    ax1.annotate('Map Unit Area (acres)', 
                 xy=(0,len(df.index)-(1.04-bar_height)),
                 fontsize=font_size,
                 fontweight='bold')
    
    # CREDIT BAR CHART
     # right subplot shows current and projected credits
    plot2_total = ax2.barh(
        bottom=np.arange(len(df.index)), 
        width=df['current_credits'] + df['proj_credits'], 
        color='red',
        align='center',
        height=bar_height,
        edgecolor='none')
    
    plot2_curr = ax2.barh(
        bottom=np.arange(len(df.index)), 
        width=df['current_credits'], 
        color='blue',
        align='center',
        height=bar_height,
        edgecolor='none')
    
    # Configure ax2
    #xaxes
    # ax2.set_xlabel('Credits')  # if x axis label is needed
    # ax2.xaxis.set_major_locator(plt.MaxNLocator(3))
    # ax2.xaxis.set_major_formatter(plt.FuncFormatter('{:,.0f}'.format))
    ax2.get_xaxis().set_visible(False)
    # Remove Axes ticks
    ax2.tick_params(axis='both', which='both', 
                    bottom=True, top=False, left=False, right=False)
    
    # yaxes
    ax2.get_yaxis().set_visible(False)

    
    for spine in ['right', 'top', 'bottom', 'left']:
        ax2.spines[spine].set_visible(False)
    
    # Title above chart
    ax2.annotate('Current / Projected Credits', 
                xy=(0,len(df.index)-(1.04-bar_height)),
                fontsize=font_size,
                fontweight='bold')
    
    # label current and projected credits
    (x_left, x_right) = ax2.get_xlim()
    x_width = x_right - x_left
    for rect, current, projected in zip(plot2_total, df['current_credits'], df['proj_credits']):
        width = rect.get_width()
        if width > x_width * 0.3:
            xy = (0, rect.get_y() + 0.3)
            color = 'white'
        else:
            xy = (width * 1.2, rect.get_y() + 0.3)
            color = 'black'
        ax2.annotate('{:,.1f} / {:,.1f}'.format(current, projected),
                    xy=xy,
                    xytext=(3, rect.get_height()/2),  
                    textcoords="offset points",
                    ha='left', 
                    va='center',
                    color=color,
                    fontsize=font_size)
    
    # Add Legend
    # ax2.legend(plot2_curr, ['Projected Credits', 'Current Credits'],
    #            loc=4)
    
    # TABLE
    # define table
    cell_text = []
    for row in df[['map_unit_id', 'map_unit_name', 'meadow']].iterrows():
        cell_text.append(list(row[1]))
    cell_text.reverse()

    # define header and cell heights
    header_height = 0.5 * (1 / float(len(df.index)))
    cell_height = (1 - header_height) / float(len(df.index))
    
    # Add table to tax
    table = tax.table(cellText=cell_text,
                cellLoc='right',
                colLabels=['ID', 'Map Unit Name', 'Meadow'],
                colLoc='right',
                colWidths=[0.1, 0.7, 0.2],
                loc='center')

    for pos, cell in table.get_celld().items():
        # set cell heights
        if pos[0] == 0:
            cell.set_height(header_height)
            cell.set_text_props(weight='bold')
            # cell.set_facecolor('grey')
        else:
            cell.set_height(cell_height)
        
        # remove border
        cell.set_edgecolor('white')
    
    # add horizontal rules between table lines
    for ax in (tax, ax1, ax2):
        for y_start in np.arange(.5, len(df.index)+.5, 1):
            ax.axhline(y=y_start,
                        xmin=0,
                        xmax=1,
                        color='grey',
                        linewidth=.1)
    
    # change table font size
    table.auto_set_font_size(False)
    table.set_fontsize(font_size)
    
    # remove axes around table
    tax.get_yaxis().set_visible(False)
    tax.get_xaxis().set_visible(False)
    for spine in ['right', 'top', 'bottom', 'left']:
        tax.spines[spine].set_visible(False)
    
    # remove space between subplots
    plt.subplots_adjust(wspace=0)
    
    return fig
    
    
def figure_one(current_data, proj_data):
    ###### FIGURE 1
    # bar chart of MU current conditions

    ##Data Wrangling
    #merge projected credits & current credits 
    plotmu = current_data.merge(proj_data[['map_unit_id', 'saleable_credits']].rename(columns = {'saleable_credits': 'proj_credits'}), on = 'map_unit_id')
    #ID Max Credits (whether current or projected)
    plotmu['maxcredits'] = plotmu[['saleable_credits', 'proj_credits']].max(axis =1) ###identify maximum credits 

    ### sort by maxcredits
    plotmu = plotmu.sort(columns=['maxcredits'], ascending = True, na_position = 'first')
    plotmu['map_unit_id'] = plotmu['map_unit_id'].astype(str)
    ## drop 0s
    plotmu = plotmu[plotmu['maxcredits'] != 0]
    ##drop Na in max credits
    plotmu.dropna(subset=['maxcredits'], inplace=True)

    ##define caption
    t= ("This graph shows the current and projected uplift on each Map Unit \n as entered in the Credit Calculator. The labels indicate the max number \nof credits,"
        " regardlesss of it they are current on predicted. \n As shown, Map Unit 19 has the greatest"
        " total number of credits, with \n 817 current credits") 
    ##TODO: Figure out how to make this dynamic text

    # ##plot
    # fig, ax = plt.subplots(figsize = (7,9))
    # fig.set_size_inches(7, 9, forward=True)

    # p0= ax.barh(plotmu['map_unit_id'], width = plotmu['maxcredits'])
    # p1 = ax.barh(plotmu['map_unit_id'], width = plotmu['proj_credits'])
    # p2 = ax.barh(plotmu.map_unit_id, width = plotmu.credits)
    # ax.text(-1,-8, t, family = 'serif', ha = 'left')
    # #txt._get_wrap_line_width = lambda : 600.
    # ax.set_ylabel('Map Unit #')
    # ax.set_xlabel('Credits')
    # ax.set_title('Credits Per Map Unit')
    # ax.legend((p1[0], p2[0]), ('Predicted', 'Current'))

    # autolabel(p0, ax)
    # fig.tight_layout()
    
    # return fig

#######################################################################
    ### new bar graph
    #############################################
    ## format: two columns, 1 row
    ## sort by saleable credits/maximum credits
    celltext = plotmu['map_unit_name'].values.tolist()
    celltext.reverse()
    celltext += [' ']
    rows = plotmu['map_unit_id'].values.tolist()
    rows.reverse()
    rows += [' ']
    cell_long = [[i] for i in celltext]

    prop_bars = 0.92 


    fig, (ax1, ax2) = plt.subplots(1,2, sharey= True, figsize = (7,9))
    cell_height = (1 /(len(plotmu['map_unit_id']))) * prop_bars

    plot1 = ax1.barh(plotmu['map_unit_id'], width = plotmu['map_unit_area'])
    #could use ax1. get_window_extent() ? returns 489 tho, so confused what that unit is. 
    ax1.set_ylabel('Map Unit #')
    ax1.set_xlabel('Acres')
    autolabel(plot1, ax1) ##use function defined above for labels 
    table = ax1.table(cellText=cell_long,
                cellLoc = 'center',
                rowLabels = rows,
                colLabels = 'Map Unit Name',
                loc = 'left')

    for pos, cell in table.get_celld().items():
        if pos == (0,0): 
            cell.set_height((1-prop_bars)/2)
        elif pos == (len(rows),0) or pos == (len(rows),-1):
            cell.set_height((1-prop_bars)/2)
        else:
            cell.set_height(cell_height)


        ##set header row to be static
        ##set the rest of the cells to be 1/# of map units

    #ax2.barh(plotmu['map_unit_id'], width = plotmu['maxcredits'])
    ax2.barh(plotmu['map_unit_id'], width = plotmu['proj_credits'])
    ax2.barh(plotmu['map_unit_id'], width = plotmu['saleable_credits'])
    ax2.set_xlabel('Credits')
    ax2.legend(['Projected Credits', 'Current Credits'])
    ### 
    #column 1

    ##table
    #MU#, MUN, MapUnit Area w/ label (acres)
    ####
    ##column 2 in 


    ###########
    ##Figure 2. Scenarios Compared to Calculator
    #####

    ##graph it
    # fig, ax = plt.subplots(figsize = (7,9))

    # p= ax.barh(plotmu2['map_unit_id'], width = plotmu2['max'], color = plotmu2['color'])
    # autolabel(p)
    # ##Erik- the only way I could figure out how to put a label on this graph was to create this invisible graph below. unfortunately it iterates over each of the colors and takes a while. please help. 

    # for i, j in color_dict.items(): #Loop over color dictionary
    #     ax.barh(plotmu2['map_unit_id'], width = 0 ,color=j,label=i) #Plot invisible bar graph but have the legends specified


    # p1 = ax.barh(plotmu['map_unit_id'], width = plotmu['maxcredits'], color = 'gray', label = "Max Credits \n from Calc")

    # ax.text(-1,-9, t, family = 'serif', ha = 'left', wrap = True)

    # ax.set_ylabel('Map Unit #')
    # ax.set_xlabel('Credits')
    # ax.set_title('Credits Per Map Unit Based on Ideal Management Regime')
    # ax.legend()
    # fig.tight_layout()
    
    return fig

def figure_two_ea(scenario_data, current_data, proj_data):
    """shows conifer and additional credits over projected with ideal management scenario"""
    # rename columns in projected and current data
    proj_data = proj_data[['map_unit_id', 'saleable_credits']]\
        .rename(columns = {'saleable_credits': 'proj_credits'})

    current_data = current_data[['map_unit_id', 'saleable_credits', 'map_unit_area', 'map_unit_name', 'meadow']]\
        .rename(columns = {'saleable_credits': 'current_credits'})
    
    # merge current and projected
    df = pd.merge(current_data, proj_data, on='map_unit_id')
    
    # find max credits generated for each MU and associated management regime
    scenario_data['max'] = scenario_data.iloc[:,4:-1].max(axis=1)  # exclude conifer at end
    scenario_data['idmax'] = scenario_data.iloc[:,4:-1].idxmax(axis=1)

    # merge scenario calc
    df = pd.merge(df, scenario_data, on=['map_unit_id', 'map_unit_name'])
    
    # replace nan with 0
    df.fillna(0, inplace=True)
    
    # sort by total credits
    df['total_credits'] = df[['current_credits', 'proj_credits']].sum(axis=1)
    df['best'] = df[['max', 'total_credits']].max(axis=1)
    df.sort(columns=['best'], ascending=True, na_position='first', inplace=True)
    
    # drop 0 and na
    filt = (df['best'] > 0) | (df['best'].isnull())
    df = df.loc[filt, :].copy()
    
    # shorten map unit names to 45 characters
    df['map_unit_name'] = df['map_unit_name'].str[:45]
    
    # define colors for bars
    color_dict = {
        'forb_grass_high': (1,0,0,1),
        'forb_grass_med': (1,0,0,0.75),
        'forb_grass_low': (1,0,0,0.50),
        'shrub_high': (0,1,0,1),
        'shrub_med': (0,1,0,0.75),
        'shrub_low': (0,1,0,0.50),
        'brotec_high': (0,0,1,1),
        'brotec_med': (0,0,1,0.75),
        'brotec_low': (0,0,1,0.50)
        }

    df['color'] = df['idmax'].map(color_dict)
    
    # FIGURE
    # define figure
    fig, (tax, ax1, ax2) = plt.subplots(1,3, 
                                        sharey= True, 
                                        figsize = (7.5, 10.5),
                                        gridspec_kw={'width_ratios': [2, 1, 1]})
    
    # constants for this plot
    bar_height = .7
    font_size = 5
    
    # ACRES BAR CHART
    # left subplot shows map unit area
    plot1 = ax1.barh(
        bottom=np.arange(len(df.index)), 
        width=df['conifer'],
        color='green',
        align='center',
        height=bar_height,
        edgecolor='none'
        )

    # label features
    autolabel(plot1, ax1)
    
    # # Configure ax1
    # ax1.set_xlabel('Map Unit Area \n(acres)')  # if x axis label is needed
    # ax1.xaxis.set_major_locator(plt.MaxNLocator(3))
    # ax1.xaxis.set_major_formatter(plt.FuncFormatter('{:,.0f}'.format))
    ax1.get_xaxis().set_visible(False)
    # Remove Axes ticks
    ax1.tick_params(axis='both', which='both', 
                    bottom=True, top=False, left=False, right=False)
    
    # y-axes
    ax1.get_yaxis().set_visible(False)
    ax1.set_ylim(-.5, len(df.index))
    
    for spine in ['right', 'top', 'bottom', 'left']:
        ax1.spines[spine].set_visible(False)
        
    # Add title above chart
    ax1.annotate('Conifer Credits', 
                 xy=(0,len(df.index)-(1.04-bar_height)),
                 fontsize=font_size,
                 fontweight='bold')
    
    # CREDIT BAR CHART
     # right subplot shows current and projected credits
    plot_max = ax2.barh(
        bottom=np.arange(len(df.index)), 
        width=df['current_credits'] + df['max'],  # scenario credits are calculated relative to current credits
        color=df['color'],
        align='center',
        height=bar_height,
        edgecolor='none')
    
    plot_total = ax2.barh(
        bottom=np.arange(len(df.index)), 
        width=df['current_credits'] + df['proj_credits'], 
        color='grey',
        align='center',
        height=bar_height,
        edgecolor='none')
    
    # Configure ax2
    #xaxes
    # ax2.set_xlabel('Credits')  # if x axis label is needed
    # ax2.xaxis.set_major_locator(plt.MaxNLocator(3))
    # ax2.xaxis.set_major_formatter(plt.FuncFormatter('{:,.0f}'.format))
    ax2.get_xaxis().set_visible(False)
    # Remove Axes ticks
    ax2.tick_params(axis='both', which='both', 
                    bottom=True, top=False, left=False, right=False)
    
    # yaxes
    ax2.get_yaxis().set_visible(False)

    
    for spine in ['right', 'top', 'bottom', 'left']:
        ax2.spines[spine].set_visible(False)
    
    # Title above chart
    ax2.annotate('Additional Credits', 
                xy=(0,len(df.index)-(1.04-bar_height)),
                fontsize=font_size,
                fontweight='bold')
    
    # calculate additional credits and set negative to zero
    df['add_credits'] = (df['current_credits'] + df['max']) - (df['current_credits'] + df['proj_credits'])
    filt = df['add_credits'] <= 0
    df.loc[filt, 'add_credits'] = 0
    df.loc[filt, 'idmax'] = ''
    
    # label current and projected credits
    (x_left, x_right) = ax2.get_xlim()
    x_width = x_right - x_left
    for rect, add_credits, best in zip(plot_total, df['add_credits'], df['best']):
        width = rect.get_width()
        if add_credits > 1:
            if best > x_width * 0.3:
                xy = (0, rect.get_y() + 0.3)
                color = 'white'
            else:
                xy = (best * 1.2, rect.get_y() + 0.3)
                color = 'black'
            ax2.annotate('+{:,.1f} credits'.format(add_credits),
                        xy=xy,
                        xytext=(3, rect.get_height()/2),  
                        textcoords="offset points",
                        ha='left', 
                        va='center',
                        color=color,
                        fontsize=font_size)
    
    # Add Legend
    # ax2.legend(plot_total, ['Projected Credits'],
    #            loc=4,
    #            frameon=True,
    #            borderpad=.75,
    #            fancybox=True)
    
    # TABLE
    # define table
    cell_text = []
    for row in df[['map_unit_id', 'map_unit_name', 'idmax']].iterrows():
        cell_text.append(list(row[1]))
    cell_text.reverse()

    # define header and cell heights
    header_height = 0.5 * (1 / float(len(df.index)))
    cell_height = (1 - header_height) / float(len(df.index))
    
    # Add table to tax
    table = tax.table(cellText=cell_text,
                cellLoc='right',
                colLabels=['ID', 'Map Unit Name', 'Recommendation'],
                colLoc='right',
                colWidths=[0.1, 0.7, 0.2],
                loc='center')

    for pos, cell in table.get_celld().items():
        # set cell heights
        if pos[0] == 0:
            cell.set_height(header_height)
            cell.set_text_props(weight='bold')
            # cell.set_facecolor('grey')
        else:
            cell.set_height(cell_height)
        
        # remove border
        cell.set_edgecolor('white')
    
    # add horizontal rules between table lines
    for ax in (tax, ax1, ax2):
        for y_start in np.arange(.5, len(df.index)+.5, 1):
            ax.axhline(y=y_start,
                        xmin=0,
                        xmax=1,
                        color='grey',
                        linewidth=.1)
    
    # change table font size
    table.auto_set_font_size(False)
    table.set_fontsize(font_size)
    
    # remove axes around table
    tax.get_yaxis().set_visible(False)
    tax.get_xaxis().set_visible(False)
    for spine in ['right', 'top', 'bottom', 'left']:
        tax.spines[spine].set_visible(False)
    
    # remove space between subplots
    plt.subplots_adjust(wspace=0)
    
    return fig


def figure_two(scenario_data, current_data, proj_data):
    """shows additional credits over projected with ideal management scenario"""
    # rename columns in projected and current data
    proj_data = proj_data[['map_unit_id', 'saleable_credits']]\
        .rename(columns = {'saleable_credits': 'proj_credits'})

    current_data = current_data[['map_unit_id', 'saleable_credits', 'map_unit_area', 'map_unit_name', 'meadow']]\
        .rename(columns = {'saleable_credits': 'current_credits'})
    
    # merge current and projected
    df = pd.merge(current_data, proj_data, on='map_unit_id')

    ###find max credits generated for each MU and associated management regime
    scenario_data['max'] = scenario_data.iloc[:,4:-1].max(axis=1)  # exclude conifer at end
    scenario_data['idmax'] = scenario_data.iloc[:,4:-1].idxmax(axis=1)

    # merge scenario calc
    df = pd.merge(df, scenario_data, on='map_unit_id')
    
    # replace nan with 0
    df.fillna(0, inplace=True)
    
    
    df['total'] = df['max'] + df['current_credits'] + df['proj_credits']
    df.sort(columns=['total'], ascending=True, na_position='first', inplace=True)
    
    # drop where no aditional credits are created  # KEEP ALL FOR CONIFER
    filt = df['max'] > (df['current_credits'] + df['proj_credits'])
    df = df[filt].copy()
    
    # define colors for bars
    color_dict = {
        'forb_grass_high': (1,0,0,1),
        'forb_grass_med': (1,0,0,0.75),
        'forb_grass_low': (1,0,0,0.50),
        'shrub_high': (0,1,0,1),
        'shrub_med': (0,1,0,0.75),
        'shrub_low': (0,1,0,0.50),
        'brotec_high': (0,0,1,1),
        'brotec_med': (0,0,1,0.75),
        'brotec_low': (0,0,1,0.50)
        }

    df['color'] = df['idmax'].map(color_dict)
    
    fig, (tax, ax) = plt.subplots(1,2, 
                                    sharey= True, 
                                    figsize = (7,9),
                                    gridspec_kw={'width_ratios': [1, 1]})
    
    bar_height = .7
    font_size = 8
                                   
    plot_max = ax.barh(
        bottom=np.arange(len(df.index)), 
        width=df['max'],
        color=df['color'],
        align='center',
        height=bar_height)
    
    plot_total = ax.barh(
        bottom=np.arange(len(df.index)), 
        width=df['current_credits'] + df['proj_credits'], 
        color='grey',
        align='center',
        height=bar_height)
    
    # ax2.xaxis.set_major_formatter(plt.FuncFormatter('{:,.0f}'.format))
    ax.get_xaxis().set_visible(False)
    # Remove Axes ticks
    ax.tick_params(axis='both', which='both', 
                    bottom=True, top=False, left=False, right=False)
    
    # yaxes
    ax.get_yaxis().set_visible(False)

    
    # for spine in ['right', 'top', 'bottom', 'left']:
    #     ax.spines[spine].set_visible(False)
    
    # Title above chart
    ax.annotate('Additional Credits', 
                xy=(0,len(df.index)-(1.04-bar_height)),
                fontsize=font_size,
                fontweight='bold')
    
    # label current and projected credits
    (x_left, x_right) = ax.get_xlim()
    x_width = x_right - x_left
    for rect, add_credits in zip(plot_total, (df['max'] - (df['current_credits'] + df['proj_credits']))):
        width = rect.get_width()
        if width > x_width * 0.3:
            xy = (0, rect.get_y() + 0.3)
            color = 'white'
        else:
            xy = (width * 1.2, rect.get_y() + 0.3)
            color = 'black'
        ax.annotate('+{:,.1f} credits'.format(add_credits),
                    xy=(width * 1.2, rect.get_y() + 0.3),
                    xytext=(3, rect.get_height()/2),  
                    textcoords="offset points",
                    ha='left', 
                    va='center',
                    color='black',
                    fontsize=font_size)
        
    # TABLE
    # define table
    cell_text = []
    for row in df[['map_unit_id', 'map_unit_name_x', 'idmax']].iterrows():
        cell_text.append(list(row[1]))
    cell_text.reverse()

    # define header and cell heights
    header_height = 0.5 * (1 / float(len(df.index)))
    cell_height = (1 - header_height) / float(len(df.index))
    
    # Add table to tax
    table = tax.table(cellText=cell_text,
                cellLoc='right',
                colLabels=['ID', 'Map Unit Name', 'Best'],
                colLoc='right',
                colWidths=[0.1, 0.7, 0.2],
                loc='center')

    for pos, cell in table.get_celld().items():
        # set cell heights
        if pos[0] == 0:
            cell.set_height(header_height)
            cell.set_text_props(weight='bold')
            # cell.set_facecolor('grey')
        else:
            cell.set_height(cell_height)
        
        # remove border
        cell.set_edgecolor('white')
    
    # add horizontal rules between table lines
    for ax1 in (tax, ax):
        for y_start in np.arange(.5, len(df.index)+.5, 1):
            ax1.axhline(y=y_start,
                        xmin=0,
                        xmax=1,
                        color='grey',
                        linewidth=.1)
    
    # change table font size
    table.auto_set_font_size(False)
    table.set_fontsize(font_size)
    
    # remove axes around table
    tax.get_yaxis().set_visible(False)
    tax.get_xaxis().set_visible(False)
    for spine in ['right', 'top', 'bottom', 'left']:
        tax.spines[spine].set_visible(False)
    
    # remove space between subplots
    plt.subplots_adjust(wspace=0)

    # #reshape for plotting
    # plotmu2 = pd.melt(plotmu1, id_vars=["map_unit_id", "credits", "max", "idmax"], 
    #                   var_name = "Mngmt_Scenario", 
    #                   value_name = "optimal_credits")

    # plotmu2 = plotmu2.sort(columns=['max'], 
    #                        ascending = False, 
    #                        na_position = 'first', 
    #                        ignore_index= True)
    # plotmu2['map_unit_id'] = plotmu2['map_unit_id'].astype(str)

    #list of Management Options Included
    # management_options = plotmu2.idmax.unique() 

    

    ##set caption
    #TODO change to dynamic text
    t= ("This graph shows the projected credits for each Map Unit based on the \n ideal management regime. \n These 'idealized' credits are compared to the maximum credits in the calcualator \n (either predicted or current). As shown, Map Unit 19 has the greatest total number \n of credits, with  902 current credits, if Restoration Management Scenarion 5 \n(High Effort Level) is used") 

    #######################################################################
    ### new bar graph
    #############################################
    ## format: two columns, 1 row
    ## sort by saleable credits/maximum credits
    # celltext = plotmu['map_unit_name'].values.tolist()
    # celltext.reverse()
    # celltext += [' ']
    # rows = plotmu['map_unit_id'].values.tolist()
    # rows.reverse()
    # rows += [' ']
    # cell_long = [[i] for i in celltext]

    # prop_bars = 0.92 * 8


    # fig, (ax1, ax2) = plt.subplots(1,2, sharey= True, figsize = (7,9))
    # cell_height = (1 /(len(plotmu['map_unit_id']))) * prop_bars

    # plot1 = ax1.barh(plotmu['map_unit_id'], width = plotmu['map_unit_area'], align = 'center')
    # #could use ax1. get_window_extent() ? returns 489 tho, so confused what that unit is. 
    # ax1.set_ylabel('Map Unit #')
    # ax1.set_xlabel('Acres')
    # autolabel(plot1, ax1) ##use function defined above for labels 
    # table = ax1.table(cellText=cell_long,
    #             cellLoc = 'center',
    #             rowLabels = rows,
    #             colLabels = 'Map Unit Name',
    #             loc = 'left', 
    #             edges = 'horizontal')

    # for pos, cell in table.get_celld().items():
    #     if pos == (0,0): 
    #         cell.set_height((1-prop_bars)/2)
    #     elif pos == (len(rows),0) or pos == (len(rows),-1):
    #         cell.set_height((1-prop_bars)/2)
    #     else:
    #         cell.set_height(cell_height)


        ##set header row to be static
        ##set the rest of the cells to be 1/# of map units

    #ax2.barh(plotmu['map_unit_id'], width = plotmu['maxcredits'])
    # ax2.barh(plotmu['map_unit_id'], width = plotmu['proj_credits'])
    # ax2.barh(plotmu['map_unit_id'], width = plotmu['saleable_credits'])
    # ax2.set_xlabel('Credits')
    # ax2.legend(['Projected Credits', 'Current Credits'])
    ### 
    #column 1

    ##table
    #MU#, MUN, MapUnit Area w/ label (acres)
    ####
    ##column 2 in 


    ###########
    ##Figure 2. Scenarios Compared to Calculator
    #####

    ##graph it
    # fig, ax = plt.subplots(figsize = (7,9))

    # p= ax.barh(plotmu2['map_unit_id'], width = plotmu2['max'], color = plotmu2['color'])
    # autolabel(p)
    # ##Erik- the only way I could figure out how to put a label on this graph was to create this invisible graph below. unfortunately it iterates over each of the colors and takes a while. please help. 

    # for i, j in color_dict.items(): #Loop over color dictionary
    #     ax.barh(plotmu2['map_unit_id'], width = 0 ,color=j,label=i) #Plot invisible bar graph but have the legends specified


    # p1 = ax.barh(plotmu['map_unit_id'], width = plotmu['maxcredits'], color = 'gray', label = "Max Credits \n from Calc")

    # ax.text(-1,-9, t, family = 'serif', ha = 'left', wrap = True)

    # ax.set_ylabel('Map Unit #')
    # ax.set_xlabel('Credits')
    # ax.set_title('Credits Per Map Unit Based on Ideal Management Regime')
    # ax.legend()
    # fig.tight_layout()
    
    return fig

def figure_three(regimes, workspace):
    #####

    ####
    #Deep Dive into Management Options##
    # 1/2 page per scenario
    ## for each management scenario

    regimes = ['rest1', 'rest2', 'rest3', 'rest4', 'rest5'] ## Fake Data; this needs to be changed to match scenario tool

    ## Add in Projected Credits to Fake Data
    plotmu1 = plotmu1.merge(projcredits, on = 'map_unit_id')

    for i in regimes: 

        ####comparison charts wrangling
        current_regime = []
        current_scenario = []
        t = "Management Regime #{}".format(i[-1])
        current_regime.append('{}_l'.format(i))
        current_regime.append('{}_m'.format(i))
        current_regime.append('{}_h'.format(i))
        current_scenario = plotmu1[['map_unit_id', 'credits', 'max', 'idmax', current_regime[0], current_regime[1], current_regime[2]]]
        current_scenario = current_scenario.merge(projcredits, on = 'map_unit_id')

        totals = plotmu1[['credits', 'proj_credits', current_regime[0], current_regime[1], current_regime[2]]].sum(axis = 0)

        ##set caption
        graph1cap= "The  graph above compares current, predicted, and modelled credit creation opportunities across \n the project site. The left-most bars represent different levels of effort of this management regime \n \n The table below captures the Map Units that will be most improved by this  management regime, and \n shows the number of credits predicted under each effort level. \n \n The barchart below shows the same information, but in credits per acre in order to normalize the effect of \n total number of acres."
    ### Table information

    #Table Top 5-10 MUs that show the greatest increase - functional acre uplift per acre
    ##TODO: make this a loop so you don't have it over 4 lines
        acres = fakedata[['map_unit_id', 'map_unit_area']]
        current_scenario=current_scenario.merge(acres, on = 'map_unit_id')
        current_scenario['low_increase_per_acre'] = (current_scenario['{}_l'.format(i)] / current_scenario['map_unit_area'])
        current_scenario['m_increase_per_acre'] = (current_scenario['{}_m'.format(i)] / current_scenario['map_unit_area'])
        current_scenario['h_increase_per_acre'] = (current_scenario['{}_h'.format(i)] / current_scenario['map_unit_area'])

    ###straight numbers for table
        subtable = current_scenario[['map_unit_id', 'credits','proj_credits', '{}_l'.format(i),'{}_m'.format(i), '{}_h'.format(i)]]

        col_name_dict1 = {'map_unit_id':'MU', 'credits': 'Current Credits', 'proj_credits': 'Projected Creds', 'low_increase_per_acre': 'Percent Increase/Acre: LOW', 'm_increase_per_acre': 'Percent Increase/Acre: MEDIUM', 'h_increase_per_acre':'Percent Increase/Acre: HIGH', '{}_l'.format(i): 'Low Effort', '{}_m'.format(i): 'Medium Effort', '{}_h'.format(i): 'High Effort'}

        subtable = subtable.rename(columns = col_name_dict1).round(decimals =2)
        subtable = subtable[subtable["High Effort"] > subtable['Projected Creds']].sort(columns= "High Effort", ascending = False)

        if len(subtable) >10: 
            subtable= subtable[0:10]

    ######
        table = current_scenario[['map_unit_id', 'credits', 'low_increase_per_acre', 'm_increase_per_acre', 'h_increase_per_acre']].sort(columns= "h_increase_per_acre", ascending = False)

        col_name_dict = {'map_unit_id':'MU', 'credits': 'Current Credits', 'low_increase_per_acre': 'Percent Increase/Acre: LOW', 'm_increase_per_acre': 'Percent Increase/Acre: MEDIUM', 'h_increase_per_acre':'Percent Increase/Acre: HIGH'}
        
        table = table.rename(columns = col_name_dict)

        table1= table[['MU','Current Credits', 'Percent Increase/Acre: LOW', 'Percent Increase/Acre: MEDIUM', 'Percent Increase/Acre: HIGH']].round(decimals=2)
        table1 = table1[table1["Percent Increase/Acre: HIGH"] > 0]
    ###Try bar chart
    ##transpose for bar chart

        table2 = table.copy()
        #table2.set_index("MU", inplace= True)
        table2 = table2[table2["Percent Increase/Acre: HIGH"] > table2['Percent Increase/Acre: HIGH'].median()]
        
        width = 0.5      # the width of the bars: can also be len(x) sequence
        colors = plt.cm.YlGnBu(np.linspace(0, 0.5, 3))

    ##GRAPH
        fig = plt.figure(figsize = (8,11))    
        ax1 = plt.subplot2grid((5,2), (0, 0), colspan=2, rowspan =2)

        ax1.bar(['Current Credits', 'Projected Creds', 'Low Effort', "Medium Effort", 'High Effort'], totals)
        ax1.set_title(t, fontsize = 18)
        ax1.set_xlabel('Management Regime \n ')
        ax1.set_ylabel('Total Number of Credits')

        #fig.tight_layout()
        #plt.figure()
        ##NARATIVE
        ax2 = plt.subplot2grid((5,2), (2, 0), colspan=2)
        ax2.axis('off')
        ax2.axis('tight')
        text= fig.text(.05,.5, graph1cap, family = 'serif', ha = 'left', wrap = True)

    #### TABLE
        # hide axes
        #fig.patch.set_visible(False)
        ax3 = plt.subplot2grid((5,2), (3, 0), rowspan=2)
        ax3.axis('off')
        ax3.axis('tight')

        the_table = ax3.table(cellText=subtable.values, colLabels=subtable.columns, loc='center', colColours= ['0.5', '0.4', '0.3', colors[2], colors[1], colors[0]])
        the_table.auto_set_font_size(False)
        the_table.set_fontsize(8)
        the_table.scale(1.8, 1.3)
        ax3.set_title('Map Unit and Percent Increase\nBased on Effort Level')

    #### comparison bar
        ax4 = plt.subplot2grid((5,2), (3, 1), rowspan =2)
        ax4.bar(table2['MU'].astype(str), table2['Percent Increase/Acre: HIGH'], width, label='High', color = colors[0])
        ax4.bar(table2['MU'].astype(str), table2['Percent Increase/Acre: MEDIUM'], width, label='Medium', color = colors[1])
        ax4.bar(table2['MU'].astype(str), table2['Percent Increase/Acre: LOW'], width, label='Low', color = colors[2])
        ax4.set_ylabel('Credits/Acre')
        ax4.set_xlabel('Map Units')
        ax4.set_title('Credits/Acre Created for Each Effort Level')
        ax4.legend()


        fig.tight_layout(pad = 2)

        save_name = os.path.join(workspace, '{}_summarypage1.pdf'.format(i))
        summary1 = fig.savefig(save_name, bbox_inches='tight', papertype = 'letter')
        
def update_pdf(workspace, current_data, proj_data, scenario_data):
    """adds charts to title page and saves to workspace"""
    fig = figure_one_ea(current_data, proj_data)
    chart_one = os.path.join(workspace, 'full_summary_chart.pdf')  
    fig.savefig(chart_one, bbox_inches='tight')  # may need a switch here for pro too
    
    fig2 = figure_two_ea(scenario_data, current_data, proj_data)
    chart_two = os.path.join(workspace, 'regime_summary_chart.pdf')
    fig2.savefig(chart_two, bbox_inches='tight')

    # MERGE AND SAVE
    title_page = os.path.join(workspace, 'Credit_Summary_Report.pdf')
    pdfDoc1 = PDFDocumentOpen(title_page)
    
    # Append summary page
    pdfDoc1.appendPages(chart_one)
    pdfDoc1.appendPages(chart_two)
    
    # Append map series
    map_series_loc = os.path.join(workspace, 'series.pdf')
    series = PDFDocumentOpen(map_series_loc)
    pdfDoc1.appendPages(map_series_loc)
    series.saveAndClose()
    
    # Save and close
    pdfDoc1.saveAndClose()
    
    # Delete intermediate reports
    try:
        Delete(map_series_loc)
        Delete(chart_one)
        Delete(chart_two)
    except:
        pass
    

if __name__ == '__main__':
    workspace = r'D:\ArcGIS\Nevada\Nevada Conservation Credit System\AdminMaterials\Test05182020'
    
    current_data = pd.read_csv(os.path.join(workspace, 'current_credits.csv'), index_col=0)
    proj_data = pd.read_csv(os.path.join(workspace, 'projected_credits.csv'), index_col=0)
    scenario_data = pd.read_csv(os.path.join(workspace, 'scenario_report.csv'), index_col=0)
    

    # fig = figure_one_ea(current_data, proj_data)
    # fig = figure_two_ea(scenario_data, current_data, proj_data)
    
    # plt.show(block=True)
    
    fig = figure_one_ea(current_data, proj_data)
    chart_one = os.path.join(workspace, 'full_summary_chart.pdf')  
    fig.savefig(chart_one, bbox_inches='tight')  # may need a switch here for pro too
    
    fig2 = figure_two_ea(scenario_data, current_data, proj_data)
    chart_two = os.path.join(workspace, 'regime_summary_chart.pdf')
    regminepdf = fig2.savefig(chart_two, bbox_inches='tight')

    ###MERGE AND SAVE
    title_page = os.path.join(workspace, 'Credit_Summary_Report.pdf')
    pdfDoc1 = PDFDocumentOpen(title_page)

    # pdfDoc1.appendPages(regminepdf)
    # pdfDoc1.appendPages(summary1)
    
    # Append summary page
    pdfDoc1.appendPages(chart_one)
    pdfDoc1.appendPages(chart_two)
    
    # pdfDoc1.appendPages(grid_pdf)
    
    # Append map series
    map_series_loc = os.path.join(workspace, 'series.pdf')
    series = PDFDocumentOpen(map_series_loc)
    pdfDoc1.appendPages(map_series_loc)

    # Save and close
    pdfDoc1.saveAndClose()
    
    # Delete interim pdfs
    
    
    # fig2 = figure_two()
    # save_name = os.path.join(workspace, 'managementregime_summary_chart.pdf')
    # regminepdf = fig.savefig(save_name, bbox_inches='tight')
    
    # fig3 = figure_three(workspace, regimes)
    # #saved in function
    
    
