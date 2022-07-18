#!/usr/bin/env python3

import argparse

parser = argparse.ArgumentParser(prog="ffssb")
subparsers = parser.add_subparsers()

# create
parser_create = subparsers.add_parser("create", help = "create a new site specific browser application.")
parser_create.add_argument("name", help="name of the application")
parser_create.add_argument("url", help="url the application will use")
parser_create.add_argument("--skip-user-chrome", action="store_true", help="do not add userChrome.css to profile")

# remove
parser_remove = subparsers.add_parser("remove", help = "remove site specific browser application.")
parser_remove.add_argument("name", help="name of the application")

args = parser.parse_args()

vars = vars(args)
print(args)
