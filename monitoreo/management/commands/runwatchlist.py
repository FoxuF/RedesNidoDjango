from django.core.management import BaseCommand

from monitoreo.models import WatchList
from monitoreo.tasks import run_watchlist


class Command(BaseCommand):
    help = 'run the specified watchlists'

    def add_arguments(self, parser):
        parser.add_argument(
            'watchlist',
            nargs='?',
            help='name of the watchlist to run (omit for all)',
        )

    def handle(self, *args, **options):
        if options['watchlist']:
            watchlist = WatchList.objects.get(name=options['watchlist'])
            run_watchlist(watchlist.pk)
        else:
            for watchlist in WatchList.objects.all(): run_watchlist(watchlist.pk)
