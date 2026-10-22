#!/usr/bin/env bash
# Build fmtools Rust binaries for the native host or explicit Rust targets.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
RUST_DIR="$SCRIPT_DIR/rust"
BIN_DIR="$SCRIPT_DIR/src/fmtools/bin"

target_to_platform() {
    case "$1" in
        x86_64-pc-windows-msvc)
            printf '%s\n' windows
            ;;
        x86_64-unknown-linux-gnu)
            printf '%s\n' linux
            ;;
        x86_64-apple-darwin)
            printf '%s\n' macos-x64
            ;;
        aarch64-apple-darwin)
            printf '%s\n' macos-arm64
            ;;
        *)
            echo "Unsupported packaging target: $1" >&2
            return 1
            ;;
    esac
}

if ! command -v cargo >/dev/null || ! command -v rustc >/dev/null; then
    echo "ERROR: Rust is not installed. Install it from https://rustup.rs/" >&2
    exit 1
fi

if (($#)); then
    targets=("$@")
else
    host_target="$(rustc -vV | sed -n 's/^host: //p')"
    if [[ -z "$host_target" ]]; then
        echo "ERROR: Could not determine the Rust host target." >&2
        exit 1
    fi
    targets=("$host_target")
fi

for target in "${targets[@]}"; do
    platform_dir="$(target_to_platform "$target")"
    echo "Building Rust tools for $target ($platform_dir)"
    rustup target add "$target"
    cargo build --manifest-path "$RUST_DIR/Cargo.toml" --locked --release --workspace --target "$target"

    release_dir="$RUST_DIR/target/$target/release"
    output_dir="$BIN_DIR/$platform_dir"
    mkdir -p "$output_dir"

    if [[ "$platform_dir" == windows ]]; then
        extension=.exe
    else
        extension=
    fi

    for binary in dupeforge-rs rename_files organize_files convert_media; do
        cp "$release_dir/$binary$extension" "$output_dir/"
    done

    if [[ "$platform_dir" != windows ]]; then
        chmod +x "$output_dir"/*
    fi
done

echo "Rust binaries are available under $BIN_DIR/<platform>/"

