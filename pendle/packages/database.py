import os
from datetime import datetime
from sqlalchemy import create_engine, Table, Column, Float, String, Boolean, MetaData, select

class PendleDatabase:
    # Initialize the database by creating a new SQLite engine and metadata object
    def __init__(self, db_name='pendb', folder='data'):
        if not os.path.exists(folder):
            os.makedirs(folder)
            
        now = datetime.now().strftime("%H-%M-%S")
        db_path = os.path.join(folder, f'{db_name}_{now}.db')
        self.engine = create_engine(f'sqlite:///{db_path}', echo=True)
        self.metadata = MetaData()
        
        # Define the table structure
        self.my_table = Table('user_data', self.metadata,
            Column('bpm', Float),
            Column('brpm', Float),
            Column('emotions', String),
            Column('session', Boolean),
        )
        
        # Create the table in the database
        self.metadata.create_all(self.engine)

    def add_data(self, data):
        # Convert the data into a list of dictionaries
        dict_data = []
        for row in data:
            dict_data.append({'bpm': row[0], 'brpm': row[1], 'emotions': row[2], 'session': row[3]})

        #Insert the data into the database
        with self.engine.connect() as conn:
            conn.execute(self.my_table.insert(), dict_data)
            conn.commit()  # Commit changes to the database
            
    # Retrieve all rows from the user_data table in the database
    def get_data(self):
        with self.engine.connect() as conn:
            stmt = select(self.my_table.c.bpm, self.my_table.c.brpm, self.my_table.c.emotions, self.my_table.c.session)
            results = conn.execute(stmt)
            return results.fetchall()