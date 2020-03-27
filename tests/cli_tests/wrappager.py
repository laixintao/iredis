#!/usr/bin/env python
import sys
import fileinput


def wrappager(boundary):
    print(boundary)
    for line in fileinput.input(files="-"):
        sys.stdout.write(line)
    print(boundary)


if __name__ == "__main__":
    wrappager(sys.argv[1])
