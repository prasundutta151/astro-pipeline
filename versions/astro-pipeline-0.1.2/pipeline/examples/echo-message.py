#!/usr/bin/env python3
"""Small runnable CLI intent used by the first-run sample."""
import argparse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--message", required=True)
parser.add_argument("--count", type=int, default=1)
parser.add_argument("--uppercase", action="store_true")
args = parser.parse_args()
if args.count < 0:
    parser.error("--count must be nonnegative")
for _ in range(args.count):
    print(args.message.upper() if args.uppercase else args.message)
