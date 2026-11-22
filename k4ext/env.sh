# Source after lib/env.sh to make the k4ext components loadable by k4run.
K4EXT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ ! -f "$K4EXT_DIR/install/lib/libConeSeedsPlugins.so" ]; then
    echo "ERROR: k4ext not built; run k4ext/build.sh inside the container" >&2
    return 1
fi
export LD_LIBRARY_PATH="$K4EXT_DIR/install/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export PYTHONPATH="$K4EXT_DIR/install/python:$K4EXT_DIR/install/lib${PYTHONPATH:+:$PYTHONPATH}"
return 0
