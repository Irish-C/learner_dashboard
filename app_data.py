import pandas as pd
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
schools_df = pd.read_csv("schools.csv")

region_options = [{'label': r, 'value': r} for r in sorted(schools_df['Region'].dropna().unique())]
division_options = [{'label': d, 'value': d} for d in sorted(schools_df['Division'].dropna().unique())]
barangay_options = [{'label': b, 'value': b} for b in sorted(schools_df['Barangay'].dropna().unique())]
school_options = [{'label': name, 'value': sid} for sid, name in zip(schools_df['BEIS School ID'], schools_df['School Name'])]

grade_options = [{'label': f'Grade {g}', 'value': f'G{g}'} for g in range(1, 13)]
grade_options.insert(0, {'label': 'Kinder', 'value': 'K'})
gender_options = [{'label': 'Male', 'value': 'Male'}, {'label': 'Female', 'value': 'Female'}]
