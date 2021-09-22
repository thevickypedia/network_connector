from json import dumps
from os import environ
from re import sub

import objc

# noinspection PyUnresolvedReferences
objc.loadBundle('CoreWLAN',
                bundle_path='/System/Library/Frameworks/CoreWLAN.framework',
                module_globals=globals())

# noinspection PyUnresolvedReferences
interface = CWInterface.interface()
networks, error = interface.scanForNetworksWithName_error_(environ.get('ssid'), None)
if not networks:
    exit('No networks identified.')

network = networks.anyObject()
network_info = sub(r'<CWNetwork: \w+> ', '', str(network)).replace('[', '').replace(']', '')

ssid_info = {}
for element in network_info.split(', '):
    dictionary = element.split('=', 1)
    ssid_info.update({dictionary[0]: dictionary[1]})
print(dumps(ssid_info, indent=2))
