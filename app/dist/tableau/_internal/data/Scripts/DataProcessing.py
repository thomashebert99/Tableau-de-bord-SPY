import pandas as pd
from datetime import datetime
import os

def calculate_stars(score, two_stars_threshold, three_stars_threshold):
    if score >= three_stars_threshold:
        return 3
    elif score >= two_stars_threshold:
        return 2
    else:
        return 1

# Function to process the statements and update the model accordingly
def process_statements(statements_ID):
    model_path = os.path.join(os.path.dirname(__file__), '..', 'Models', 'modelProcessing.csv')
    levels_info_path = os.path.join(os.path.dirname(__file__), '..', 'Models', 'levelsInfo.csv')
    statements_path = os.path.join(os.path.dirname(__file__), '..', 'Raw', statements_ID + '.csv')
    output_path = os.path.join(os.path.dirname(__file__), '..', 'Processed', statements_ID + '_Processing.csv')

    # Read the CSV files
    statements_df = pd.read_csv(statements_path)
    model_df = pd.read_csv(model_path)
    levels_info_df = pd.read_csv(levels_info_path)
    
    # Convert timestamps to datetime for comparison
    statements_df['timestamp'] = pd.to_datetime(statements_df['timestamp'])
    
    # Sort the statements by timestamp to ensure chronological order
    statements_df.sort_values(by='timestamp', inplace=True)
    
    # Iterate through each launched event
    for index, launched_row in statements_df[statements_df['verb'] == 'launched'].iterrows():
        actor = launched_row['actor']
        scenario = launched_row['scenario']
        level = launched_row['level']
        xml_file = launched_row['xml']
        start_time = launched_row['timestamp']

        if level.startswith("niveau"):
            level_number = level[len("niveau"):]  # Extrait le numéro après "niveau"
            level = f"[fr]niveau{level_number}[/fr][en]level{level_number}[/en]"
        elif level.startswith("level"):
            level_number = level[len("level"):]  # Extrait le numéro après "level"
            level = f"[fr]niveau{level_number}[/fr][en]level{level_number}[/en]"
        else:
            level_number = level
        
        # Find the corresponding row in the model
        model_index = model_df[(model_df['scenario'] == scenario) & 
                               (model_df['level'] == level_number) & 
                               (model_df['xml'] == xml_file)].index
        
        # If there's a corresponding row in the model, proceed
        if not model_index.empty:
            model_index = model_index[0]
            
            # Find the next 'completed' or 'exited' event
            next_row = statements_df[(statements_df['actor'] == actor) & 
                                     (statements_df['timestamp'] > start_time) & 
                                     ((statements_df['verb'] == 'completed') | 
                                      (statements_df['verb'] == 'exited'))].head(1)
            
            if not next_row.empty:
                next_row = next_row.iloc[0]
                end_time = next_row['timestamp']
                time_spent = (end_time - start_time).total_seconds()
                
                if model_df.at[model_index, 'stars'] != 3:
                
                    # Update time spent in the model, treat NaN as 0
                    current_time = model_df.at[model_index, 'time']
                    model_df.at[model_index, 'time'] = time_spent if pd.isna(current_time) else current_time + time_spent
                    
                    # Update attempts, treat NaN as 0
                    current_attempts = model_df.at[model_index, 'attempts']
                    model_df.at[model_index, 'attempts'] = 1 if pd.isna(current_attempts) else current_attempts + 1
                    
                    # Update success and score if the verb is 'completed'
                    if next_row['verb'] == 'completed':
                        model_df.at[model_index, 'success'] = 1 if next_row['success'] else 0
                        
                        # For score, only update if it's greater than the current score or if the current score is NaN
                        current_score = model_df.at[model_index, 'score']
                        new_score = next_row['score'] if 'score' in next_row else None
                        if new_score is not None:
                            if pd.isna(current_score) or new_score > current_score:
                                model_df.at[model_index, 'score'] = new_score
                        
                        # Calculate stars based on score
                        level_info = levels_info_df[levels_info_df['level'] == xml_file].iloc[0]
                        stars = calculate_stars(next_row['score'], level_info['2-stars'], level_info['3-stars'])
                        
                        # Check if current stars value is NaN and update accordingly
                        current_stars = model_df.at[model_index, 'stars']
                        if pd.isna(current_stars):
                            model_df.at[model_index, 'stars'] = stars
                        else:
                            model_df.at[model_index, 'stars'] = max(current_stars, stars)
    
    # Write to the output file
    model_df.to_csv(output_path, index=False)


