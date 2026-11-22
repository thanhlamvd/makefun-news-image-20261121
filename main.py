#!/usr/bin/env python3
"""Entry for make.fun news-image-20261121.

Places the committed front-page image (entry.png, 1024x1024) into
the output directory as entry.png. Python 3.13 standard library
only; no network, no clock, no randomness, so two runs write the
same bytes. The output directory comes from MAKEFUN_OUTPUT_DIR
and defaults to /output.
"""

import os
import shutil
import struct
import sys
from pathlib import Path

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1048576


def check_png(path: Path) -> None:
    """Refuse to deliver a file that is not a whole 1024x1024 PNG
    inside the 1 MiB limit: the gate rejects anything else."""
    data = path.read_bytes()
    if len(data) > MAX_BYTES:
        raise SystemExit("entry.png over the 1 MiB limit: %d bytes"
                         % len(data))
    if data[:8] != PNG_MAGIC:
        raise SystemExit("entry.png is not a PNG")
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (1024, 1024):
        raise SystemExit("entry.png is %dx%d, not 1024x1024"
                         % (width, height))
    if data[-8:-4] != b"IEND":
        raise SystemExit("entry.png has no IEND chunk")


def main() -> int:
    here = Path(__file__).resolve().parent
    source = here / "entry.png"
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    shutil.copyfile(source, target)
    check_png(target)
    print("wrote %s" % target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
