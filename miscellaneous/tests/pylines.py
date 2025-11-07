import os
import sys
from pathlib import Path

# Configuration
EXCLUDED_DIRS = {'.venv', '__pycache__', '.git', '.pytest_cache', 'node_modules', 'venv', 'env'}
PYTHON_EXTENSIONS = {'.py', '.pyx', '.pyi'}  # Include Cython and stub files
MIN_LINES_TO_SHOW = 0  # Only show files with at least this many lines

def count_lines_in_file(filepath):
    """Count all lines in a file, handling various encodings."""
    encodings = ['utf-8', 'latin-1', 'cp1252', 'ascii']
    
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                # Count all lines (including empty ones for true LOC count)
                lines = sum(1 for line in f)
                return lines
        except (UnicodeDecodeError, UnicodeError):
            continue
        except Exception as e:
            print(f"Warning: Failed to read {filepath}: {e}", file=sys.stderr)
            return 0
    
    print(f"Warning: Could not decode {filepath} with any encoding", file=sys.stderr)
    return 0

def should_exclude_file(filepath):
    """Check if a file should be excluded based on common patterns."""
    path = Path(filepath)
    
    # Only exclude auto-generated files, not __init__.py which are legitimate
    excluded_patterns = ['_pb2.py', '_pb2_grpc.py']
    
    # Exclude files that are likely auto-generated
    if any(pattern in path.name for pattern in excluded_patterns):
        return True
    
    return False

def main():
    """Main function to count lines in Python files."""
    start_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    
    if not os.path.exists(start_dir):
        print(f"Error: Directory '{start_dir}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    print(f"Counting Python lines in: {os.path.abspath(start_dir)}")
    print(f"Excluded directories: {', '.join(sorted(EXCLUDED_DIRS))}")
    print("-" * 50)
    
    file_stats = []
    total_lines = 0
    total_files = 0
    
    try:
        for root, dirs, files in os.walk(start_dir):
            # Skip hidden directories and excluded ones
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in EXCLUDED_DIRS]
            
            for file in files:
                # Check if it's a Python file
                if not any(file.endswith(ext) for ext in PYTHON_EXTENSIONS):
                    continue
                
                filepath = os.path.join(root, file)
                
                # Skip files we want to exclude
                if should_exclude_file(filepath):
                    continue
                
                lines = count_lines_in_file(filepath)
                
                if lines >= MIN_LINES_TO_SHOW:
                    total_lines += lines
                    total_files += 1
                    # Store relative path for cleaner output
                    rel_path = os.path.relpath(filepath, start_dir)
                    file_stats.append((lines, rel_path))
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error during file traversal: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Sort by line count (descending)
    file_stats.sort(reverse=True, key=lambda x: x[0])
    
    # Display results
    if not file_stats:
        print("No Python files found!")
        return
    
    print("\nResults (sorted by line count):")
    print("-" * 50)
    
    for lines, filepath in file_stats:
        print(f"{lines:6,} lines | {filepath}")
    
    print("-" * 50)
    print(f"Total: {total_lines:,} lines across {total_files} Python files")
    
    # Additional statistics
    if file_stats:
        avg_lines = total_lines / total_files
        largest_file = file_stats[0]
        print(f"Average: {avg_lines:.1f} lines per file")
        print(f"Largest: {largest_file[1]} ({largest_file[0]:,} lines)")
        
        # Show summary by size categories
        small_files = sum(1 for lines, _ in file_stats if lines < 50)
        medium_files = sum(1 for lines, _ in file_stats if 50 <= lines < 200)
        large_files = sum(1 for lines, _ in file_stats if lines >= 200)
        
        print(f"\nFile size distribution:")
        print(f"  Small (<50 lines): {small_files} files")
        print(f"  Medium (50-199 lines): {medium_files} files") 
        print(f"  Large (200+ lines): {large_files} files")

if __name__ == "__main__":
    main()
