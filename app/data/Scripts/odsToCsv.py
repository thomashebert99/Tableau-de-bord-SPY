import pandas as pd

# Remplacez 'path_to_ods_file.ods' par le chemin de votre fichier ODS
ods_file_path = 'modelProcessing.ods'

# Remplacez 'output_file.csv' par le chemin où vous voulez sauvegarder le fichier CSV
csv_file_path = 'modelProcessing.csv'

# Lire le fichier ODS
ods_data = pd.read_excel(ods_file_path, engine='odf')

# Enregistrer les données dans un fichier CSV
ods_data.to_csv(csv_file_path, index=False)
