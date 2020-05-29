import pandas as pd
import numpy as np
from math import floor
from models import CreditData
import os


# Constants
BREEDING_TRIGGER = 0.3


# Functions

def score_site_scale(project, site_scale_values):
    '''
    Returns dataframe with score of provided site_scale_values
    :param project: an instance of the CreditData class. Used to get
    scoring curves and scoring weights associated with the project.
    :param site_scale_values: the site_scale_values table to be
    scored.
    '''
    
    # read from database
    scoring_curves = project.scoring_curves
    curve_lookup = project.curve_lookup
    scoring_weights = project.scoring_weights

    # helper function to lookup score of any value against any scoring curve
    def score_attribute(hab_value, curve_name):
        """
        Looks up a score from the 'scoring_curves' dataframe for the measure of any 
        habitat attribute (e.g., 35 percent cover of forb_cover). N/A returns 0.
        :param hab_value: measure of the habitat attribute, percents as integers
        :param curve_name: name of the scoring curve to use (e.g., b_sage_cover).
        """
        if np.isnan(hab_value):
            return 0
        else:
            return scoring_curves.loc[int(floor(hab_value)), curve_name]
    

    # Create site scale score dataframe
    site_scale_scores = site_scale_values.loc[:, ['map_unit_id']].copy()
    
    # Score attributes
    # b_trigger is the sum of grass cover and sage cover > 30%, NA is interpretted as 0
    site_scale_scores['b_trigger'] = (
        site_scale_values.loc[:, 'shrub_cover'].fillna(0)
        + site_scale_values.loc[:, 'grass_cover'].fillna(0)
    ) > BREEDING_TRIGGER
    
    # b_sage_cover is the straight score
    score = 'b_sage_cover'
    value = curve_lookup[score]  # evaluates to value = sage_cover
    site_scale_scores[score] = (
        site_scale_values[value]
        .apply(lambda x: score_attribute(x*100, score))
    )
    
    # b_shrub_cover is the straight score
    score = 'b_shrub_cover'
    value = curve_lookup[score]
    site_scale_scores[score] = (
        site_scale_values[value]
        .apply(lambda x: score_attribute(x*100, score))
    )
    
    # b_forb_cover is either the meadow score (use mesic) or, 
    # if not meadow, the weighted average by precipitation zone, 
    # calc both and average
    # calculate for meadow first
    filt = site_scale_values['meadow']!='No Meadow'
    score = 'b_forb_cover'
    value = curve_lookup[score]
    score_appended = score + '_mesic'
    site_scale_scores.loc[filt, score] = (
        site_scale_values.loc[filt, value]
        .apply(lambda x: score_attribute(x*100, score_appended))
    )
    # calculated weighted average for arid and mesic 
    # (note filt is reversed)
    score = 'b_forb_cover'
    value = curve_lookup[score]
    score_arid = score + '_arid'
    score_mesic = score + '_mesic'
    site_scale_scores.loc[~filt, score] = (
        site_scale_values.loc[~filt, value]
        .apply(lambda x: score_attribute(x*100, score_arid))
        * site_scale_values.loc[~filt, 'arid']
        + site_scale_values.loc[~filt, value]
        .apply(lambda x: score_attribute(x*100, score_mesic))
        * site_scale_values.loc[~filt, 'mesic']
    )

    # b_forb_rich is either the meadow score (use mesic) or, if not 
    # meadow, the weighted average by precipitation zone, calc both 
    # and average. Do not multiply by 100.
    # calculate for meadow first
    filt = site_scale_values['meadow'] != 'No Meadow'
    score = 'b_forb_rich'
    value = curve_lookup[score]
    score_meadow = score + '_mesic'
    site_scale_scores.loc[filt, score] = (
        site_scale_values.loc[filt, value]
        .apply(lambda x: score_attribute(x, score_meadow))
    )
    # calculated weighted average for arid and mesic 
    # (note filt is reversed)
    score_arid = score + '_arid'
    score_mesic = score + '_mesic'
    site_scale_scores.loc[~filt, score] = (
        site_scale_values.loc[~filt, value]
        .apply(lambda x: score_attribute(x, score_arid))
        * site_scale_values.loc[~filt, 'arid']
        + site_scale_values.loc[~filt, value]
        .apply(lambda x: score_attribute(x, score_mesic))
        * site_scale_values.loc[~filt, 'mesic']
    )

    # s_forb_cover is either the meadow score (use meadow) or, if not 
    # meadow, the weighted average by precipitation zone, calc both 
    # and average
    # calculate for meadow first
    filt = site_scale_values['meadow'] != 'No Meadow'
    score = 's_forb_cover'
    value = curve_lookup[score]
    score_meadow = score + '_meadow'
    site_scale_scores.loc[filt, score] = (
        site_scale_values.loc[filt, value]
        .apply(lambda x: score_attribute(x*100, score_meadow))
    )
    # calculated weighted average for arid and mesic 
    # (note filt is reversed)
    score_arid = score + '_arid'
    score_mesic = score + '_mesic'
    site_scale_scores.loc[~filt, score] = (
        site_scale_values.loc[~filt, value]
        .apply(lambda x: score_attribute(x*100, score_arid))
        * site_scale_values.loc[~filt, 'arid']
        + site_scale_values.loc[~filt, value]
        .apply(lambda x: score_attribute(x*100, score_mesic))
        * site_scale_values.loc[~filt, 'mesic']
    )

    # s_forb_rich is either the meadow score (use mesic) or, if not 
    # meadow, the weighted average by precipitation zone, calc both 
    # and average
    # calculate for meadow first
    filt = site_scale_values['meadow'] != 'No Meadow'
    score = 's_forb_rich'
    value = curve_lookup[score]
    score_meadow = score + '_mesic'
    site_scale_scores.loc[filt, score] = (
        site_scale_values.loc[filt, value]
        .apply(lambda x: score_attribute(x, score_meadow))
    )
    # calculated weighted average for arid and mesic 
    # (note filt is reversed)
    score_arid = score + '_arid'
    score_mesic = score + '_mesic'
    site_scale_scores.loc[~filt, score] = (
        site_scale_values.loc[~filt, value]
        .apply(lambda x: score_attribute(x, score_arid))
        * site_scale_values.loc[~filt, 'arid']
        + site_scale_values.loc[~filt, value]
        .apply(lambda x: score_attribute(x, score_mesic))
        * site_scale_values.loc[~filt, 'mesic']
    )

    # s_grass_cover is either the meadow score (use meadow) or, 
    # if not meadow, the weighted average by precipitation zone, 
    # calc both and average
    filt = site_scale_values['meadow'] != 'No Meadow'
    score = 's_grass_cover'
    value = curve_lookup[score]
    score_meadow = score + '_meadow'
    site_scale_scores.loc[filt, score] = (
        site_scale_values.loc[filt, value]
        .apply(lambda x: score_attribute(x*100, score_meadow))
    )
    # calculated weighted average for arid and mesic 
    # (note filt is reversed)
    score_arid = score + '_arid'
    score_mesic = score + '_mesic'
    site_scale_scores.loc[~filt, score] = (
        site_scale_values.loc[~filt, value]
        .apply(lambda x: score_attribute(x*100, score_arid))
        * site_scale_values.loc[~filt, 'arid']
        + site_scale_values.loc[~filt, value]
        .apply(lambda x: score_attribute(x*100, score_mesic))
        * site_scale_values.loc[~filt, 'mesic']
    )

    # s_dist_sage is 1 if no_meadow or, if meadow, use altered or 
    # unaltered. 
    # Do not multiply by 100.
    filt = site_scale_values['meadow'] == 'No Meadow'
    score = 's_dist_sage'
    value = curve_lookup[score]
    score_meadow = score + '_meadow'
    site_scale_scores.loc[filt, score] = 1
    # use a weighted average for altered and unaltered, where weight is 
    # either 1 or 0 
    score_altered = score + '_altered'
    score_unaltered = score + '_unaltered'
    site_scale_scores.loc[~filt, score] = (
        site_scale_values.loc[~filt, value]
        .apply(lambda x: score_attribute(x, score_altered))
        * (site_scale_values.loc[~filt, 'meadow'] == 'Altered').astype(int)
        + site_scale_values.loc[~filt, value]
        .apply(lambda x: score_attribute(x, score_unaltered))
        * (site_scale_values.loc[~filt, 'meadow'] == 'Unaltered').astype(int)
    )
    
    # w_sage_height is either big or low (use sage_species column)
    score = 'w_sage_height'
    value = curve_lookup[score]
    filt = site_scale_values['sage_species'] == 'Big Sagebrush'
    score_curve = score + '_big'
    site_scale_scores.loc[filt, score] = (
        site_scale_values.loc[filt, value]
        .apply(lambda x: score_attribute(x, score_curve))
    )

    filt = site_scale_values['sage_species'] == 'Low or Black Sagebrush'
    score_curve = score + '_low'
    site_scale_scores.loc[filt, score] = (
        site_scale_values.loc[filt, value]
        .apply(lambda x: score_attribute(x, score_curve))
    )

    filt = site_scale_values['sage_species'] == 'None'
    site_scale_scores.loc[filt, score] = 0
    
    # w_sage_cover is either big or low (use sage_species column)
    score = 'w_sage_cover'
    value = curve_lookup[score]
    filt = site_scale_values['sage_species']=='Big Sagebrush'
    score_curve = score + '_big'
    site_scale_scores.loc[filt, score] = (
        site_scale_values.loc[filt, value]
        .apply(lambda x: score_attribute(x*100, score_curve))
    )

    filt = site_scale_values['sage_species']=='Low or Black Sagebrush'
    score_curve = score + '_low'
    site_scale_scores.loc[filt, score] = (
        site_scale_values.loc[filt, value]
        .apply(lambda x: score_attribute(x*100, score_curve))
    )

    filt = site_scale_values['sage_species']=='None'
    site_scale_scores.loc[filt, score] = 0
    
    # Score brotec
    score = 'brotec_cover'
    value = curve_lookup[score]
    site_scale_scores[score] = (
        site_scale_values[value]
        .apply(lambda x: score_attribute(x*100, score))
    )

    # helper function for returning attr_weight
    def get_attr_weight(season, hab_attr):
        return scoring_weights.loc[(season, hab_attr), 'score_weight']
    
    # helper function for returning func_weight
    def get_func_weight(season, hab_function):
        scoring_weights_ungroup = scoring_weights.reset_index()  # for pandas v0.16
        function_weights = (
            scoring_weights_ungroup.groupby(['season', 'hab_function']).sum()
        )
        return function_weights.loc[(season, hab_function), 'score_weight']
    
    # Cover score for breeding is the weighted sum of sage_cover and 
    # shrub_cover if the breeding trigger is True, else 0. Un-weight 
    # by weight of cover as habitat function for interpretability (100% is 
    # max score). Note grass cover is only used to establish breeding 
    # trigger, it is not a scored attribute.
    site_scale_scores['b_cover'] = (
        ((site_scale_scores['b_sage_cover'] 
        * get_attr_weight('breed', 'sage_cover')
        + site_scale_scores['b_shrub_cover'] 
        * get_attr_weight('breed', 'shrub_cover'))
        * site_scale_scores['b_trigger'].astype(int))
        / get_func_weight('breed', 'cover')
        )
    
    # Forage score for breeding is weighted sum of forb cover and forb 
    # richness. Un-weight by weight of forage as habitat function for 
    # nterpretability (100% is max score).
    site_scale_scores['b_forage'] = (
        (site_scale_scores['b_forb_cover'] 
            * get_attr_weight('breed', 'forb_cover')
        + site_scale_scores['b_forb_rich'] 
        * get_attr_weight('breed', 'forb_rich'))
        / get_func_weight('breed', 'forage')
        )
    
    # Forage score for summer is weighted sum of forb cover and forb 
    # richness. Un-weight by weight of forage as habitat function for 
    # interpretability (100% is max score).
    site_scale_scores['s_forage'] = (
        (site_scale_scores['s_forb_cover'] 
        * get_attr_weight('summer', 'forb_cover')
        + site_scale_scores['s_forb_rich'] 
        * get_attr_weight('summer', 'forb_rich'))
        / get_func_weight('summer', 'forage'))
    
    # Cover score for summer is same as grass_cover score. 
    site_scale_scores['s_cover'] = site_scale_scores['s_grass_cover']
    
    # Site-scale breeding is weighted sum of cover and forage multiplied  by 
    # brotec_cover score. If trigger is not met, 0. If indirect_benefit_area, 
    # use HSI. If conifer_phase == 'Phase III', then 0.
    # First calculate the weighted sum
    site_scale_scores['breed'] = (
        (site_scale_scores['b_cover'] 
            * get_func_weight('breed', 'cover')
        + site_scale_scores['b_forage'] 
        * get_func_weight('breed', 'forage'))
        * site_scale_scores['brotec_cover']
        )
    # Overwrite for map units that don't meet trigger
    filt = ~site_scale_scores['b_trigger']
    site_scale_scores.loc[filt, 'breed'] = 0
    # Overwrite HSI for indirect benefit map units
    filt = (
        site_scale_values['indirect_benefits_area']
        .astype('int').astype('bool')
    )
    site_scale_scores.loc[filt, 'breed'] = (
        site_scale_values.loc[filt, 'spring_hsi']
    )
    # Overwrite for map units that have phase 3 conifer
    filt = site_scale_values['conifer_phase'] == 'Phase III'
    site_scale_scores.loc[filt, 'breed'] = 0
    
    # Site-scale summer is weighted sum of forage and cover multiplied by 
    # brotec_cover score, multiplied by dist_sage score. If 
    # indirect_benefit_area, use HSI. If conifer_phase == 'Phase III', then 0.
    # First calculate the weighted sum
    site_scale_scores['summer'] = (
        (site_scale_scores['s_forage'] 
         * get_func_weight('summer', 'forage')
        + site_scale_scores['s_cover'] 
        * get_func_weight('summer', 'cover'))
        * site_scale_scores['brotec_cover']
        * site_scale_scores['s_dist_sage']
        )
    # Overwrite HSI for indirect benefit map units
    filt = (
        site_scale_values['indirect_benefits_area']
        .astype('int').astype('bool')
    )
    site_scale_scores.loc[filt, 'summer'] = (
        site_scale_values.loc[filt, 'summer_hsi']
    )
    # Overwrite for map units that have phase 3 conifer
    filt = site_scale_values['conifer_phase'] == 'Phase III'
    site_scale_scores.loc[filt, 'summer'] = 0
    
    # Site scale winter is the weighted sum of sage_height and sage_cover 
    # scores. No modifiers. If indirect_benefit_area, use HSI. If 
    # conifer_phase == 'Phase III', then 0.
    # First calculate the weighted sum
    site_scale_scores['winter'] = (
        site_scale_scores['w_sage_height'] 
        * get_attr_weight('winter', 'sage_height')
        + site_scale_scores['w_sage_cover'] 
        * get_attr_weight('winter', 'sage_cover'))
    # Overwrite HSI for indirect benefit map units
    filt = (
        site_scale_values['indirect_benefits_area']
        .astype('int').astype('bool')
    )
    site_scale_scores.loc[filt, 'winter'] = (
        site_scale_values.loc[filt, 'winter_hsi']
    )
    # Overwrite for map units that have phase 3 conifer
    filt = site_scale_values['conifer_phase'] == 'Phase III'
    site_scale_scores.loc[filt, 'winter'] = 0
    
    return site_scale_scores


