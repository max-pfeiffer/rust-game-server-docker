#!/bin/bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:`dirname $0`/RustDedicated_Data/Plugins:`dirname $0`/RustDedicated_Data/Plugins/x86_64

if [[ -n "${POD_NAME}" ]]; then
  if [[ -f "/srv/rust/config/${POD_NAME}" ]]; then
    source "/srv/rust/config/${POD_NAME}"
  else
    echo "File with environment variables at /srv/rust/config/${POD_NAME} does not exit"
    exit 1
  fi
fi

./RustDedicated -batchmode "$@"
