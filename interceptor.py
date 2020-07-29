#!/usr/bin/env python3
import sys

def error(parser):
    def wrapper(interceptor):
        parser.print_help()

        sys.exit(-1)

    return wrapper