def correct_baseline(standard_baseline, current_site_scale):
    '''Returns regional standard baseline or current site-scale if current is lower'''
    
    standard_baseline.set_index(['map_unit_id', 'season'], inplace=True)
    baseline_values = standard_baseline.unstack()
    baseline_values = baseline_values.reset_index(col_level=1, col_fill=None)
    baseline_values.columns = ['map_unit_id', 'breed', 'summer', 'winter']
    baseline_corrected = pd.merge(
        baseline_values, 
        current_site_scale[
            ['map_unit_id', 
             'breed', 
             'summer', 
             'winter']
            ], 
        on='map_unit_id', 
        suffixes=('_baseline', '_current')
    )
    
    for season in ['breed', 'summer', 'winter']:
        filt = (
            baseline_corrected[season + '_baseline'] 
            > baseline_corrected[season + '_current']
        )
        baseline_corrected.loc[filt, season + '_baseline'] = (
            baseline_corrected.loc[filt, season + '_current']
        )
    baseline_corrected.drop(
        ['breed_current', 'summer_current', 'winter_current'], 
        axis=1, 
        inplace=True
        )
    baseline_corrected.columns = ['map_unit_id', 'breed', 'summer', 'winter']

    return baseline_corrected

    # Plug this into calc_facres to get baseline facres


