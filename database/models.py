# for CreditCalculator class
import pandas as pd
import numpy as np
import os

# for CreditData class
from components import create_connection
from collections import OrderedDict

# TODO Add column names to each df

class CreditCalculator:    
    def __init__(self, calc_file):
        self.calc_file = calc_file
    
    @property    
    def map_units_df(self):
        # read in map units table
        map_units_df = pd.read_excel(
            self.calc_file, 
            '1.1 Enter Map Unit Data',
            skiprows=5, header=None,
            parse_cols="C:G,J:O,V")  # read TRUE/FALSE as bool (0) in indirect_benefits
        map_units_df = map_units_df[map_units_df.iloc[:,0].notnull()]
        return map_units_df
    
    @property
    def current_ls_df(self):
        # read in current local-scale values from map unit table
        current_ls_df = pd.read_excel(
            self.calc_file,
            '1.1 Enter Map Unit Data',
            skiprows=5, header=None,
            parse_cols="C,P:R"
        )
        return current_ls_df
    
    @property
    def projected_ls_df(self):
        # read in projected local-scale values from map unit table
        projected_ls_df = pd.read_excel(
            self.calc_file,
            '1.1 Enter Map Unit Data',
            skiprows=5, header=None,
            parse_cols="C,S:U"
        )
        return projected_ls_df
    
    @property
    def transects_data_df(self):
        # read in transects table
        transects_data_df = pd.read_excel(
            self.calc_file, 
            '1.1 Enter Map Unit Data',
            skiprows=5, header=None,
            parse_cols="C:K")
        transects_data_df = transects_data_df[transects_data_df.iloc[:,0].notnull()]
        return transects_data_df
    
    @property
    def mgmt_cats_df(self):
        # read in mgmt cats table
        mgmt_cats_df = pd.read_excel(
            self.calc_file, 
            '1.3 Enter Mgmt Cats Data',
            skiprows=5, header=None,
            parse_cols="C:E")
        mgmt_cats_df = mgmt_cats_df[mgmt_cats_df.iloc[:,0].notnull()]
        return mgmt_cats_df
    
    @property
    def wmz_df(self):
        # read in wmz table
        wmz_df = pd.read_excel(
            self.calc_file, 
            '1.3 Enter Mgmt Cats Data',
            skiprows=5, header=None,
            parse_cols="J:L")
        wmz_df = wmz_df[wmz_df.iloc[:,0].notnull()]
        return wmz_df
    
    @property
    def pmu_df(self):
        # read in pmu table
        pmu_df = pd.read_excel(
            self.calc_file, 
            '1.3 Enter Mgmt Cats Data',
            skiprows=5, header=None,
            parse_cols="Q:S")
        pmu_df = pmu_df[pmu_df.iloc[:,0].notnull()]
        return pmu_df
    
    @property
    def precip_df(self):
        # read in precip table
        precip_df = pd.read_excel(
            self.calc_file, 
            '1.3 Enter Mgmt Cats Data',
            skiprows=5, header=None,
            parse_cols="X:Z")
        precip_df = precip_df[precip_df.iloc[:,0].notnull()]
        return precip_df
    
    @property
    def desktop_results_df(self):
        # read in desktop results table
        desktop_results_df = pd.read_excel(
            self.calc_file, 
            '1.4 Review Desktop Results',
            skiprows=5, header=None,
            parse_cols="B:AC")
        desktop_results_df = desktop_results_df[desktop_results_df.iloc[:,0].notnull()]
        return desktop_results_df
    
    @property
    def field_sheets_df(self):
        # read in field sheets table (additional map unit info)
        field_sheets_df = pd.read_excel(
            self.calc_file, 
            '2.1 Track Field Sheets',
            skiprows=5, header=None,
            parse_cols="A:L")
        field_sheets_df = field_sheets_df[field_sheets_df[1].notnull()]
        return field_sheets_df
    
    @property
    def field_info_df(self):
        # read in field info table (additional transects info)
        field_info_df = pd.read_excel(
            self.calc_file, 
            '2.2 Enter Field Info',
            skiprows=5, header=None,
            parse_cols="B:V")
        field_info_df = field_info_df[field_info_df.iloc[:,0].notnull()]    
        # format date column
        field_info_df[8] = field_info_df[8].map(lambda x: x.strftime('%Y-%m-%d') 
                                                if pd.notnull(x) else np.nan)
        # format time columns
        field_info_df[10] = field_info_df[10].astype(str)
        field_info_df[11] = field_info_df[11].astype(str)
        return field_info_df
        
    @property
    def shrubs_df(self):
        # read in shrub data
        shrubs_df = pd.read_excel(
            self.calc_file, 
            '2.3 Enter Shrub Data',
            skiprows=5, header=None,
            parse_cols="C:H")
        shrubs_df = shrubs_df[shrubs_df.iloc[:,0].notnull()]
        return shrubs_df
        
    # @property
    def plot_df(self, plot_cols):
        # read in plot data        
        plot_df = pd.read_excel(
            self.calc_file, 
            '2.4 Enter Forbs & Grass Data',
            skiprows=5, header=None,
            parse_cols=plot_cols)
        plot_df = plot_df[plot_df.iloc[:,0].notnull()]
        return plot_df
        
    @property
    def forb_grass_df(self):
        # read in forbs and grasses data
        forb_grass_df = pd.read_excel(
            self.calc_file, 
            '2.4 Enter Forbs & Grass Data',
            skiprows=5, header=None,
            parse_cols="C:D, T:X")
        forb_grass_df = forb_grass_df[forb_grass_df.iloc[:,0].notnull()]
        return forb_grass_df
        
    @property
    def transects_review_df(self):
        # read in transects data table
        transects_review_df = pd.read_excel(
            self.calc_file, 
            '2.5 Review Transect Data',
            skiprows=5, header=None,
            parse_cols="B:O")
        transects_review_df = transects_review_df[transects_review_df.iloc[:,0].notnull()]
        return transects_review_df
    
    @property
    def site_scale_values_df(self):
        # read in attribute values from projected condition
        site_scale_values_df = pd.read_excel(
            self.calc_file, 
            '2.6 Enter Projected Condition',
            skiprows=5, header=None,
            parse_cols="B:K, N, R, V, Z, AD, AL, AY, BC, BI, BQ, BU, CH, CL")
        site_scale_values_df = site_scale_values_df[site_scale_values_df.iloc[:,0].notnull()]
        return site_scale_values_df
    
    @property
    def site_scale_scores_df(self):
        # read in attribute values from projected condition
        site_scale_scores_df = pd.read_excel(
            self.calc_file, 
            '2.6 Enter Projected Condition',
            skiprows=5, header=None,
            parse_cols=("B, L, P, T, X, AB, AF, AH, AJ, AN, AP, AS, AU, AW,"
                     "BA, BE, BG, BK, BM, BO, BS, BW, BY, CB, CD, CF,"
                     "CJ, CN, CP, CS, CU, CW")
            )
        site_scale_scores_df = site_scale_scores_df[site_scale_scores_df.iloc[:,0].notnull()]
        return site_scale_scores_df
    
    @property
    def projected_values_df(self):
        # read in projected attribute values
        # return a tidy dataset with only non-null inputs
        projected_values_df = pd.read_excel(
            self.calc_file, 
            '2.6 Enter Projected Condition',
            skiprows=5, header=None,
            parse_cols=("B, O, S, W, AA, AE, AM, AR, AZ, BD, BJ, BR, BV, CA, CI,"
                     "CM, CR")
            )
        projected_values_df = projected_values_df[projected_values_df.iloc[:,0].notnull()]
        
        col_names = [
            'map_unit_id',
            'b_sage_cover',
            'b_shrub_cover',   
            'b_grass_cover',
            'b_forb_cover',
            'b_forb_rich',
            'b_brotec_cover',
            'b_alt',
            's_forb_cover',
            's_forb_rich',
            's_grass_cover',
            's_brotec_cover',
            's_dist_sage',
            's_alt',
            'w_sage_height',
            'w_sage_cover',
            'w_alt'
        ]

        projected_values_df.columns=col_names
        projected_melt = pd.melt(projected_values_df, id_vars = 'map_unit_id', 
                                 var_name='hab_attr')
        projected_melt = projected_melt[projected_melt['value'].notnull()]
        return projected_melt

    @property
    def projected_scores_df(self):
        # read in projected attribute values
        projected_scores_df = pd.read_excel(
            self.calc_file, 
            '2.6 Enter Projected Condition',
            skiprows=5, header=None,
            parse_cols=("B, M, Q, U, Y, AC, AG, AI, AK, AO, AQ, AT, AV, AX,"
                     "BB, BF, BH, BL, BN, BP, BT, BX, BZ, CC, CE, CG,"
                     "CK, CO, CQ, CT, CV, CX")
            )
        projected_scores_df = projected_scores_df[projected_scores_df.iloc[:,0].notnull()]
        return projected_scores_df
    
    @property
    def baseline_rr_inputs_df(self):
        # read in baseline and rr inputs
        baseline_rr_inputs_df = pd.read_excel(
            self.calc_file,
            '3.1 Enter Baseline & Rsrv Acct',
            skiprows=5, header=None,
            parse_cols="B, F, H, K, S, T, U"
        )
        baseline_rr_inputs_df = baseline_rr_inputs_df[baseline_rr_inputs_df.iloc[:,0].notnull()]
        return baseline_rr_inputs_df
    
    @property
    def baseline_rr_df(self):
        # read in baseline
        baseline_rr_df = pd.read_excel(
            self.calc_file, 
            '3.1 Enter Baseline & Rsrv Acct',
            skiprows=5, header=None,
            parse_cols="B:E, G, I:J, L:R")
        baseline_rr_df = baseline_rr_df[baseline_rr_df.iloc[:,0].notnull()]
        return baseline_rr_df
    
    @property
    def baseline_credits_df(self):
        # read in credit amount
        baseline_credits_df = pd.read_excel(
            self.calc_file, 
            '3.2 Review Credit Amount',
            skiprows=5, header=None,
            parse_cols="B:O")
        baseline_credits_df = baseline_credits_df[baseline_credits_df.iloc[:,0].notnull()]
        return baseline_credits_df
    
    @property
    def current_credits_df(self):
        # read in credit amount
        current_credits_df = pd.read_excel(
            self.calc_file, 
            '3.2 Review Credit Amount',
            skiprows=5, header=None,
            parse_cols="B:C, P:AN")
        current_credits_df = current_credits_df[current_credits_df.iloc[:,0].notnull()]
        return current_credits_df
    
    @property
    def projected_credits_df(self):
        # read in credit amount
        projected_credits_df = pd.read_excel(
            self.calc_file, 
            '3.2 Review Credit Amount',
            skiprows=5, header=None,
            parse_cols="B:C, AO:BM")
        projected_credits_df = projected_credits_df[projected_credits_df.iloc[:,0].notnull()]
        return projected_credits_df


