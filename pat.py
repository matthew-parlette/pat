#!/usr/bin/python

import argparse
import logging
import os
import yaml
import trello.util
from datetime import date, timedelta
from trello import TrelloClient

class PluginMount(type):
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            # This branch only executes when processing the mount point itself.
            # So, since this is a new plugin type, not an implementation, this
            # class shouldn't be registered as a plugin. Instead, it sets up a
            # list where plugins can be registered later.
            cls.plugins = []
        else:
            # This must be a plugin implementation, which should be registered.
            # Simply appending it to the list is all that's needed to keep
            # track of it later.
            cls.plugins.append(cls)

class ReportProvider:
    __metaclass__ = PluginMount

    def __init__(self, log, config):
        log.info("Registering %s as a Report Provider" % str(self.__class__.__name__))
        self.log = log
        self.config = config

class Trello(ReportProvider):
    """docstring for Trello"""
    def __init__(self, log, config):
        super(Trello, self).__init__(log, config)
        self.log.info("Initializing Trello client...")
        self.api = TrelloClient(
            self.config['trello']['key'],
            self.config['trello']['secret'],
            self.config['trello']['oauth_token'],
            self.config['trello']['oauth_token_secret']
        )
        self.log.info("Trello client initialized")

    def run(self,date):
        result = ""
        self.log.debug("Retrieving list of boards...")
        for board in self.api.list_boards():
            if board.closed is False:
                self.log.debug("Found open board %s" % board)
                self.log.debug("Getting card with actions on %s" % (
                    date.isoformat()
                ))
                cards = board.get_cards({
                    'actions': 'all',
                    'since': date.isoformat(),
                    })
                self.log.debug("Cards loaded as %s" % str(cards))
                if cards:
                    self.log.debug("Board %s has updated cards" % board)
                    result += "%s\n" % (str(board))
                    for card in cards:
                        self.log.debug("Processing card %s" % card)
                        card.fetch_actions(action_filter='all')
                        if card.actions:
                            result += "\t%s\n" % card.name
                        for action in card.actions or []:
                            self.log.debug("Action dictionary is %s" % str(action))
                            result += "\t\t%s\n" % (
                                str(self.action_string(action))
                            )
                else:
                    self.log.debug("Board %s has no updates for this timeframe" % board)
        return result

    def action_string(self,action):
        """Generate a readable string for the provided action.

        action is a dictionary."""

        data = action[u'data']
        if action['type'] == 'createCard':
            return "Created in %s" % (
                data[u'list'][u'name'],
            )
        elif action['type'] == 'updateCard':
            # Moving card within a list or to a new list
            if data.get('list'):
                # Moved card within list
                return ""
            else:
                # Moved to new list
                if data.get('listAfter') == 'done':
                    return "Completed '%s'" % data['card']
                else:
                    return "Moved to %s" % (
                        data[u'listAfter'][u'name'],
                    )
        elif action['type'] == 'commentCard':
            if len(data['text']) <= 67:
                text = data['text']
            else:
                text = data['text'][:67] + "..."
            return "Commented\n\t\t\t%s" % (
                text,
            )
        elif action['type'] == 'addAttachmentToCard':
            return "Added %s" % (
                data[u'attachment']['name'],
            )
        elif action['type'] == 'addChecklistToCard':
            return "Added %s" % (
                data[u'checklist']['name'],
            )
        elif action['type'] == 'addMemberToCard':
            return "Assigned to %s" % (
                action[u'member'][u'initials'],
            )
        else:
            return "Unknown action type '%s'\n\t\t\t%s" % (
                action['type'],
                action['data'].keys(),
            )


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
        log.debug("Loading config file %s" % args.config)
        config = yaml.load(file(args.config))
        if config:
            # config contains items
            config = dict(defaults.items() + yaml.load(file(args.config)).items())
        else:
            # config is empty, just use defaults
            config = defaults
    else:
        log.debug("Config file does not exist, creating a default config...")
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

    # log.debug("Creating Trello client...")
    # trello = Trello(
    #     log=log,
    #     api_key=config["trello"]["key"],
    #     api_secret=config["trello"]["secret"],
    #     token=config["trello"]["oauth_token"],
    #     token_secret=config["trello"]["oauth_token_secret"]
    # ) or None
    # if trello:
    #     log.debug("Connected to Trello")

    # Load plugins
    reports = [p(log, config) for p in ReportProvider.plugins]

    log.info("PAT Initialized")

    report_date = date.today() - timedelta(days=0)
    log.info("Generating report for %s..." % report_date.isoformat())
    for report in reports:
        print report.run(report_date)

    log.info("PAT shutting down...")
