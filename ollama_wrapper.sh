#!/bin/bash
# Wrapper to run ollama inside the 'ollama' docker container

# Determine if we need interactive TTY
if [ -t 0 ]; then
    IT="-it"
else
    IT="-i"
fi

# Exec into docker container
exec docker exec $IT ollama ollama "$@"
