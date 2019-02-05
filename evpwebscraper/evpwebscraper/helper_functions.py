from csv import DictReader, DictWriter

def read_in_data(data_file_in):
    towns = []
    with open(data_file_in, 'r') as csvfile:
        reader = DictReader(csvfile)
        for row in reader:
            towns.append(row)
    return towns

def write_out_data(data_file_out, headers, data):
    with open(data_file_out, 'w') as csvfile:
        writer = DictWriter(csvfile, fieldnames=headers)
        writer.writeheaders()
        for row in data:
            writer.writerow(row)

