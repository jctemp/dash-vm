from netifaces import interfaces, ifaddresses, AF_INET


def addresses() -> list:
    """
    Finds the IP address of the current machine.
    @return list of tuples (name, ip)
    """

    address_list = []
    for iface in interfaces():
        if iface == "lo":
            continue
        if AF_INET in ifaddresses(iface):
            address_list.append((iface, ifaddresses(iface)[AF_INET][0]['addr']))

    return address_list
