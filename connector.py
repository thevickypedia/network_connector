from json import dumps
from os import environ
from re import sub
from subprocess import PIPE, Popen

import objc


def get_ssid() -> str:
    process = Popen(
        ['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-I'],
        stdout=PIPE)
    out, err = process.communicate()
    if error := process.returncode:
        exit(f"Failed to fetch SSID with exit code: {error}\n{err}")
    # noinspection PyTypeChecker
    return dict(map(str.strip, info.split(': ')) for info in out.decode('utf-8').split('\n')[:-1]).get('SSID')


def class_to_string_to_list_to_dict(network):
    network_info = sub(r'<CWNetwork: \w+> ', '', str(network)).replace('[', '').replace(']', '')
    ssid_info = {}
    for element in network_info.split(', '):
        dictionary = element.split('=', 1)
        ssid_info.update({dictionary[0]: dictionary[1]})
    return ssid_info


def connector(ssid, password):
    # noinspection PyUnresolvedReferences
    objc.loadBundle('CoreWLAN',
                    bundle_path='/System/Library/Frameworks/CoreWLAN.framework',
                    module_globals=globals())

    # noinspection PyUnresolvedReferences
    interface = CWInterface.interface()
    networks, error = interface.scanForNetworksWithName_error_(ssid, None)
    if not networks:
        print(f'Failed to detect the SSID: {ssid}')
        print(error) if error else None
        return

    network = networks.anyObject()
    extracted = class_to_string_to_list_to_dict(network=network)
    value = sub(r'<CWChannel: \w+> ', '', str(extracted.get('channel'))).split('=')
    extracted.pop('channel')
    extracted.update({value[0]: value[1]})
    print(dumps(extracted, indent=2))

    success, error = interface.associateToNetwork_password_error_(network, password, None)
    if success:
        print(f'Connected to {get_ssid()}')
    if error:
        print(f'Unable to connect to {ssid}')
        print(error)


if __name__ == '__main__':
    connector(ssid=environ.get('ssid'), password=environ.get('password'))
