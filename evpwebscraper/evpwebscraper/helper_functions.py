from csv import DictReader, DictWriter

from . conf import *

def read_in_data(data_file_in):
    towns = []
    with open(data_file_in, 'r') as csvfile:
        reader = DictReader(csvfile)
        for row in reader:
            towns.append(row[HEADERS['town']])
    return towns

