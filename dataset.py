import csv

def load_data(filename):
    data_dict = {}
    with open(filename, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            key = row['']
            data_dict[key] = row
    return data_dict

data = load_data("megaGymDataset.csv")
print(data) 