def calc_facres(desktop_results, site_scale_scores, local_scale):
    '''Returns f-acre report for any set of site_scale_scores'''
    
    # Subset desktop_results 
    facres_report = (
        desktop_results[
            ['map_unit_id', 
             'map_unit_name', 
             'meadow', 
             'map_unit_area']
            ]
        .copy()
    )
    
    # Join local_scale
    facres_report = pd.merge(
        facres_report,
        local_scale,
        how='left',
        on='map_unit_id'
    )
    
    # Join site_scale_scores
    facres_report = pd.merge(
        facres_report, 
        site_scale_scores[
            ['map_unit_id', 
             'breed',
             'summer',
             'winter']
            ], 
        how='left', 
        on='map_unit_id')

    # Calculate habitat function
    for season in ['breed', 'summer', 'winter']:
        facres_report[season + '_overall'] = (
            facres_report[season] * facres_report['ls_' + season]
        )
        
        # Calculate functional acres
        facres_report[season + '_facres'] = (
            facres_report[season +'_overall'] 
            * facres_report['map_unit_area']
        )
    
    # re-order columns
    facres_col_order = [
        'map_unit_id', 
        'map_unit_name', 
        'meadow', 
        'map_unit_area', 
        'breed',
        'ls_breed', 
        'breed_overall', 
        'breed_facres', 
        'summer',
        'ls_summer', 
        'summer_overall', 
        'summer_facres', 
        'winter',
        'ls_winter', 
        'winter_overall', 
        'winter_facres'
    ]
    
    facres_report = facres_report[facres_col_order]
    
    return facres_report


