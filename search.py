import os
import sys
import time
import subprocess
from datetime import datetime

DELIMITER = "---------"

def get_file_info(path):
    try:
        stats = os.stat(path)
        created = time.ctime(stats.st_ctime)
        accessed = time.ctime(stats.st_atime)
        return created, accessed
    except Exception as e:
        return f"Error getting file info: {e}", "", "", ""

def search_file_or_dir(root_dir, search_term):
    matches = []
    for dirpath, dirnames, filenames in os.walk(root_dir, onerror=lambda e: None):
        for name in dirnames + filenames:
            if search_term.lower() in name.lower():
                matches.append(os.path.join(dirpath, name))
    return matches

def create_log_file(search_term, matches):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(script_dir, "results.txt")

    with open(log_path, "w") as f:
        log_entries = []

        for path in matches:
            if os.path.isfile(path):
                created, accessed = get_file_info(path)
                result = (
                    f"\nType: File\n"
                    f"Name: {os.path.basename(path)}\n"
                    f"Path: {path}\n"
                    f"Created: {created}\n"
                    f"Accessed: {accessed}\n"
                    f"\n{DELIMITER}\n"
                )
            elif os.path.isdir(path):
                try:
                    content = os.listdir(path)
                    content_str = ', '.join(content)
                except Exception as e:
                    content_str = f"Error reading contents: {e}"
                created, accessed = get_file_info(path)
                result = (
                    f"Type: Directory\n"
                    f"Path: {path}\n"
                    f"Contents: {content_str}\n"
                    f"Created: {created}\n"
                    f"Accessed: {accessed}\n"
                    f"\n{DELIMITER}\n"
                )
            else:
                result = f"Unknown type: {path}"
            print(result)
            log_entries.append(result)

        log_entry = (
            f"Search Date: {datetime.now()}\n"
            f"Search Term: {search_term}\n"
            f"Start Directory: /\n"
            f"Results:\n\n{''.join(log_entries)}"
        )

        f.write(log_entry)
    return log_path

def open_and_delete_log(log_path):
    print(f"Opening log file in TextEdit: {log_path}")

    apple_script = f'''
    set theFile to POSIX file "{log_path}" as alias
    tell application "TextEdit"
        activate
        open theFile
        repeat until (count of windows) = 0
            delay 1
        end repeat
    end tell
    '''

    subprocess.run(["osascript", "-e", apple_script])
    
    if os.path.exists(log_path):
        os.remove(log_path)
        print("Log file closed and deleted.")

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 search.py <file_or_directory_name_part>")
        sys.exit(1)

    search_term = sys.argv[1]
    start_dir = "/"

    if not os.path.isdir(start_dir):
        print(f"Error: '{start_dir}' is not a valid directory.")
        sys.exit(1)

    matches = search_file_or_dir(start_dir, search_term)

    if matches:
        log_path = create_log_file(search_term, matches)
        open_and_delete_log(log_path)
    else:
        print("No matching files or directories found.")

if __name__ == "__main__":
    main()
