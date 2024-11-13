"""Remove unused files from geocache."""

import sys
from pathlib import Path


def main():
    (input_file,) = sys.argv[1:]
    used_files = set(line.strip() for line in open(input_file).readlines())
    sys.stderr.write(f"Read {len(used_files)} used files from {input_file}\n")

    geocache = Path("geocache")
    n_delete = 0
    for cache_file in geocache.iterdir():
        if ("geocache/" + cache_file.name) not in used_files:
            cache_file.unlink()
            # print(f"Would remove {cache_file}")
            n_delete += 1

    sys.stderr.write(f"Deleted {n_delete} files\n")


if __name__ == "__main__":
    main()
