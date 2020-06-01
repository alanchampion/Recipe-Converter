import json
import os, sys
import codecs

def read_in_file(file_name):
    title = ""
    text_content = ""
    labels = []

    with codecs.open(file_name, encoding='utf-8') as json_file:
        data = json.load(json_file)
        
        if 'labels' in data:
            for label in data['labels']:
                labels.append(label['name'])
            if not ('Drinks' in labels and data['color'] in ["BROWN", "RED"]):
                json_file.close()
                print(f"Removing file {file_name}")
                os.remove(file_name)
            else:
                json_file.close()
        else:
            json_file.close()
            print(f"Removing file {file_name}")
            os.remove(file_name)
    return None

json_files = [pos_json for pos_json in os.listdir(os.getcwd()) if pos_json.endswith('.json')]
for file_name in json_files:
    try:
        read_in_file(file_name)
    except SystemExit as e:
        print("Shutting down program")
        sys.exit()