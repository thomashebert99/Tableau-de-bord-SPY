import pandas as pd

def to_lowercase(data):
    if isinstance(data, str):
        return data.lower()
    return data

# Remplacez ceci par le chemin de votre fichier ODS
ods_file_path = 'model.ods'

# Charger le fichier ODS
ods_data = pd.read_excel(ods_file_path, engine='odf')

# Appliquer la transformation à toutes les cellules de texte dans chaque colonne
ods_data_transformed = ods_data.apply(lambda col: col.map(to_lowercase))

# Sauvegarder le résultat dans un nouveau fichier ODS
# Remplacez ceci par le chemin de votre nouveau fichier ODS
new_ods_file_path = 'modelProcessing.ods'
ods_data_transformed.to_excel(new_ods_file_path, engine='odf', index=False)
