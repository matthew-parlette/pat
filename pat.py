#!/usr/bin/python

import argparse
import logging
import os
import yaml
import trello.util
from trello import TrelloClient

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Process command line options.')
    parser.add_argument('-d','--debug', action='store_true',
                        help='Enable debug logging')
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
    defaults = {
        "trello": {
            "key": "",
            "secret": "",
            "oauth_token": "",
            "oauth_token_secret": "",
        }
    }
    if os.path.isfile(args.config):
        log.info("Loading config file %s" % args.config)
        config = yaml.load(file(args.config))
        if config:
            # config contains items
            config = dict(defaults.items() + yaml.load(file(args.config)).items())
        else:
            # config is empty, just use defaults
            config = defaults
    else:
        log.info("Config file does not exist, creating a default config...")
        with open(args.config, 'w') as outfile:
            outfile.write( yaml.dump(defaults, default_flow_style=False) )
        config = defaults
    log.debug("Config loaded as:\n%s" % str(config))

    if config['trello']['oauth_token'] == "":
        # Need to get the trello oauth_token and oauth_token_secret
        log.debug("Retrieving Trello oauth token...")
        os.environ["TRELLO_API_KEY"] = config["trello"]["key"]
        os.environ["TRELLO_API_SECRET"] = config["trello"]["secret"]
        os.environ["TRELLO_EXPIRATION"] = 'never'
        trello.util.create_oauth_token()

    log.debug("Creating Trello client...")
    trello_api = TrelloClient(
        api_key=config["trello"]["key"],
        api_secret=config["trello"]["secret"],
        token=config["trello"]["oauth_token"],
        token_secret=config["trello"]["oauth_token_secret"]
    )
    print trello_api.list_boards()

    log.info("PAT Initialized")
    log.info("PAT shutting down...")