def calc_credits(project, desktop_results, pre_facre_report, post_facre_report):
    '''
    Returns credits as difference between pre_facre_report and post_facre_report.
    :param project: an instance of the CreditData class. Used to get reserve account,
    standard values and mulipliers policy data associated with the project.
    :param desktop_results: the desktop_results view from the project database
    :param *_facre_report: the pre or post f_acre report from calc_facres()
    '''
    
    # read from database
    reserve_account = project.reserve_account
    standard_values = project.standard_values
    multipliers_policy = project.multipliers_policy
    
    # merge pre and post reports on map_unit_id
    credit_compare = pd.merge(
        pre_facre_report, 
        post_facre_report, 
        on=['map_unit_id', 
            'map_unit_name', 
            'meadow', 
            'map_unit_area'], 
        suffixes=('_pre', '_post'))
    
    # calculate deltas per season
    for season in ['breed', 'summer', 'winter']:
        credit_compare[season + '_delta'] = (
            credit_compare[season + '_facres_post'] 
            - credit_compare[season + '_facres_pre']
        )
    
    # prepare mgmt multiplier dataframe
    multipliers_df = (
        desktop_results[
            ['map_unit_id', 
             'phma', 
             'ghma', 
             'ohma']
            ].copy()
    )
    
    # weight each mgmt category by its multiplier
    for mgmt_cat in ['PHMA', 'GHMA', 'OHMA']:
        col_name = mgmt_cat.lower()
        filt = multipliers_policy['mgmt_cat'] == mgmt_cat
        multipliers_df[col_name] = (
            multipliers_df[col_name] 
            * multipliers_policy.loc[filt, 'multiplier'].values
        )
    
    # calculate weighted average
    col_names = [mgmt_cat.lower() for mgmt_cat in ['PHMA', 'GHMA', 'OHMA']]
    multipliers_df['mgmt_multiplier'] = multipliers_df[col_names].sum(axis=1)
    
    # merge with facre deltas
    credit_compare = pd.merge(
        credit_compare, 
        multipliers_df[
            ['map_unit_id', 
             'mgmt_multiplier']
            ], 
        on='map_unit_id')
    
    # apply meadow multiplier
    standard_values.set_index('variable', inplace=True)
    meadow_multiplier = (
        standard_values.at['meadow_multiplier', 'standard_value']
    )
    credit_compare['meadow_multiplier'] = meadow_multiplier
    
    # overwrite meadow multiplier if not meadow
    filt = credit_compare['meadow'] == 'No Meadow'
    credit_compare.loc[filt, 'meadow_multiplier'] = 0
    
    # multiply difference from above by multipliers for each season
    credit_compare['breed_credits'] = (
        credit_compare['breed_delta'] 
        * credit_compare['mgmt_multiplier']
    )
    
    credit_compare['summer_credits'] = (
        credit_compare['summer_delta'] 
        * (credit_compare['mgmt_multiplier'] 
           + credit_compare['meadow_multiplier'])
    )
    
    credit_compare['winter_credits'] = (
        credit_compare['winter_delta'] 
        * credit_compare['mgmt_multiplier']
    )
    
    # identify maximum diff and save seasonal habitat type to new variable
    credit_columns = ['breed_credits', 'summer_credits', 'winter_credits']
    
    season_dict = {
        np.nan: 'None',
        'breed_credits': 'Breeding',
        'summer_credits': 'Late Brood-Rearing',
        'winter_credits': 'Winter'
    }
    
    credit_compare['habitat_type'] = (
        credit_compare.loc[:, credit_columns].idxmax(axis=1)
    )
    credit_compare['habitat_type'] = (
        credit_compare['habitat_type'].map(season_dict)
    )
    
    # Calculate current credits generated as maximum diff
    credit_compare['credits'] = (
        credit_compare.loc[:, credit_columns].max(axis=1)
    )
    
    # Overwrite map units with no credits to None
    filt = credit_compare['credits'] == 0
    credit_compare.loc[filt, 'habitat_type'] = 'None'
    
    # Get reserve account contribution
    credit_compare = pd.merge(
        credit_compare, 
        reserve_account[
            ['map_unit_id', 
             'total_contribution']
            ], 
        on='map_unit_id')
    
    credit_compare['reserve_credits'] = (
        credit_compare['credits'] 
        * credit_compare['total_contribution']
    )
    
    # Create site_scale_values table by substituting in projected values
    credit_compare['saleable_credits'] = (
        credit_compare['credits'] 
        - credit_compare['reserve_credits']
    )
    
    return credit_compare


