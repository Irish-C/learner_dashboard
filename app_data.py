import pandas as pd
import re

dataset_path = 'data.csv'
data = pd.read_csv(dataset_path)

grade_columns = [col for col in data.columns if re.match(r'^(K|G\d{1,2}|Elem NG|JHS NG)', col)]
data['Total Male'] = data[[col for col in grade_columns if 'Male' in col]].sum(axis=1)
data['Total Female'] = data[[col for col in grade_columns if 'Female' in col]].sum(axis=1)
data['Total Enrollment'] = data['Total Male'] + data['Total Female']
data['School Year'] = '2024-2025'

# Dropdown prep
grade_keys = sorted(set(re.match(r'^(K|G\d{1,2}|Elem NG|JHS NG)', col).group(1) for col in grade_columns))
grade_sort_order = {'K': 0, 'G1': 1, 'G2': 2, 'G3': 3, 'G4': 4, 'G5': 5, 'G6': 6, 'Elem NG': 7,
                    'G7': 8, 'G8': 9, 'G9': 10, 'G10': 11, 'JHS NG': 12, 'G11': 13, 'G12': 14}
grade_keys.sort(key=lambda g: grade_sort_order.get(g, 100))

grade_options = [{'label': 'Kinder', 'value': 'K'}] + \
    [{'label': f'Grade {g[1:]}', 'value': g} if g.startswith('G') else {'label': g, 'value': g}
     for g in grade_keys if g != 'K']

correct_region_order = [
    'CAR', 'NCR', 'Region I', 'Region II', 'Region III', 'Region IV-A',
    'MIMAROPA', 'Region V', 'Region VI', 'Region VII', 'Region VIII',
    'Region IX', 'Region X', 'Region XI', 'Region XII', 'CARAGA', 'BARMM'
]

region_options = [{'label': r, 'value': r} for r in correct_region_order if r in data['Region'].unique()]
school_dropdown_options = [{'label': f"{row['BEIS School ID']} - {row['School Name']}", 'value': row['BEIS School ID']} for _, row in data.iterrows()]

# Grade Columns for filtering
grade_columns = [col for col in data.columns if re.match(r'^(K|G\d{1,2}|Elem NG|JHS NG)', col)]

# SHS Track Enrollment
def prepare_shs_totals(level_prefix):
    return {
        'ABM': data[[f"{level_prefix} ACAD - ABM Male", f"{level_prefix} ACAD - ABM Female"]].sum().sum(),
        'HUMSS': data[[f"{level_prefix} ACAD - HUMSS Male", f"{level_prefix} ACAD - HUMSS Female"]].sum().sum(),
        'STEM': data[[f"{level_prefix} ACAD STEM Male", f"{level_prefix} ACAD STEM Female"]].sum().sum(),
        'GAS': data[[f"{level_prefix} ACAD GAS Male", f"{level_prefix} ACAD GAS Female"]].sum().sum(),
        'PBM': data[[f"{level_prefix} ACAD PBM Male", f"{level_prefix} ACAD PBM Female"]].sum().sum(),
        'TVL': data[[f"{level_prefix} TVL Male", f"{level_prefix} TVL Female"]].sum().sum(),
        'SPORTS': data[[f"{level_prefix} SPORTS Male", f"{level_prefix} SPORTS Female"]].sum().sum(),
        'ARTS & DESIGN': data[[f"{level_prefix} ARTS Male", f"{level_prefix} ARTS Female"]].sum().sum()
    }

import pandas as pd

shs_track_df_g11 = pd.DataFrame(list(prepare_shs_totals("G11").items()), columns=['Track', 'Total Enrollment'])
shs_track_df_g11['Grade Level'] = 'G11'

shs_track_df_g12 = pd.DataFrame(list(prepare_shs_totals("G12").items()), columns=['Track', 'Total Enrollment'])
shs_track_df_g12['Grade Level'] = 'G12'

combined_shs_track_df = pd.concat([shs_track_df_g11, shs_track_df_g12])
