import pandas as pd
import numpy as np
import re

dataset_path = 'data.csv'
data = pd.read_csv(dataset_path)

grade_columns = [col for col in data.columns if re.match(r'^(K|G1(?!\d)|G2|G3|G4|G5|G6|G7|G8|G9|G10|G11|G12|Elem NG|JHS NG)', col)]
data['Total Male'] = data[[col for col in grade_columns if 'Male' in col]].sum(axis=1)
data['Total Female'] = data[[col for col in grade_columns if 'Female' in col]].sum(axis=1)
data['Total Enrollment'] = data['Total Male'] + data['Total Female']

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


# Build optimized combined SHS dataframe with Region, Grade, Gender, Track, and School Year
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
                    if pd.notna(value) and value > 0:
                        shs_track_records.append({
                            'Region': row['Region'],
                            'School Year': row['School Year'],
                            'Gender': gender,
                            'Grade Level': grade,
                            'Track': strand,
                            'Total Enrollment': value
                        })

combined_shs_track_df = pd.DataFrame(shs_track_records)

# Manage Data Page
SCHOOLS_PATH = 'schools.csv'
ENROLLMENT_PATH = 'data_2023-2024.csv'

def load_schools():
    return pd.read_csv(SCHOOLS_PATH)

def load_enrollment_data():
    return pd.read_csv(ENROLLMENT_PATH)

def get_school_metadata(school_name):
    schools_df = load_schools()
    return schools_df[schools_df['School Name'] == school_name].iloc[0]

def sanitize_enrollment_data(df, row_index):
    # Format empty or 0 values in the enrollment columns as 'N/A'
    for col in df.columns[2:]:  # Skip 'School Year' and 'BEIS School ID'
        val = df.at[row_index, col]
        if pd.isna(val) or val == 0 or val == 0.0:
            df.at[row_index, col] = "N/A"
    return df

def save_enrollment_data(df):
    df.to_csv(ENROLLMENT_PATH, index=False)
