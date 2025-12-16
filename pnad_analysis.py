import pnadium
import pandas as pd
import numpy as np
import os

# --- 0. CONFIGURAÇÃO INICIAL (INGLÊS) ---

ANO = 2025
TRIMESTRE = 2
# Novo nome de arquivo para refletir a mudança de delimitador
NOME_ARQUIVO_CSV = f'PNAD_Dados_Tableau_Ready_COMMA_{ANO}T{TRIMESTRE}.csv' 

# Mapeamento de Colunas: PNAD (Original) -> Novo Nome (INGLÊS)
MAPA_COLUNAS_EN = {
    'UF': 'State_Code',
    'V1028': 'Weight_Person',
    'V2007': 'Gender',
    'V2009': 'Age',
    'VD3004': 'Education_Level',
    'VD4020': 'Effective_Income',
    'VD4001': 'Labor_Force_Status',
    'VD4002': 'Employment_Type',
    'VD4035': 'Weekly_Hours',
    'VD4008': 'Economic_Sector'
}
COLUNAS_PNAD_ORIGINAIS = list(MAPA_COLUNAS_EN.keys())


def aplicar_legendas_e_finalizar(df):
    """Aplica legendas em inglês e prepara o DataFrame para exportação BI (Tableau)."""
    print("Applying English labels and preparing for Tableau export...")
    
    # --- 1. State/UF (Unidade da Federação) ---
    mapa_uf = {
        11: 'Rondonia', 12: 'Acre', 13: 'Amazonas', 14: 'Roraima', 15: 'Para', 16: 'Amapa', 17: 'Tocantins',
        21: 'Maranhao', 22: 'Piaui', 23: 'Ceara', 24: 'Rio Grande do Norte', 25: 'Paraiba', 26: 'Pernambuco', 27: 'Alagoas', 28: 'Sergipe', 29: 'Bahia',
        31: 'Minas Gerais', 32: 'Espirito Santo', 33: 'Rio de Janeiro', 35: 'Sao Paulo',
        41: 'Parana', 42: 'Santa Catarina', 43: 'Rio Grande do Sul',
        50: 'Mato Grosso do Sul', 51: 'Mato Grosso', 52: 'Goias', 53: 'Distrito Federal'
    }
    df['State_Name'] = df['State_Code'].map(mapa_uf).fillna('Unknown')
    
    # --- 2. Gender (V2007) ---
    mapa_gender = {1: 'Male', 2: 'Female'}
    df['Gender'] = df['Gender'].map(mapa_gender)

    # --- 3. Labor Force Status (VD4001) ---
    mapa_status = {1: 'Employed', 2: 'Unemployed', 3: 'Out of Labor Force'}
    df['Labor_Force_Status'] = df['Labor_Force_Status'].map(mapa_status)

    # --- 4. Employment Type (VD4002) ---
    mapa_employment_type = {
        1: 'Employee with formal contract',
        2: 'Employee without formal contract',
        3: 'Military or statutory public servant',
        4: 'Employer',
        5: 'Self-employed',
        6: 'Unpaid worker',
        7: 'Domestic worker employer family member',
        8: 'Domestic worker'
    }
    df['Employment_Type'] = df['Employment_Type'].map(mapa_employment_type)

    # --- 5. Education Level (VD3004) ---
    mapa_education = {
        1: 'No schooling',
        2: 'Incomplete Elementary/High School',
        3: 'Complete High School/Incomplete College',
        4: 'Complete College/Higher'
    }
    df['Education_Level'] = df['Education_Level'].map(mapa_education)

    # --- 6. Economic Sector (VD4008) ---
    mapa_sector = {
        1: 'Agriculture, Livestock, Forestry, Fishing, and Aquaculture',
        2: 'Industry',
        3: 'Construction',
        4: 'Trade, Repair of motor vehicles and motorcycles',
        5: 'Transportation, storage and mail',
        6: 'Accommodation and food service',
        7: 'Information, communication, financial, real estate and professional activities',
        8: 'Public Administration, defense, social security, education, human health and social services',
        9: 'Domestic services',
        10: 'Other services'
    }
    df['Economic_Sector'] = df['Economic_Sector'].map(mapa_sector)

    # --- 7. Standardize Numeric Columns (Final Tableau Names) ---
    df = df.rename(columns={
        'Effective_Income': 'Monthly_Income',
        'Weekly_Hours': 'Weekly_Hours_Worked',
        'Weight_Person': 'Sampling_Weight' 
    })
    
    # Reorder columns (State Name primeiro)
    colunas_ordenadas = [
        'State_Name', 'State_Code', 'Gender', 'Age', 
        'Labor_Force_Status', 'Employment_Type', 'Economic_Sector', 
        'Education_Level', 'Weekly_Hours_Worked', 'Monthly_Income', 
        'Sampling_Weight'
    ]
    
    return df[colunas_ordenadas]


# --- ETAPA 1: Download/Load and Process Data ---
if not os.path.exists(NOME_ARQUIVO_CSV):
    print(f"1. File {NOME_ARQUIVO_CSV} not found. Downloading and processing PNAD data - {ANO}.{TRIMESTRE}...")
    
    try:
        dados_pnad = pnadium.trimestral.download(
            ano=ANO, 
            t=TRIMESTRE, 
            colunas=COLUNAS_PNAD_ORIGINAIS 
        )
    except Exception as e:
        print(f"ERROR downloading data with pnadium: {e}")
        exit()
    
    # 2. Rename variables (to English)
    df_analise = dados_pnad.rename(columns=MAPA_COLUNAS_EN).copy()
    
    # 3. Force numeric types 
    for col in MAPA_COLUNAS_EN.values():
        df_analise[col] = pd.to_numeric(df_analise[col], errors='coerce')
    
    # 4. Filter for valid data
    df_analise = df_analise.loc[
        (df_analise['Effective_Income'].notna()) &
        (df_analise['Weight_Person'].notna()) 
    ].copy()
    
    # 5. Apply English labels and finalize names for Tableau
    df_final = aplicar_legendas_e_finalizar(df_analise)
    
    # 6. Save the final file (PRONTO PARA TABLEAU)
    # MUDANÇA CRÍTICA: sep=',' para compatibilidade universal CSV/Tableau.
    df_final.to_csv(NOME_ARQUIVO_CSV, index=False, sep=',', encoding='utf-8', na_rep='')
    print(f"\nProcessing complete. New CSV file for Tableau saved to: {NOME_ARQUIVO_CSV}")
    print(f"Number of observations saved: {df_final.shape[0]}")

else:
    # Load previously cleaned and labeled data
    try:
        # Usamos sep=',' na leitura também
        df_final = pd.read_csv(NOME_ARQUIVO_CSV, sep=',', encoding='utf-8', keep_default_na=True, na_values=[''])
        
        if df_final.empty:
            print("CRITICAL ERROR: Loaded DataFrame is empty. Please DELETE the CSV and run again to force a fresh download.")
            exit()
        
        print(f"Clean and Tableau-ready data loaded from {NOME_ARQUIVO_CSV}. Rows: {df_final.shape[0]}")
        
    except Exception as e:
        print(f"CRITICAL ERROR loading the CSV: {e}. Please DELETE the CSV and run again.")
        exit()

# ----------------------------------------------------
# FINAL VISUALIZATION
# ----------------------------------------------------
print("\n--- Sample of the Final DataFrame (Tableau Ready) ---")
print(df_final.head()) 
print("\n--- Data Types ---")
print(df_final.dtypes)

print(f"\nO arquivo {NOME_ARQUIVO_CSV} está pronto. No Tableau, use vírgula (,) como delimitador de campo.")