from getch import _Getch
from plugin import PluginMount, PluginProvider
from datetime import date, timedelta

class Menu(object):
    """docstring for Menu"""
    def __init__(self, log, config):
        super(Menu, self).__init__()
        self.log = log
        self.config = config
        self.getch = _Getch()

        # Load plugins
        self.log.info("Importing plugins...")
        from plugins import trelloplug
        self.log.info("Loading plugins...")
        self.plugins = [p(log, config) for p in PluginProvider.plugins]

    def display(self):
        running = True
        while running:
            print "Main Menu"
            print "---------"
            print "(R)eport"
            print "(Q)uit"

            print "> ",
            selection = self.getch().lower()

            if selection == "r":
                report_date = date.today() - timedelta(days=0)
                self.log.info("Generating report for %s..." % report_date.isoformat())
                for plugin in self.plugins:
                    print plugin.report(report_date)

            if selection == "q":
                running = False
