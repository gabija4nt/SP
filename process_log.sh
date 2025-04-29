#!/bin/bash

# Get current datetime
date_time=$(date +"%Y-%m-%d-%H-%M-%S")
logs_dir="logs-$date_time"
mkdir -p "$logs_dir"

# Check if a username is provided
if [ -n "$1" ]; then
    users=("$1")  # Only the specific user
else
    users=($(ps -eo user= | sort | uniq))  # All users
fi

# Generate log files for each user
for user in "${users[@]}"; do
    # Clean user name (in case of trailing spaces)
    clean_user=$(echo "$user" | tr -d '[:space:]')
    log_file="$logs_dir/${clean_user}-process-log-$date_time.log"

    {
        echo "Date: $(date +%Y-%m-%d)"
        echo "Time: $(date +%H:%M:%S)"
        echo
        echo "Processes for user: $clean_user"
        echo "----------------------------------------"
        # Skip if no processes for user
        ps -u "$clean_user" -o pid=,comm=,%cpu=,%mem=,etime=,rss= 2>/dev/null | while read -r pid comm cpu mem etime rss; do
            echo "PID: $pid"
            echo "Name: $comm"
            echo "CPU: $cpu%"
            echo "Memory: $mem%"
            echo "Elapsed Time: $etime"
            echo "Memory Usage (RSS): ${rss}KB"
            echo "----------------------------------------"
        done
    } > "$log_file"  # Redirect output to file instead of terminal

    echo "Created log: $log_file"
done

echo
echo "Log files have been created in: $logs_dir"
echo "----------------------------------------"

# List files with line counts
total_lines=0
for file in "$logs_dir"/*.log; do
    line_count=$(wc -l < "$file")
    echo "File: $(basename "$file") - $line_count lines"
    total_lines=$((total_lines + line_count))
done

echo "Total line count across all files: $total_lines"
echo

# If a single user was given, show that user's file content
if [ -n "$1" ]; then
    user_file="$logs_dir/${1}-process-log-$date_time.log"
    echo "----- Log content for user '$1' -----"
    cat "$user_file"
    echo "-------------------------------------"
fi

# Wait for Enter, then cleanup
echo
read -p "Press Enter to delete logs and exit..." _
rm -rf "$logs_dir"
echo "Logs deleted. Goodbye!"