class PolicyTables:
    def __init__(self, version, folder):
        """provide HQT version as a float (e.g., 1.6) and path to
        policy tables folder"""
        self.version = version
        self.folder = folder
    
    pass

    
class CreditData:
    def __init__(self, db):
        self.db = db
        self.conn = create_connection(self.db)

    @property
    def desktop_results(self):
        desktop_results = pd.read_sql_query(
            """SELECT * FROM view_desktop_results""", self.conn
            )
        return desktop_results

    @property
    def site_scale_values(self):
        site_scale_values = pd.read_sql_query(
            """SELECT * FROM view_site_scale_values""", self.conn
            )
        return site_scale_values

    @property
    def current_ls(self):
        current_ls = pd.read_sql_query(
            """SELECT * FROM current_ls""", self.conn
        )
        return current_ls

    @property
    def projected_ls(self):
        projected_ls = pd.read_sql_query(
            """SELECT * FROM projected_ls""", self.conn
        )
        return projected_ls

    @property
    def scoring_curves(self):
        scoring_curves = pd.read_sql_query(
            """SELECT * FROM scoring_curves_v100""", self.conn,
            index_col= 'attr_value'
            )
        return scoring_curves

    @property
    def scoring_weights(self):
        scoring_weights = pd.read_sql_query(
            """SELECT * FROM scoring_weights""", self.conn,
            index_col=['season', 'attribute']
            )
        return scoring_weights

    @property
    def standard_baseline(self):
        standard_baseline = pd.read_sql_query(
            """SELECT * FROM view_baseline""", self.conn
            )
        return standard_baseline

    @property
    def multipliers_policy(self):
        multipliers_policy = pd.read_sql_query(
            """SELECT * FROM mgmt_multiplier""", self.conn
            )
        return multipliers_policy

    @property
    def standard_values(self):
        standard_values = pd.read_sql_query(
            """SELECT * FROM standard_values""", self.conn
            )
        return standard_values
    
    @property
    def reserve_account(self):
        reserve_account = pd.read_sql_query(
            """SELECT * FROM view_reserve_account""", self.conn
            )
        return reserve_account

    @property
    def projected_values(self):
        projected_values = pd.read_sql_query(
            """SELECT * FROM projected_values""", self.conn
            )
        return projected_values

    @property
    def curve_lookup(self):
        # Scoring curves base names
        curve_lookup = OrderedDict([
            ('b_sage_cover', 'sage_cover'),
            ('b_shrub_cover', 'shrub_cover'),
            ('b_forb_cover', 'forb_cover'),
            ('b_forb_rich', 'forb_rich'),
            ('s_forb_cover', 'forb_cover'),
            ('s_forb_rich', 'forb_rich'),
            ('s_grass_cover', 'grass_cover'),
            ('s_dist_sage', 'dist_sage'),
            ('w_sage_height', 'sage_height'),
            ('w_sage_cover', 'sage_cover'),
            ('brotec_cover', 'brotec_cover')
        ])
        return curve_lookup    
    