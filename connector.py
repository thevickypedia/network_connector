import objc

# noinspection PyUnresolvedReferences
objc.loadBundle('CoreWLAN',
                bundle_path='/System/Library/Frameworks/CoreWLAN.framework',
                module_globals=globals())

# noinspection PyUnresolvedReferences
interface = CWInterface.interface()
networks, error = interface.scanForNetworksWithName_error_(None, None)
if networks:
    print(networks)
