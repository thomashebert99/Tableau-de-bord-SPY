import pandas as pd
import os

def analyze_student_data():
    scenario_completion = {}
    directory_path = 'data/Processed/'

    # Parcourir tous les fichiers CSV dans le répertoire
    for file in os.listdir(directory_path):
        if file.endswith('.csv'):
            file_path = os.path.join(directory_path, file)
            df = pd.read_csv(file_path)

            # Remplacer les valeurs NaN par 0 dans la colonne 'success'
            df['success'] = df['success'].fillna(0)

            # Grouper par scénario et vérifier si chaque scénario est terminé
            for scenario, group in df.groupby('scenario'):
                if scenario not in scenario_completion:
                    scenario_completion[scenario] = {'completed': 0, 'not_completed': 0}

                # Un scénario est terminé si tous les niveaux ont success == 1
                if group['success'].all():
                    scenario_completion[scenario]['completed'] += 1
                else:
                    scenario_completion[scenario]['not_completed'] += 1

    # Nombre total d'élèves (nombre total de fichiers CSV)
    total_students = len([file for file in os.listdir(directory_path) if file.endswith('.csv')])

    # Créer le DataFrame final
    scenarios = []
    completed = []
    not_completed = []

    for scenario, counts in scenario_completion.items():
        scenarios.append(scenario)
        completed.append(counts['completed'])
        not_completed.append(total_students - counts['completed'])

    return pd.DataFrame({
        "scenario": scenarios,
        "a terminé": completed,
        "n'a pas terminé": not_completed
    })

def calculate_competence_scores():
    # Charger les informations des niveaux
    levels_info_path = 'data/Models/levelsInfo.csv'
    levels_info_df = pd.read_csv(levels_info_path)
    directory_path = 'data/Processed/'
    
    # Préparer un DataFrame pour stocker les scores cumulatifs
    scores_df = pd.DataFrame()

    # Lister tous les fichiers des élèves
    student_files = [f for f in os.listdir(directory_path) if f.endswith('.csv')]

    for student_file in student_files:
        student_df = pd.read_csv(os.path.join(directory_path, student_file))
        
        # Fusionner les informations des niveaux avec les scores des élèves
        merged_df = pd.merge(student_df, levels_info_df, left_on='xml', right_on='level')

        # Remplacer les valeurs NaN par 0 dans la colonne 'score'
        merged_df['score'] = merged_df['score'].fillna(0)
        
        # Itérer sur chaque niveau pour calculer les scores
        for index, row in merged_df.iterrows():
            scenario = row['scenario']
            score = row['score']
            condition_present = row['conditions']
            loop_present = row['loops']
            condition_score = 0
            loop_score = 0
            
            # Vérifier la présence des compétences et calculer les scores
            if condition_present or loop_present:
                if score == row['2-stars'] - row['2-stars']:
                    score_value = 0
                elif score < row['2-stars']:
                    score_value = 0.33
                elif score < row['3-stars']:
                    score_value = 0.66
                else:
                    score_value = 1
                
                if condition_present:
                    condition_score = score_value
                if loop_present:
                    loop_score = score_value
            
            # Ajouter ou mettre à jour les scores dans le DataFrame
            if scenario not in scores_df.index:
                scores_df.loc[scenario, 'conditions'] = condition_score
                scores_df.loc[scenario, 'conditions max'] = condition_present
                scores_df.loc[scenario, 'boucles'] = loop_score
                scores_df.loc[scenario, 'boucles max'] = loop_present
            else:
                scores_df.loc[scenario, 'conditions'] += condition_score
                scores_df.loc[scenario, 'conditions max'] += condition_present
                scores_df.loc[scenario, 'boucles'] += loop_score
                scores_df.loc[scenario, 'boucles max'] += loop_present
    
    # Transformer le dictionnaire en DataFrame
    scores_df = scores_df.reset_index().rename(columns={'index': 'scenario'})

    return scores_df

def calculate_competence_scores_perso(student_ID):
    # Charger les informations des niveaux
    levels_info_path = 'data/Models/levelsInfo.csv'
    levels_info_df = pd.read_csv(levels_info_path)
    directory_path = 'data/Processed/' + student_ID + '_Processing.csv'
    
    # Préparer un DataFrame pour stocker les scores cumulatifs
    scores_df = pd.DataFrame()

    student_df = pd.read_csv(directory_path)
    
    # Fusionner les informations des niveaux avec les scores des élèves
    merged_df = pd.merge(student_df, levels_info_df, left_on='xml', right_on='level')

    # Remplacer les valeurs NaN par 0 dans la colonne 'score'
    merged_df['score'] = merged_df['score'].fillna(0)
    
    # Itérer sur chaque niveau pour calculer les scores
    for index, row in merged_df.iterrows():
        scenario = row['scenario']
        score = row['score']
        condition_present = row['conditions']
        loop_present = row['loops']
        condition_score = 0
        loop_score = 0
        
        # Vérifier la présence des compétences et calculer les scores
        if condition_present or loop_present:
            if score == row['2-stars'] - row['2-stars']:
                    score_value = 0
            elif score < row['2-stars']:
                score_value = 0.33
            elif score < row['3-stars']:
                score_value = 0.66
            else:
                score_value = 1
            
            if condition_present:
                condition_score = score_value
            if loop_present:
                loop_score = score_value
        
        # Ajouter ou mettre à jour les scores dans le DataFrame
        if scenario not in scores_df.index:
            scores_df.loc[scenario, 'conditions'] = condition_score
            scores_df.loc[scenario, 'conditions max'] = condition_present
            scores_df.loc[scenario, 'boucles'] = loop_score
            scores_df.loc[scenario, 'boucles max'] = loop_present
        else:
            scores_df.loc[scenario, 'conditions'] += condition_score
            scores_df.loc[scenario, 'conditions max'] += condition_present
            scores_df.loc[scenario, 'boucles'] += loop_score
            scores_df.loc[scenario, 'boucles max'] += loop_present

    # Transformer le dictionnaire en DataFrame
    scores_df = scores_df.reset_index().rename(columns={'index': 'scenario'})

    return scores_df

def calculate_progression(student_ID):
    # Charger les informations des niveaux
    levels_info_path = 'data/Models/levelsInfo.csv'
    #levels_info_path = '../Models/levelsInfo.csv'
    levels_info_df = pd.read_csv(levels_info_path)
    directory_path = 'data/Processed/' + student_ID + '_Processing.csv'
    #directory_path = '../Processed/' + student_ID + '_Processing.csv'

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

#df = calculate_progression("A5A6EC6D")
#print(df)