def project_site_scale(projected_values, site_scale_values):
    '''
    Substitutes projected_values for site_scale_values. Projected_values 
    should be in tidy form with columns ['map_unit_id', 'hab_attr', and 
    'attr_value']
    '''
    
    # Pivot projected values
    projected_pivot = (
        projected_values
        .set_index(['map_unit_id', 'hab_attr'])
        .unstack()
        .reset_index(col_fill=None)
    )    
    col_names = [name for _, name in projected_pivot.columns]
    projected_pivot.columns = col_names
    
    # Eliminate seasonal duplication
    hab_attrs = [
        'sage_cover', 
        'sage_height', 
        'shrub_cover',
        'forb_cover', 
        'forb_rich', 
        'grass_cover', 
        'brotec_cover'
    ]
    
    projected_single = projected_pivot[['map_unit_id']].copy()
    
    # average any values that appear in multiple seasons (values should
    # be identical given one field assessment)
    for hab_attr in hab_attrs:
        filt = projected_pivot.columns.str.endswith(hab_attr)
        if filt.sum() > 0:  # one or more columns ends with hab_attr
            projected_single[hab_attr] = (
                projected_pivot.loc[:, filt].mean(axis=1)
            )
    
    # Substitute projected into current values
    suffixes = ('_preTEMP', '_postTEMP')
    projected_site_scale = pd.merge(
        site_scale_values, 
        projected_single, 
        on='map_unit_id', 
        suffixes=suffixes)
    
    for hab_attr in hab_attrs:
        if projected_site_scale.columns.str.startswith(hab_attr).sum() > 1:  # i.e., 2 columns end the same
            filt = projected_site_scale[hab_attr + suffixes[1]].notnull()
            projected_site_scale.loc[filt, hab_attr] = (
                projected_site_scale.loc[filt, hab_attr + suffixes[1]]
            )
            projected_site_scale.loc[~filt, hab_attr] = (
                projected_site_scale.loc[~filt, hab_attr + suffixes[0]]
            )
    
    drop_cols = (
        projected_site_scale.columns.str.endswith(suffixes[0]) | 
        projected_site_scale.columns.str.endswith(suffixes[1])
    )
    
    projected_site_scale = projected_site_scale.loc[:, ~drop_cols].copy()

    # re-order columns to be the same as the current site_scale_values
    projected_site_scale = projected_site_scale[site_scale_values.columns]

    return projected_site_scale


