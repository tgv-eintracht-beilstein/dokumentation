# Detect OS for platform-specific library paths
build:
    #!/usr/bin/env sh
    if [ "$(uname)" = "Darwin" ]; then
        DYLD_FALLBACK_LIBRARY_PATH="$(brew --prefix)/lib" uv run python build.py
    else
        uv run python build.py
    fi
