import os
import sqlite3
from settings import *


class DataManagement:
    def __init__(self):
        self.db_file = DATABASE_FILE

        # Check if database file exists
        if not os.path.exists(self.db_file):
            print(f"Database file not found: {self.db_file}")
        else:
            try:
                # Establish a connection to the database
                self.db_connection = sqlite3.connect(self.db_file)
                self.cursor =   self.db_connection.cursor()
                print("Database connected successfully!")

            except sqlite3.OperationalError as e:
                print(f"Error connecting to the database: {e}")
    
    def close(self):
        if self.db_connection:
            self.db_connection.close()
    
    def __del__(self):
        self.close()


'''for fetching save states'''
class LoadSaveState(DataManagement):
    def __init__(self):
        super().__init__()
    
    def fetch_all_save_state(self):
        try:
            self.cursor.execute(f"SELECT * FROM save_data")
            result = self.cursor.fetchall()
            if result:
                return result # Saved data: [[data_1], [data_2], ...]
            else:
                return None
        except sqlite3.OperationalError as e:
            print(f"Database error: {e}")
            return

    def fetch_character_stats(self, save_data_id:int):
        try:
            self.cursor.execute(f"SELECT * FROM character_stats WHERE  save_data_id = ?", (save_data_id,))
            result = self.cursor.fetchall()
            if result:
                return result # Retrieved character stats data: [[data_1], [data_2], ...]
            else:
                return None
        except sqlite3.OperationalError as e:
            print(f"Database error: {e}")
            return

    def fetch_character_inventory(self, save_data_id:int):
        try:
            self.cursor.execute(f"SELECT * FROM character_inventory WHERE  save_data_id = ?", (save_data_id,))
            result = self.cursor.fetchall()
            if result:
                return result #Retrieved character inventory data: [[save_data_1], [save_data_2], ...]
            else:
                return None
        except sqlite3.OperationalError as e:
            print(f"Database error: {e}")
            return


'''adding new save state'''
class AddSaveState(DataManagement):
    def __init__(self):
        super().__init__()
    
    def add_save_state(self, 
                       save_title:str, 
                       character_class:str, 
                       character_exp:int, 
                       character_level:int, 
                       character_wave:int, 
                       character_weapons:str, 
                       character_armors:str, 
                       character_accessories:str, 
                       character_consumables:str) -> bool:
        try:
            # Insert into parent table (save_data)
            query_save_data = "INSERT INTO save_data (save_data_title) VALUES (?);"
            self.cursor.execute(query_save_data, (save_title,))
            
            # Get the auto-generated save_data_id
            save_data_id = self.cursor.lastrowid
            
            # Insert into character_stats
            query_stats = """INSERT INTO character_stats 
                            (save_data_id, character_class, character_exp, 
                            character_level, character_wave) 
                            VALUES (?, ?, ?, ?, ?);"""
            self.cursor.execute(query_stats, (save_data_id, character_class, character_exp,
                                            character_level, character_wave))
            
            # Insert into character_inventory
            query_inventory = """INSERT INTO character_inventory
                                (save_data_id, character_weapons, character_armors, 
                                character_accessories, character_consumables)
                                VALUES (?, ?, ?, ?, ?);"""
            self.cursor.execute(query_inventory, (save_data_id, character_weapons,
                                                character_armors, character_accessories,
                                                character_consumables))
            
            self.db_connection.commit()
            return True
        
        except sqlite3.Error as e:  
            print(f"Database error: {e}")
            self.db_connection.rollback() 
            return False


'''for updating/changing save data'''
class UpdateSaveData(DataManagement):
    def __init__(self):
        super().__init__()
    
    """Optional: Rename a game saved state"""
    def update_save_state(self,save_data_id:int, new_save_title:str) -> bool:
        try:
            sql = """UPDATE save_data 
                    SET save_data_title = ?
                    WHERE save_data_id = ?"""
            self.cursor.execute(sql, (new_save_title, save_data_id))
            self.db_connection.commit()
            return True
        except sqlite3.Error as e: 
            print(f"Database error: {e}")
            self.db_connection.rollback()
            return False
                

    def update_character_stats(self, 
                               save_data_id:int,
                               character_class:str, 
                               character_exp:int, 
                               character_level:int, 
                               character_wave:int) -> bool:
        try:
            sql = """UPDATE character_stats 
                    SET character_class = ?, 
                        character_exp = ?, 
                        character_level = ?, 
                        character_wave = ? 
                    WHERE save_data_id = ?"""
            self.cursor.execute(sql, (character_class, character_exp, character_level, character_wave, save_data_id))
            self.db_connection.commit()
            return True
        except sqlite3.Error as e: 
            print(f"Database error: {e}")
            self.db_connection.rollback()
            return False

    def update_character_inventory(self, 
                                   save_data_id:int, 
                                   character_weapons:str, 
                                   character_armors:str, 
                                   character_accessories:str, 
                                   character_consumables:str) -> bool:
        try:
            sql = """UPDATE character_inventory 
                    SET character_weapons = ?, 
                        character_armors = ?, 
                        character_accessories = ?, 
                        character_consumables = ? 
                    WHERE save_data_id = ?"""
            self.cursor.execute(sql, (character_weapons, character_armors, character_accessories, character_consumables, save_data_id))
            self.db_connection.commit()
            return True
        except sqlite3.Error as e: 
            print(f"Database error: {e}")
            self.db_connection.rollback() 
            return False

