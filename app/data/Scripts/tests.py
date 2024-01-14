import pandas as pd
import os

def calculate_progression(student_ID):
    # Charger les informations des niveaux
    levels_info_path = '../Models/levelsInfo.csv'
    levels_info_df = pd.read_csv(levels_info_path)
    directory_path = '../Processed/' + student_ID + '_Processing.csv'

    # Initialiser le DataFrame pour stocker les résultats
    progression_df = pd.DataFrame(columns=['scenario', 'niveau', 'progression'])

    # Lecture du fichier CSV de l'élève
    student_df = pd.read_csv(directory_path)

    # Fusionner les données de l'élève avec les informations des niveaux
    merged_df = pd.merge(student_df, levels_info_df, left_on='xml', right_on='level')

    # Remplacer les valeurs NaN par 0 dans la colonne 'score'
    merged_df['score'] = merged_df['score'].fillna(0)

    # Calculer la progression pour chaque niveau
    for _, row in merged_df.iterrows():
        score = row['score']
        if score == row['2-stars'] - row['2-stars']:
            progression = 0
        elif score < row['2-stars']:
            progression = 33
        elif score < row['3-stars']:
            progression = 66
        else:
            progression = 100
        
        # Extraire le niveau en français
        level_fr = row['level_x'].split('[fr]')[1].split('[/fr]')[0]

        # Créer une nouvelle ligne à ajouter
        new_row = pd.DataFrame({'scenario': [row['scenario']],
                                'niveau': [level_fr],
                                'progression': [progression]})

        # Concaténer la nouvelle ligne au DataFrame
        progression_df = pd.concat([progression_df, new_row], ignore_index=True)
            
    return progression_df

df = calculate_progression("A5A6EC6D")
filtered_df = df[df['scenario'] == "infiltration"]
num_bars = filtered_df['niveau'].count()
print(num_bars)
progression_values = filtered_df['progression'].tolist()
print(progression_values)