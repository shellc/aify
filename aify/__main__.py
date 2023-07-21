#!/usr/bin/env python
import os
import sys
import argparse
import uvicorn
from uvicorn.config import LOGGING_CONFIG

import aify
import aify.embeddings

logger = {"handlers": ["default"], "level": "INFO", "propagate": False}
LOGGING_CONFIG['loggers'][''] = logger
LOGGING_CONFIG['loggers']['aify'] = logger

AIFY_LIB_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.pardir))
sys.path.insert(0, AIFY_LIB_DIR)


def runserver(args):
    """
    Initialize and start the uvicorn service process.
    """
    apps_dir = args.apps_dir
    if apps_dir:
        apps_dir = os.path.abspath(apps_dir)
        os.environ['AIFY_APPS_DIR'] = apps_dir

        if args.reload:
            if not args.reload_dirs:
                args.reload_dirs = []
                args.reload_dirs.append(AIFY_LIB_DIR)
            args.reload_dirs.append(apps_dir)

    uvicorn.run('aify:entry',
                host=args.host,
                port=args.port,
                workers=args.workers,
                reload=args.reload,
                h11_max_incomplete_event_size=0,
                log_config=LOGGING_CONFIG,
                reload_dirs=args.reload_dirs,
                reload_includes="**/*.[py][ym]*"
                )


parser = argparse.ArgumentParser()
parser.add_argument('--env-file', default='.env',
                    help="environment configuration file")

subparser = parser.add_subparsers(
    title="commands", help="type command --help to print help message")

# run command
parser_run = subparser.add_parser('run', help="run aify server")
parser_run.add_argument('-H', '--host', default='127.0.0.1',
                        help="bind socket to this host. default: 127.0.0.1")
parser_run.add_argument('-p', '--port', default=2000,
                        type=int, help="bind socket to this port, default: 2000")
parser_run.add_argument('-w', '--workers', default=1, type=int,
                        help="number of worker processes, default: 1")
parser_run.add_argument('-r', '--reload', default=True,
                        action='store_true', help="enable auto-reload")
parser_run.add_argument('--reload-dirs', default=None,
                        help="set reload directories explicitly, default is applications directory")

parser_run.add_argument("apps_dir", nargs='?',
                        default=None, help="applications directory")
parser_run.set_defaults(func=runserver)

# embed command
parser_embed = subparser.add_parser(
    'embed', help="build embeddings from a CSV dataset")
parser_embed.add_argument("from_csv_file", help="read data from this CSV file")
parser_embed.add_argument(
    "to_csv_file", help="write embeddings to this CSV file")
parser_embed.set_defaults(func=lambda args: aify.embeddings.build_csv(
    args.from_csv_file, args.to_csv_file))


def main():
    """
    Main function to start Aify.
    """
    args = parser.parse_args(sys.argv[1:])

    if os.path.exists(args.env_file):
        from dotenv import load_dotenv
        load_dotenv(args.env_file)

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


# Fire
main()
