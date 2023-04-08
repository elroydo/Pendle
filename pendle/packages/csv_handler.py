import os
import csv
import datetime

class CSVHandler:
    def __init__(self, file_name='data', folder='data'):
        #Create data folder if it doesn't exist
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        now = datetime.datetime.now()
        timestamp = now.strftime("%H-%M-%S")
        self.file_path = os.path.join(folder, f'{file_name}_{timestamp}.csv') #Get full path
    
    def save_data(self, data):
        #Create data file if it doesn't exist
        if not os.path.isfile(self.file_path): #Check if file exists 
            with open(self.file_path, mode='a', newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(['timestamp', 'bpm', 'brpm', 'emotions', 'session']) #Write headers
                for metric in data:
                    writer.writerow(metric) #Write data to file
            print(f'Data written to {self.file_path}.')
        else:
            print(f'{self.file_path} already exists.')
            
    def get_data(self):
        data = []
        with open(self.file_path, mode='r') as csv_file:
            reader = csv.reader(csv_file)
            headers = next(reader)  # skip headers
            data = [[row[0], float(row[1]), float(row[2]), row[3], True if row[4].lower() == 'true' else False] for row in reader]
        return data