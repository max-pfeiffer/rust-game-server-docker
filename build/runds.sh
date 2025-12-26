#!/bin/bash
# Check for Helm chart specific files containing environment variables
if [[ -n "${CONFIG_FILE_PATH}" ]]; then
  if [[ -f "${CONFIG_FILE_PATH}" ]]; then
    source "${CONFIG_FILE_PATH}"
  else
    echo "SECRET_FILE_PATH is set, but file with environment variables at ${CONFIG_FILE_PATH} does not exit"
    exit 1
  fi
fi

if [[ -n "${SECRET_FILE_PATH}" ]]; then
  if [[ -f "${SECRET_FILE_PATH}" ]]; then
    source "${SECRET_FILE_PATH}"
  else
    echo "SECRET_FILE_PATH is set, but file with environment variables at ${SECRET_FILE_PATH} does not exit"
    exit 1
  fi
fi

# Set Rust specific environment variables
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:`dirname $0`/RustDedicated_Data/Plugins:`dirname $0`/RustDedicated_Data/Plugins/x86_64

# Run Rust dedicated server
./RustDedicated -batchmode "$@"
