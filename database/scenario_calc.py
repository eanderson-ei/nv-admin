import credit_calc as calc
from models import CreditData
import os
import pandas as pd


def apply_improvement(value, factor, lower_bound=None, upper_bound=None):
    '''helper function for applying improvement factor to dataframes'''
    improved = value * factor
    improved[improved.ge(upper_bound)] = upper_bound
    improved[improved.le(lower_bound)] = lower_bound
    return improved


def run_scenario(site_scale_values_indexed, improvements):
    '''
    returns dict of projected_values as tidy dataframes for each effort level.
    :param site_scale_values_indexed: site-scale values read from the database 
    (excludes seasonal duplication) where the index is 'map_unit_id'.
    :param improvements: a dictionary of dictionaries, specifying the factor to multiply
    each current value by, with a lower and upper bound as a tuple, for low, med, and 
    high efforts.
    '''
    # Set up empty dict for storing outcomes
    outcomes = {}

    projected = site_scale_values_indexed.drop(site_scale_values_indexed.columns, axis=1)

    for hab_attr in improvements.keys():
        filt = site_scale_values_indexed.columns.str.endswith(hab_attr)
        if filt.sum() > 0:
            df = site_scale_values_indexed.loc[:, filt].copy()
            for effort, level in improvements[hab_attr].items():
                result = df.apply(apply_improvement, factor=level[0], 
                                  lower_bound=level[1], upper_bound=level[2])
                result.columns = [hab_attr + '_' + effort]
                projected = projected.join(result)
    
    # melt each effort level and append to outcomes
    for effort in improvements[hab_attr].keys():
        filt = projected.columns.str.endswith(effort)
        df = projected.loc[:, filt].copy()
        # remove effort from column name
        df.columns = [col_name[0] for col_name in df.columns.str.split('_' + effort)]
        melted = pd.melt(df.reset_index(), 
                         id_vars = 'map_unit_id', 
                         var_name='hab_attr')
        outcomes[effort] = melted        
        
    return outcomes


def run_base_scenarios(site_scale_values_indexed):
    '''
    defines and runs base scenarios (brotec, forb_grass, shrub), returns nested dict of
    scenarios and levels of effort
    :param site_scale_values_indexed: site-scale values read from the database 
    (excludes seasonal duplication) where the index is 'map_unit_id'.
    '''
    scenarios = {}
    # Create brotec scenario
    improvements = {
        'brotec_cover': {'low': (0.5, 0, 1), 'med': (0.25, 0, 1), 'high': (0.1, 0, 1)}
    }
    brotec_scenario = run_scenario(site_scale_values_indexed, improvements)
    scenarios['brotec'] = brotec_scenario
    
    # Create forb and grass scenario
    improvements = {
        'forb_cover': {'low': (1.1, 0, 1), 'med': (1.25, 0, 1), 'high': (1.5, 0, 1)},
        'forb_rich': {'low': (1, 0, None), 'med': (2, 0, None), 'high': (3, 0, None)},
        'grass_cover': {'low': (1.1, 0, 1), 'med': (1.25, 0, 1), 'high': (1.5, 0, 1)}
    }
    forb_grass_scenario = run_scenario(site_scale_values_indexed, improvements)
    scenarios['forb_grass'] = forb_grass_scenario
    
    # Create shrub scenario
    improvements = {
        'sage_cover': {'low': (1.1, 0, 1), 'med': (1.2, 0, 1), 'high': (1.3, 0, 1)},
        'shrub_cover': {'low': (1.1, 0, 1), 'med': (1.2, 0, 1), 'high': (1.3, 0, 1)}
    }
    shrub_scenario = run_scenario(site_scale_values_indexed, improvements)
    scenarios['shrub'] = shrub_scenario
    
    return scenarios


def calc_scenario_credits(scenarios, project, current_facres):
    '''
    calculate functional acres report for each scenario and compares to current
    functional acres report to calculate credits.
    :param scenarios: nested dict of scenarios and levels of effort, generated by
    run_base_scenarios()
    :param project: an instance of the CreditData class.
    :param current_facres: the current_facres report to compare scenarios for the 
    purpose of calculating credits.
    '''
    desktop_results = project.desktop_results
    site_scale_values = project.site_scale_values
    projected_ls = project.projected_ls
    credit_reports = {}
    
    for scenario_name, scenario_results in scenarios.items():
        for effort, projected_values in scenario_results.items():
            # Project site-scale values
            projected_site_scale = calc.project_site_scale(projected_values, 
                                                           site_scale_values)
            
            # Score projected site-scale values
            projected_scores = calc.score_site_scale(project, projected_site_scale)
            
            # Create projected functional acre report
            projected_facres = calc.calc_facres(desktop_results, projected_scores, 
                                                projected_ls)
            
            # Calculate projected credits
            projected_credits = calc.calc_credits(project, desktop_results, current_facres, 
                                                  projected_facres)
            
            # Append scenario name and dataframe to credit_reports dictionary
            credit_reports[scenario_name + '_' + effort] = projected_credits
    
    return credit_reports


