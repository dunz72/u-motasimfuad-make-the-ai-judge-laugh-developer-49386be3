"""Developer-excuses entry runner.

Reads the single-line excuse from entry.txt beside this file, checks it
against the competition gate (one line, 1-200 characters), and copies it
byte for byte into $MAKEFUN_OUTPUT_DIR/entry.txt (default /output).
The copy is then re-read and its SHA-256 is compared with the source,
so a truncated or mangled write is caught here instead of failing on
the grader. Standard library only: the grading image ships no
third-party packages.
"""

import hashlib
import os
import sys


CHAR_LIMIT = 200


def abort(reason):
    """Report a problem on stderr and stop with a non-zero exit."""
    print(f"error: {reason}", file=sys.stderr)
    sys.exit(1)


def script_dir():
    """Directory holding this script (and entry.txt)."""
    return os.path.dirname(os.path.abspath(__file__))


def read_bytes(path):
    """Return the raw bytes of path, or stop with an error."""
    try:
        with open(path, "rb") as handle:
            return handle.read()
    except OSError as exc:
        abort(f"cannot read {path}: {exc}")


def decode_text(data):
    """Decode entry bytes as UTF-8, or stop with an error."""
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        abort("entry.txt is not valid UTF-8")


def check_line(text):
    """Enforce the gate: exactly one visible line, 1-200 chars."""
    if "\n" in text or "\r" in text:
        abort("entry.txt must hold exactly one line (no newline)")
    if not text.strip():
        abort("entry.txt must not be empty or only whitespace")
    if len(text) > CHAR_LIMIT:
        abort(
            f"entry is {len(text)} chars, but the sealed limit is {CHAR_LIMIT}"
        )
    # One visible line, nothing hidden before or after it.
    if text != text.strip():
        abort("entry.txt must not have leading or trailing spaces")


def output_dir():
    """Destination directory from the environment, or /output."""
    return os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"


def ensure_dir(path):
    """Create the output directory if needed, or stop with an error."""
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as exc:
        abort(f"cannot create output dir {path}: {exc}")


def write_copy(path, data):
    """Write data to path, or stop with an error."""
    try:
        with open(path, "wb") as handle:
            handle.write(data)
    except OSError as exc:
        abort(f"cannot write {path}: {exc}")


def digest(data):
    """SHA-256 hex digest of data."""
    return hashlib.sha256(data).hexdigest()


def confirm_copy(path, expected):
    """Re-read path and stop unless its digest matches expected."""
    written = read_bytes(path)
    if digest(written) != expected:
        abort("output differs from entry.txt (sha256 mismatch)")


def run():
    source = os.path.join(script_dir(), "entry.txt")
    data = read_bytes(source)
    text = decode_text(data)
    check_line(text)

    dest_dir = output_dir()
    ensure_dir(dest_dir)
    dest = os.path.join(dest_dir, "entry.txt")
    write_copy(dest, data)
    confirm_copy(dest, digest(data))

    print(f"wrote {len(data)} bytes, {len(text)} chars -> {dest}")
    print(f"sha256: {digest(data)}")


if __name__ == "__main__":
    run()
