import requests
import csv
import json
import os
import sys
from requests.auth import HTTPBasicAuth

def get_first_value_from_list(dictionary, key, default_value=None):
    return (dictionary.get(key) or [default_value])[0]

# Replace with your own endpoint, username, and password
endpoint = "https://lrsels.lip6.fr/data/xAPI"
username = "9fe9fa9a494f2b34b3cf355dcf20219d7be35b14"
password = "b547a66817be9c2dbad2a5f583e704397c9db809"

# Prepare headers for xAPI statement query
headers = {
    "X-Experience-API-Version": "1.0.3",
    "Content-Type": "application/json"
}

# The verbs you are querying for
verbs = [
    "http://adlnet.gov/expapi/verbs/launched",
    "http://adlnet.gov/expapi/verbs/completed",
    "http://adlnet.gov/expapi/verbs/exited"
]

# Récupérez le premier argument en ligne de commande comme nom de l'agent
if len(sys.argv) > 1:
    agent_name = sys.argv[1]
else:
    print("Please provide the agent name as the first argument.")
    sys.exit(1)

# The agent you are querying for
agent = {"account": {"homePage": "https://www.lip6.fr/mocah/", "name": agent_name}}

# Function to get statements for a verb
def get_statements_for_verb(verb, more_url=""):
    if more_url:
        # Si l'URL `more` est un chemin relatif, ajoutez-le à l'`endpoint`
        if more_url.startswith('/data/xAPI/statements'):
            more_url = "https://lrsels.lip6.fr" + more_url

        response = requests.get(more_url, auth=HTTPBasicAuth(username, password), headers=headers)
    else:
        params = {
            "agent": json.dumps(agent),
            "verb": verb,
            "limit": 100
        }
        response = requests.get(endpoint + "/statements", params=params, auth=HTTPBasicAuth(username, password), headers=headers)

    if response.status_code == 200:
        json_response = response.json()
        statements = json_response['statements']

        # Vérifiez si plus de données doivent être récupérées
        if 'more' in json_response and json_response['more']:
            more_url = json_response['more']
            statements += get_statements_for_verb(verb, more_url=more_url)
        return statements
    else:
        print(f"Failed to query statements for verb {verb}: ", response.text)
        return []

# Get statements for all verbs
all_statements = []
for verb in verbs:
    all_statements.extend(get_statements_for_verb(verb))

actor = all_statements[0].get('actor', {}).get('name', '')

# Chemin du fichier dans le répertoire 'Raw'
output_path = os.path.join(os.path.dirname(__file__), '..', 'Raw', str(actor) + '.csv')

# Write the statements to a CSV file
with open(output_path, 'w', newline='') as csvfile:
    fieldnames = ['actor', 'timestamp', 'verb', 'xml', 'scenario', 'level', 'success', 'score']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # Trier les statements par ordre chronologique décroissant selon timestamp
    sorted_statements = sorted(all_statements, key=lambda x: x.get('timestamp', ''), reverse=False)
    
    writer.writeheader()
    for statement in sorted_statements:
        writer.writerow({
            'actor': statement.get('actor', {}).get('name', ''),
            'timestamp': statement.get('timestamp', ''),
            'verb': statement.get('verb', {}).get('display', {}).get('en-US', ''),
            'xml' : get_first_value_from_list(statement.get('object', {}).get('definition', {}).get('extensions', {}), "https://spy.lip6.fr/xapi/extensions/value", ''),
            'scenario' : get_first_value_from_list(statement.get('object', {}).get('definition', {}).get('extensions', {}), "https://spy.lip6.fr/xapi/extensions/context", ''),
            'level' : get_first_value_from_list(statement.get('object', {}).get('definition', {}).get('extensions', {}), "https://w3id.org/xapi/seriousgames/extensions/progress", ''),
            'success' : statement.get('result', {}).get('success', ''),
            'score': get_first_value_from_list(statement.get('result', {}).get('extensions', {}), "https://spy.lip6.fr/xapi/extensions/score", '')
        })

#print("Statements have been written to " + str(actor) + ".csv")