def calc_conifer_credits(project, current_site_scale, current_facres):
    '''
    calculates credits resulting from local-scale uplift only (excluding
    any site-scale uplift) to reflect uplift from conifer and anthro 
    removal.
    :param project: an instance of the CreditData class.
    :param current_site_scale: the scored current site scale dataframe
    :param current_facres: the current_facres report to compare conifer for the 
    purpose of calculating credits. 
    '''
    desktop_results = project.desktop_results
    projected_ls = project.projected_ls

    # Create current functional acre report
    conifer_facres = calc.calc_facres(desktop_results, current_site_scale, 
                                      projected_ls)
    
    # Caculate credits for uplift from conifer removal
    conifer_credits = calc.calc_credits(project, desktop_results, current_facres, 
                                        conifer_facres)
    
    return conifer_credits


def run_scenario_report(project, save_interims=False):
    '''
    returns dataframe with saleable credits per scenario. 
    :param project: an instance of the CreditData class.
    :param save_interims: if True, the full credit report for each scenario 
    and for the conifer scenario is saved as a csv.'''
    # read from database
    site_scale_values = project.site_scale_values
    current_ls = project.current_ls
    desktop_results = project.desktop_results
    
    # set index of site_scale values for use in run_scenario
    site_scale_values_indexed = site_scale_values.set_index('map_unit_id')
    
    # Get current facres report to streamline comparison with scenarios
    # Score current site-scale values
    current_site_scale = calc.score_site_scale(project, site_scale_values)
    
    # Create current functional acre report
    current_facres = calc.calc_facres(desktop_results, current_site_scale, 
                                      current_ls)
    
    # Run scenarios
    scenarios = run_base_scenarios(site_scale_values_indexed)
    
    # Calculate credits for each scenario 
    credit_reports = calc_scenario_credits(scenarios, project, current_facres)
    
    # Compile saleable_credits for each scenario into a single dataframe
    list_of_credit_reports = list(credit_reports.items())  # make list to maintain order
    first_scenario, first_scenario_report = list_of_credit_reports[0]
    scenario_report = first_scenario_report[['map_unit_id', 'map_unit_name', 
                                           'meadow', 'map_unit_area',
                                           'saleable_credits']].copy()
    scenario_report.rename(columns = {'saleable_credits': first_scenario}, inplace=True)
        
    for name, data in list_of_credit_reports[1:]:
        data.rename(columns = {'saleable_credits': name}, inplace=True)
        scenario_report = pd.merge(scenario_report, data[['map_unit_id', name]],
                                   how='outer', on='map_unit_id', 
                                   suffixes=(False, False))
    
    # Calculate credits from conifer alone    
    conifer_credits = calc_conifer_credits(project, current_site_scale, current_facres)
    
    # Append to scenario report
    conifer_report = conifer_credits[['map_unit_id', 'saleable_credits']].copy()
    conifer_report.rename(columns = {'saleable_credits': 'conifer'}, inplace=True)
    scenario_report = pd.merge(scenario_report, conifer_report, how='outer',
                               on='map_unit_id', suffixes=(False, False))
    
    if save_interims:
        # Save outputs
        for name, data in credit_reports.items():
            save_name = name + '.csv'
            calc.save_output(workspace, data, save_name)
            
        # Save outputs
        calc.save_output(workspace, conifer_credits, 'conifer_credits.csv')
    
    return scenario_report


def main():
    workspace = r'D:\ArcGIS\Nevada\Nevada Conservation Credit System\AdminMaterials\Test05182020'
    db = os.path.join(workspace, 'crawford.db')
    current_credits = pd.read_csv(os.path.join(workspace, 'current_credits.csv'), index_col=0)
    
    # Instantiate CreditData object
    C = CreditData(db=db)
    
    scenario_report = run_scenario_report(C, save_interims=False)
    
    # Save outputs
    calc.save_output(workspace, scenario_report, 'scenario_report.csv')
    
    # Close conn
    C.conn.close()


if __name__ == '__main__':
    main()