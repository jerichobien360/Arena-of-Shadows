import sqlite3
import json
from datetime import datetime

def view_database(db_path='maps.db'):
    """View the contents of the SQLite database"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=" * 60)
        print("SQLite Database Viewer - Maps Database")
        print("=" * 60)
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("No tables found in the database.")
            return
        
        print(f"Tables found: {[table[0] for table in tables]}")
        print()
        
        # Get all maps
        cursor.execute("SELECT * FROM maps ORDER BY updated_at DESC")
        maps = cursor.fetchall()
        
        if not maps:
            print("No maps found in the database.")
            return
        
        print(f"Total maps: {len(maps)}")
        print("-" * 60)
        
        for map_data in maps:
            id, name, grid_data, created_at, updated_at = map_data
            
            print(f"Map ID: {id}")
            print(f"Name: {name}")
            print(f"Created: {created_at}")
            print(f"Updated: {updated_at}")
            
            # Parse and display grid info
            try:
                grid = json.loads(grid_data)
                grid_size = len(grid)
                
                # Count tile types
                tile_counts = {}
                for row in grid:
                    for tile in row:
                        tile_counts[tile] = tile_counts.get(tile, 0) + 1
                
                print(f"Grid Size: {grid_size}x{grid_size}")
                print("Tile Distribution:")
                
                tile_names = {
                    0: "Empty",
                    1: "Grass", 
                    2: "Dirt",
                    3: "Water",
                    4: "Wall",
                    5: "Gold"
                }
                
                for tile_id, count in sorted(tile_counts.items()):
                    tile_name = tile_names.get(tile_id, f"Unknown({tile_id})")
                    percentage = (count / (grid_size * grid_size)) * 100
                    print(f"  {tile_name}: {count} tiles ({percentage:.1f}%)")
                
                print()
                
            except json.JSONDecodeError:
                print("Error: Invalid grid data format")
                print()
            
            print("-" * 60)
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except FileNotFoundError:
        print(f"Database file '{db_path}' not found. Run the map editor first to create it.")

def view_specific_map(map_name, db_path='maps.db'):
    """View a specific map in ASCII format"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT grid_data FROM maps WHERE name = ?", (map_name,))
        result = cursor.fetchone()
        
        if not result:
            print(f"Map '{map_name}' not found.")
            return
        
        grid = json.loads(result[0])
        
        print(f"Map: {map_name}")
        print("=" * (len(grid[0]) * 2 + 1))
        
        # ASCII representation
        tile_chars = {
            0: '.',  # Empty
            1: 'G',  # Grass
            2: 'D',  # Dirt
            3: 'W',  # Water
            4: '#',  # Wall
            5: '$'   # Gold
        }
        
        for row in grid:
            line = ""
            for tile in row:
                char = tile_chars.get(tile, '?')
                line += char + " "
            print(line)
        
        print("=" * (len(grid[0]) * 2 + 1))
        print("Legend: . = Empty, G = Grass, D = Dirt, W = Water, # = Wall, $ = Gold")
        
        conn.close()
        
    except Exception as e:
        print(f"Error viewing map: {e}")

def export_map_to_text(map_name, output_file=None, db_path='maps.db'):
    """Export a map to a text file"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM maps WHERE name = ?", (map_name,))
        result = cursor.fetchone()
        
        if not result:
            print(f"Map '{map_name}' not found.")
            return
        
        id, name, grid_data, created_at, updated_at = result
        grid = json.loads(grid_data)
        
        if output_file is None:
            output_file = f"{map_name}_export.txt"
        
        with open(output_file, 'w') as f:
            f.write(f"Map Export: {name}\n")
            f.write(f"Created: {created_at}\n")
            f.write(f"Updated: {updated_at}\n")
            f.write(f"Size: {len(grid)}x{len(grid[0])}\n\n")
            
            # Write grid as numbers
            f.write("Grid Data (numbers):\n")
            for row in grid:
                f.write(" ".join(map(str, row)) + "\n")
            
            f.write("\nGrid Data (visual):\n")
            tile_chars = {0: '.', 1: 'G', 2: 'D', 3: 'W', 4: '#', 5: '$'}
            for row in grid:
                line = ""
                for tile in row:
                    char = tile_chars.get(tile, '?')
                    line += char + " "
                f.write(line + "\n")
            
            f.write("\nLegend:\n")
            f.write(". = Empty (0)\n")
            f.write("G = Grass (1)\n") 
            f.write("D = Dirt (2)\n")
            f.write("W = Water (3)\n")
            f.write("# = Wall (4)\n")
            f.write("$ = Gold (5)\n")
        
        print(f"Map '{map_name}' exported to '{output_file}'")
        conn.close()
        
    except Exception as e:
        print(f"Error exporting map: {e}")

if __name__ == "__main__":
    print("SQLite Database Viewer")
    print("Choose an option:")
    print("1. View all maps")
    print("2. View specific map (ASCII)")
    print("3. Export map to text file")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        view_database()
    elif choice == "2":
        map_name = input("Enter map name: ").strip()
        if map_name:
            view_specific_map(map_name)
    elif choice == "3":
        map_name = input("Enter map name to export: ").strip()
        if map_name:
            export_map_to_text(map_name)
    else:
        print("Invalid choice. Showing all maps by default:")
        view_database()
