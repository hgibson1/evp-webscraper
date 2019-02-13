from csv import DictReader, DictWriter

def read_in_data(data_file_in):
    towns = []
    try:
        with open(data_file_in, 'r') as csvfile:
            reader = DictReader(csvfile)
            for row in reader:
                towns.append(row)
    except FileNotFoundError as e:
        print(str(e))
    return towns
