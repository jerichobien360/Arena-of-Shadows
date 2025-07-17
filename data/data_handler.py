import os
import sqlite3


'''for fetching save states'''
class LoadSaveState:
    def __init__(self):
        self.database_file = 'data/AOS_player_data.db'

        #check if db exists
        if not os.path.exists(self.database_file):
            print(f"Database file not found: {self.database_file}")
            return
        else:
            try:
                # Establish a connection to the database
                self.conn = sqlite3.connect(self.database_file)
                self.cursor = self.conn.cursor()
                print(f"connected to Database")

            except sqlite3.OperationalError as e:
                print(f"Error connecting to the database: {e}")
    
    def fetch_all_save_state(self):
        try:
            self.cursor.execute(f"SELECT * FROM save_data")
            result = self.cursor.fetchall()
            if result:
                return result #in the form [[save_data_1], [save_data_2], ...]
            else:
                return None
        except sqlite3.OperationalError as e:
            print(f"Database error: {e}")

    def fetch_character_stats(self, save_data_id:int):
        try:
            self.cursor.execute(f"SELECT * FROM character_stats WHERE  save_data_id = ?", (save_data_id,))
            result = self.cursor.fetchall()
            if result:
                return result #in the form [[save_data_1], [save_data_2], ...]
            else:
                return None
        except sqlite3.OperationalError as e:
            print(f"Database error: {e}")

    def fetch_character_inventory(self, save_data_id:int):
        try:
            self.cursor.execute(f"SELECT * FROM character_inventory WHERE  save_data_id = ?", (save_data_id,))
            result = self.cursor.fetchall()
            if result:
                return result #in the form [[save_data_1], [save_data_2], ...]
            else:
                return None
        except sqlite3.OperationalError as e:
            print(f"Database error: {e}")


'''adding new save state'''
class AddSaveState:
    def __init__(self):
        self.database_file = 'data/AOS_player_data.db'

        #check if db exists
        if not os.path.exists(self.database_file):
            print(f"Database file not found: {self.database_file}")
            return
        else:
            try:
                # Establish a connection to the database
                self.conn = sqlite3.connect(self.database_file)
                self.cursor = self.conn.cursor()
                print(f"connected to Database")

            except sqlite3.OperationalError as e:
                print(f"Error connecting to the database: {e}")
    
    def add_save_state(self, save_title:str, character_class:str, character_exp:int, character_level:int, character_wave:int, character_weapons:str, character_armors:str, character_accessories:str, character_consumables:str):
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
            
            self.conn.commit()
            return True
        
        except sqlite3.Error as e:  
            print(f"Database error: {e}")
            self.conn.rollback() 
            return False
        
        finally:
            if self.conn:
                self.conn.close()


'''for updating/changing save data'''
class UpdateSaveData:
    def __init__(self):
        self.database_file = 'data/AOS_player_data.db'

        #check if db exists
        if not os.path.exists(self.database_file):
            print(f"Database file not found: {self.database_file}")
            return
        else:
            try:
                # Establish a connection to the database
                self.conn = sqlite3.connect(self.database_file)
                self.cursor = self.conn.cursor()
                print(f"connected to Database")

            except sqlite3.OperationalError as e:
                print(f"Error connecting to the database: {e}")
    
    '''use this if you want to add an option to rename a save state'''
    def update_save_state(self,save_data_id:int, new_save_title:str):
        try:
            sql = """UPDATE save_data 
                    SET save_data_title = ?, 
                    WHERE save_data_id = ?"""
            self.cursor.execute(sql, (save_data_id, new_save_title))
            self.conn.commit()
            return True
        except sqlite3.Error as e: 
            print(f"Database error: {e}")
            self.conn.rollback() 
        finally:
            if self.conn:
                self.conn.close()

    def update_character_stats(self, save_data_id:int, character_class:str, character_exp:int, character_level:int, character_wave:int):
        try:
            sql = """UPDATE character_stats 
                    SET character_class = ?, 
                        character_exp = ?, 
                        character_level = ?, 
                        character_wave = ? 
                    WHERE save_data_id = ?"""
            self.cursor.execute(sql, (character_class, character_exp, character_level, character_wave, save_data_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e: 
            print(f"Database error: {e}")
            self.conn.rollback() 
        finally:
            if self.conn:
                self.conn.close()

    def update_character_inventory(self, save_data_id:int, character_weapons:str, character_armors:str, character_accessories:str, character_consumables:str):
        try:
            sql = """UPDATE character_inventory 
                    SET character_weapons = ?, 
                        character_armors = ?, 
                        character_accessories = ?, 
                        character_consumables = ? 
                    WHERE save_data_id = ?"""
            self.cursor.execute(sql, (character_weapons, character_armors, character_accessories, character_consumables, save_data_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e: 
            print(f"Database error: {e}")
            self.conn.rollback() 
        finally:
            if self.conn:
                self.conn.close()

