#!/bin/bash

######################################################################################
# Script to pull current system logs and information to aid with investigative efforts.
# Can be extended to include - as necessary - other logs such as dmesg, kernel, secure etc
######################################################################################

BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOG_DIR="${BASE_DIR}/system_logs_$(date '+%Y-%m-%d-%H-%M-%S')"

# Create log directory
mkdir -p "${LOG_DIR}"

# Get the last 200 megabytes of data from /var/log/messages
function get_var_log_messages(){
  tail -c 200M /var/log/messages > "${LOG_DIR}/var_log_messages.txt"
}

# Get output of top e.g. top -b -n1 -o %MEM
function get_top_running_processes_by_memory_usage(){
  top -b -n1 -o +%MEM > "${LOG_DIR}/top_output_sort_memory.txt"
}

# Get free memory
function get_memory_usage_info(){
  free -h > "${LOG_DIR}/memory_usage.txt"
}

# Get disk usage
function get_filesystem_disk_usage_info(){
  df -h --total > "${LOG_DIR}/disk_space_usage.txt"
  df -ih --total > "${LOG_DIR}/disk_inode_space_usage.txt"
}

# Get uptime with load average
function get_uptime_info(){
  uptime > "${LOG_DIR}/uptime.txt"
}

compress_files() {
    echo "Generating tar file and removing logs directory..."
    tar -czf "${LOG_DIR}.tgz" -C "${LOG_DIR}" .
    echo  -e "\e[1m\e[31mGenerated file ${LOG_DIR}.tgz, Please collect and send to ADP Support!\e[0m"
    rm -rf "${LOG_DIR}"
}

get_uptime_info &
get_filesystem_disk_usage_info &
get_memory_usage_info &
get_top_running_processes_by_memory_usage
get_var_log_messages
compress_files
