
import pandas as pd
import numpy as np
import re
import os

SCHOOLS_PATH = 'data_files/schools.csv'

correct_region_order = [
    'CAR', 'NCR', 'Region I', 'Region II', 'Region III', 'Region IV-A',
    'MIMAROPA', 'Region V', 'Region VI', 'Region VII', 'Region VIII',
    'Region IX', 'Region X', 'Region XI', 'Region XII', 'CARAGA', 'BARMM'
]

def load_data_for_year(school_year):
    path = f"data_files/data_{school_year}.csv"
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset for year {school_year} not found at {path}")

    data = pd.read_csv(path)

    # Merge with schools.csv
    schools_df = pd.read_csv(SCHOOLS_PATH)
    data = data.merge(schools_df, on='BEIS School ID', how='left')

    # Extract grade columns
    grade_columns = [col for col in data.columns if re.match(r'^(K|G1(?!\d)|G2|G3|G4|G5|G6|G7|G8|G9|G10|G11|G12|Elem NG|JHS NG)', col)]

    data['Total Male'] = data[[col for col in grade_columns if 'Male' in col]].replace("N/A", 0).apply(pd.to_numeric, errors='coerce').sum(axis=1)
    data['Total Female'] = data[[col for col in grade_columns if 'Female' in col]].replace("N/A", 0).apply(pd.to_numeric, errors='coerce').sum(axis=1)
    data['Total Enrollment'] = data['Total Male'] + data['Total Female']

    # Build grade options
    grade_keys = sorted(set(re.match(r'^(K|G\d{1,2}|Elem NG|JHS NG)', col).group(1) for col in grade_columns if re.match(r'^(K|G\d{1,2}|Elem NG|JHS NG)', col)))
    grade_sort_order = {'K': 0, 'G1': 1, 'G2': 2, 'G3': 3, 'G4': 4, 'G5': 5, 'G6': 6, 'Elem NG': 7,
                        'G7': 8, 'G8': 9, 'G9': 10, 'G10': 11, 'JHS NG': 12, 'G11': 13, 'G12': 14}
    grade_keys.sort(key=lambda g: grade_sort_order.get(g, 100))

    grade_options = [{'label': 'Kinder', 'value': 'K'}] +         [{'label': f'Grade {g[1:]}', 'value': g} if g.startswith('G') else {'label': g, 'value': g} for g in grade_keys if g != 'K']

    region_options = [{'label': r, 'value': r} for r in correct_region_order if r in data['Region'].unique()]
    return data, grade_columns, grade_options, region_options

def load_schools():
    return pd.read_csv(SCHOOLS_PATH)

def get_school_metadata(school_name):
    schools_df = load_schools()
    return schools_df[schools_df['School Name'] == school_name].iloc[0]

def sanitize_enrollment_data(df, row_index):
    for col in df.columns[2:]:
        val = df.at[row_index, col]
        if pd.isna(val) or val == 0 or val == 0.0:
            df.at[row_index, col] = "N/A"
    return df

def build_combined_shs_track_df(data):
    shs_track_records = []

    strands = ['ABM', 'HUMSS', 'STEM', 'GAS', 'PBM', 'TVL', 'SPORTS', 'ARTS & DESIGN']
    grades = ['G11', 'G12']
    genders = ['Male', 'Female']

    for _, row in data.iterrows():
        for grade in grades:
            for strand in strands:
                for gender in genders:
                    if strand in ['TVL', 'SPORTS', 'ARTS & DESIGN']:
                        col_name = f"{grade} {strand.split()[0]} {gender}"
                    else:
                        col_name = f"{grade} ACAD - {strand} {gender}"
                    if col_name in data.columns:
                        value = row[col_name]
                        if pd.notna(value) and value != "N/A" and float(value) > 0:
                            shs_track_records.append({
                                'Region': row['Region'],
                                'School Year': row['School Year'],
                                'Gender': gender,
                                'Grade Level': grade,
                                'Track': strand,
                                'Total Enrollment': float(value)
                            })

    return pd.DataFrame(shs_track_records)
