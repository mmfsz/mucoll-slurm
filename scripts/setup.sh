#!/bin/bash

#source /opt/spack/opt/spack/__spack_path_placeholder__/__spack_path_placeholder__/__spack_path_placeholder__/__spack_path_placeholder__/linux-x86_64/mucoll-stack-2025-11-11-qnljda2jpzad6mfv26pge4ux75mnbl3v/setup.sh
# Expected spack stack for the current container image. Bump this string when the
# image is bumped (it is the ONE place that names the stack, matched by glob below so
# the __spack_path_placeholder__ hash need not be tracked here).
_want_stack="mucoll-stack-2026-01-29"
_stack_setup=$(ls /opt/spack/opt/spack/*/*/*/*/linux-x86_64/${_want_stack}-*/setup.sh 2>/dev/null | head -1)
if [ -z "$_stack_setup" ]; then
    echo "ERROR: expected spack stack '${_want_stack}' not found in this container." >&2
    echo "       Your .sif is likely stale — re-pull the image:" >&2
    echo "         apptainer pull --force mucoll-sim.sif docker://ghcr.io/muoncollidersoft/mucoll-sim-ubuntu24:main" >&2
else
    source "$_stack_setup"
    echo "Loaded spack stack: ${_want_stack}"
fi

export PS1="[\u@\h \w]\$ "
alias ls='ls --color=auto'
