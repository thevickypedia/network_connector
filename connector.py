import logging
from importlib import reload
from json import dump
from os import environ, path
from re import sub
from subprocess import PIPE, Popen

import objc
from dotenv import load_dotenv

reload(logging)
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(module)s:%(lineno)d] - %(funcName)s - %(message)s',
    datefmt='%b-%d-%Y %I:%M:%S %p'
)

if path.isfile('.env'):
    load_dotenv(dotenv_path='.env', verbose=True, override=True)

logger = logging.getLogger(__name__)


def get_ssid() -> str or None:
    """Gets SSID of the network connected.

    Returns:
        str or None:
        WiFi or Ethernet SSID.
    """
    process = Popen(
        ['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-I'],
        stdout=PIPE)
    out, err = process.communicate()
    if error := process.returncode:
        logger.error(f"Failed to fetch SSID with exit code: {error}\n{err}")
        return
    # noinspection PyTypeChecker
    return dict(map(str.strip, info.split(': ')) for info in out.decode('utf-8').split('\n')[:-1]).get('SSID')


def class_to_string_to_list_to_dict(network: classmethod) -> dict:
    """Converts the class ``objective-c class CWNetwork`` to a dictionary object.

    Args:
        network: Takes the class object type ``objective-c`` as an argument.

    Returns:
        dict:
        A dictionary object of information about the SSID.
    """
    network_info = sub(r'<CWNetwork: \w+> ', '', str(network)).replace('[', '').replace(']', '')
    ssid_info = {}
    for element in network_info.split(', '):
        dictionary = element.split('=', 1)
        ssid_info.update({dictionary[0]: dictionary[1]})
    return ssid_info


def connector(ssid: str, password: str) -> None:
    """Connects to the given SSID for WiFi connection.

    Args:
        ssid: Wifi access point name.
        password: Password to connect to the SSID.
    """
    logger.info(f'Scanning for {ssid} in WiFi range')
    # noinspection PyUnresolvedReferences
    objc.loadBundle('CoreWLAN',
                    bundle_path='/System/Library/Frameworks/CoreWLAN.framework',
                    module_globals=globals())

    # noinspection PyUnresolvedReferences
    interface = CWInterface.interface()
    networks, error = interface.scanForNetworksWithName_error_(ssid, None)
    if not networks:
        logger.error(f'Failed to detect the SSID: {ssid}')
        logger.error(error) if error else None
        return

    network = networks.anyObject()
    extracted = class_to_string_to_list_to_dict(network=network)
    value = sub(r'<CWChannel: \w+> ', '', str(extracted.get('channel'))).split('=')
    extracted.pop('channel')
    extracted.update({value[0]: value[1]})
    with open(f'{ssid}.json', 'w') as file:
        dump(extracted, file, indent=2)

    success, error = interface.associateToNetwork_password_error_(network, password, None)
    if success:
        logger.info(f'Connected to {get_ssid() or ssid}')
    elif error:
        logger.error(f'Unable to connect to {ssid}')
        logger.error(error)


if __name__ == '__main__':
    connector(ssid=environ.get('ssid'), password=environ.get('password'))