def run_calculator(project, projected_values_input=None):
    """
    returns current and projected credit dataframes
    :param project: an instance of the CreditData class.
    :param projected_values_input: optional table of 
    projected_values as csv. Projected_values should be in tidy form with 
    columns ['map_unit_id', 'hab_attr', and 'attr_value']
    """
    # read in projected_values csv if provided, or read from database
    if projected_values_input:
        projected_values = pd.read_csv(projected_values_input)
    else:
        projected_values = project.projected_values
    
    # read from database
    site_scale_values = project.site_scale_values
    current_ls = project.current_ls
    projected_ls = project.projected_ls
    desktop_results = project.desktop_results
    standard_baseline = project.standard_baseline
    
    # Score current site-scale values
    current_site_scale = score_site_scale(project, site_scale_values)
    
    # Create current functional acre report
    current_facres = calc_facres(desktop_results, current_site_scale, 
                                 current_ls)
    
    # Get baseline site scale scores
    baseline_corrected = correct_baseline(standard_baseline, 
                                          current_site_scale)
    
    # Create baseline funcional acre report
    baseline_facres = calc_facres(desktop_results, baseline_corrected, 
                                  current_ls)
    
    # Calculate current credits    
    current_credits = calc_credits(project, desktop_results,baseline_facres, 
                                   current_facres)
    
    # Project site-scale values
    projected_site_scale = project_site_scale(projected_values, 
                                              site_scale_values)
    
    # Score projected site-scale values
    projected_scores = score_site_scale(project, projected_site_scale)
    
    # Create projected functional acre report
    projected_facres = calc_facres(desktop_results, projected_scores, 
                                   projected_ls)
    
    # Calculate projected credits
    projected_credits = calc_credits(project, desktop_results, current_facres, 
                                     projected_facres)
    
    return current_credits, projected_credits


def save_output(workspace, output, file_name):
    save_name = os.path.join(workspace, file_name)
    output.to_csv(save_name)
        
    
def main():
    workspace = r'D:\ArcGIS\Nevada\Nevada Conservation Credit System\AdminMaterials\Test05182020'
    db = os.path.join(workspace, 'crawford.db')
    
    # Instantiate CreditData object
    C = CreditData(db=db)
                   
    # run calculator
    current_credits, projected_credits = run_calculator(
        project=C,
        projected_values_input=None
        )
    
    # save outputs
    save_output(workspace, current_credits, 'current_credits.csv')
    save_output(workspace, projected_credits, 'projected_credits.csv')
    
    # Close conn
    C.conn.close()


if __name__ == '__main__':
    main()
    