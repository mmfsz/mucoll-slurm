#!/bin/bash

# Load the Spack software stack shipped with the container.
#
# /opt/setup_mucoll.sh is the image's own entrypoint helper and always names the
# stack that image actually carries, so this survives image bumps with no edit
# here. (It exists in every mucoll-sim image we use, 3.0 and 3.1 alike.) We need
# it explicitly because `apptainer exec` bypasses the entrypoint — the upstream
# setup docs call this out for exactly the batch-job case.
#
# Previously this globbed a hardcoded `mucoll-stack-<date>` string that had to be
# bumped by hand on every image change.
if [ -f /opt/setup_mucoll.sh ]; then
    source /opt/setup_mucoll.sh
    echo "Loaded spack stack: ${MUCOLL_RELEASE_VERSION:-unknown}"
else
    echo "ERROR: /opt/setup_mucoll.sh not found — this is not a mucoll-sim container." >&2
    echo "       Check MUCOLL_IMAGE (see lib/image.sh)." >&2
fi

export PS1="[\u@\h \w]\$ "
alias ls='ls --color=auto'
