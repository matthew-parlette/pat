from plugin import PluginProvider
import trello

class Trello(PluginProvider):
    """docstring for Trello"""
    def __init__(self, log, config):
        super(Trello, self).__init__(log, config)
        self.log.info("Initializing Trello client...")

        # Gather the oauth tokens if they weren't provided
        if config['trello']['oauth_token'] == "":
            # Need to get the trello oauth_token and oauth_token_secret
            log.debug("Retrieving Trello oauth token...")
            os.environ["TRELLO_API_KEY"] = config["trello"]["key"]
            os.environ["TRELLO_API_SECRET"] = config["trello"]["secret"]
            os.environ["TRELLO_EXPIRATION"] = 'never'
            trello.util.create_oauth_token()

        # Establish the Trello client connection
        self.api = trello.TrelloClient(
            self.config['trello']['key'],
            self.config['trello']['secret'],
            self.config['trello']['oauth_token'],
            self.config['trello']['oauth_token_secret']
        )
        self.log.info("Trello client initialized")

    def report(self,date):
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
