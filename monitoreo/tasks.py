import concurrent.futures
import os
import textwrap
from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from django.core.mail import send_mass_mail
from django.utils import timezone
from ping3 import ping

from monitoreo.models import WatchList
from todos_los_nodos.models import AP


def ping_and_update(ipDeviceObj, now):
    isAlive = ping(ipDeviceObj.ip)
    if isAlive is not None:
        ipDeviceObj.alive = True
        ipDeviceObj.lastAlive = now
    else:
        ipDeviceObj.alive = False
        # send report
    ipDeviceObj.save()


def run_watchlist(watchlist_pk):
    date = timezone.now()
    watchlist = WatchList.objects.get(pk=watchlist_pk)
    workers = os.cpu_count() + 4
    devices_all = watchlist.devices.all()
    with ThreadPoolExecutor(workers) as executor:
        futures_to_ping = {executor.submit(ping_and_update, status, date): status for status in devices_all}
        # build error mail tuples
        datatuple = []
        for future in concurrent.futures.as_completed(futures_to_ping):
            ipDevice = futures_to_ping[future]
            if not ipDevice.alive:
                message = f'''\
                {ipDevice.name} ({ipDevice.ip}) no responde.'''
                if isinstance(ipDevice, AP) and ipDevice.nodo:
                    # ugly indent but it works
                    message += f'''
                 Switch: {ipDevice.nodo.switch}
                 Puerto: {ipDevice.nodo.switch.tipo.capitalize()} {ipDevice.nodo.port}
                 Nodo:   {ipDevice.nodo}'''
                message += f'''
                 Descripcion: {ipDevice.notas}
                 LastAlive: {ipDevice.lastAlive}
                '''
                message = textwrap.dedent(message)
                datatuple.append(
                    (f"{ipDevice.name} no responde",
                     message,
                     settings.DEFAULT_FROM_EMAIL,
                     [str(subscriber) for subscriber in watchlist.subscribers.all()])
                )
        send_mass_mail(datatuple, fail_silently=True)
    # done
