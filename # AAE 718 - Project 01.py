# AAE 718 - Project 01
# BEA Use Tables

import pandas as pd


def load_single_sheet(file_path, sheet_name):
    """Load a single sheet from the BEA Use Tables Excel file.
    Returns a long-format dataframe with columns: year, commodity, industry, value
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

    year = int(sheet_name)

    # Row 5 has industry codes, Row 6 has industry names
    # Commodity data starts at row 7, ends before row with code 'T005'
    # Industry data starts at col 2, ends before col with code 'T001'

    # Find commodity row range
    commodity_start = 7
    commodity_end = None
    for i in range(commodity_start, df.shape[0]):
        if str(df.iloc[i, 0]) == 'T005':
            commodity_end = i
            break

    # Find industry col range
    industry_start = 2
    industry_end = None
    for j in range(industry_start, df.shape[1]):
        if str(df.iloc[5, j]) == 'T001':
            industry_end = j
            break

    # Extract commodity codes (ensure string)
    commodity_codes = [str(df.iloc[i, 0]) for i in range(commodity_start, commodity_end)]

    # Extract industry codes (ensure string)
    industry_codes = [str(df.iloc[5, j]) for j in range(industry_start, industry_end)]

    # Build long-format data
    records = []
    for i, comm in enumerate(commodity_codes):
        for j, ind in enumerate(industry_codes):
            raw_val = df.iloc[commodity_start + i, industry_start + j]
            # Convert to numeric, treat "..." and NaN as 0
            val = pd.to_numeric(raw_val, errors='coerce')
            if pd.isna(val):
                val = 0.0
            records.append((year, comm, ind, val))

    return pd.DataFrame(records, columns=['year', 'commodity', 'industry', 'value'])


def load_descriptions(file_path):
    """Load NAICS code descriptions from the first sheet.
    Returns a dataframe with columns: naics_code, description
    """
    df = pd.read_excel(file_path, sheet_name=0, header=None)

    # Collect codes and descriptions from rows (commodities)
    codes = {}

    # Row commodities: rows 7 to before T005
    for i in range(7, df.shape[0]):
        code = str(df.iloc[i, 0])
        if code == 'T005':
            break
        name = str(df.iloc[i, 1])
        codes[code] = name

    # Column industries: cols 2 to before T001 (row 5 = code, row 6 = name)
    for j in range(2, df.shape[1]):
        code = str(df.iloc[5, j])
        if code == 'T001':
            break
        name = str(df.iloc[6, j])
        if code not in codes:
            codes[code] = name

    desc_df = pd.DataFrame(
        [(k, v) for k, v in codes.items()],
        columns=['naics_code', 'description']
    )

    return desc_df


def load_use_tables(file_path):
    """Load all years and return the two required dataframes.
    1. use_df: year, commodity, industry, value
    2. desc_df: naics_code, description
    """
    xls = pd.ExcelFile(file_path)

    all_years = []
    for sheet in xls.sheet_names:
        print(f"Loading {sheet}...")
        year_df = load_single_sheet(file_path, sheet)
        all_years.append(year_df)

    use_df = pd.concat(all_years, ignore_index=True)
    desc_df = load_descriptions(file_path)

    return use_df, desc_df