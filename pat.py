#!/usr/bin/python

import argparse
import logging
import os

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Process command line options.')
    parser.add_argument('-d','--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('-c','--config', help='Specify a config file to use',
                        type=str, default='config.yaml')
    parser.add_argument('--version', action='version', version='0')
    args = parser.parse_args()

    # Setup logging options
    log_level = logging.DEBUG if args.debug else logging.INFO
    log = logging.getLogger(os.path.basename(__file__))
    log.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(funcName)s(%(lineno)i):%(message)s')

    ## Console Logging
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    ch.setFormatter(formatter)
    log.addHandler(ch)

    ## File Logging
    fh = logging.FileHandler(os.path.basename(__file__) + '.log')
    fh.setLevel(log_level)
    log.addHandler(fh)
    fh.setFormatter(formatter)

    log.info("PAT Initializing...")
    if os.path.isfile(args.config):
        log.info("Loading config file %s" % args.config)
    else:
        log.info("Config file does not exist, creating a default config...")

    log.info("PAT Initialized")
    log.info("PAT shutting down...")
