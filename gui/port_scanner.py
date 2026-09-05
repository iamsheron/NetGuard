import socket


COMMON_PORTS = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    135: "MS RPC",
    139: "NetBIOS",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    587: "SMTP",
    993: "IMAPS",
    995: "POP3S",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    5900: "VNC",
    8080: "HTTP Proxy",
}


def scan_ports(ip, timeout=0.4):
    """
    Scan a selected local-network device for commonly used TCP ports.

    Returns:
        [
            {
                "port": 22,
                "service": "SSH",
                "state": "OPEN"
            }
        ]
    """

    results = []

    for port, service in COMMON_PORTS.items():

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        sock.settimeout(timeout)

        try:

            result = sock.connect_ex(
                (ip, port)
            )

            if result == 0:

                results.append({
                    "port": port,
                    "service": service,
                    "state": "OPEN"
                })

        except socket.error:
            pass

        finally:
            sock.close()

    return results

PORT_RISK = {
    21: ("FTP", "HIGH"),
    22: ("SSH", "REVIEW"),
    23: ("Telnet", "HIGH"),
    25: ("SMTP", "REVIEW"),
    53: ("DNS", "LOW"),
    80: ("HTTP", "REVIEW"),
    110: ("POP3", "HIGH"),
    135: ("MS RPC", "HIGH"),
    139: ("NetBIOS", "HIGH"),
    143: ("IMAP", "REVIEW"),
    443: ("HTTPS", "LOW"),
    445: ("SMB", "HIGH"),
    587: ("SMTP", "REVIEW"),
    993: ("IMAPS", "LOW"),
    995: ("POP3S", "LOW"),
    3306: ("MySQL", "HIGH"),
    3389: ("RDP", "HIGH"),
    5432: ("PostgreSQL", "HIGH"),
    5900: ("VNC", "HIGH"),
    8080: ("HTTP Proxy", "REVIEW"),
}


def get_port_risk(port):
    """
    Return the service and security-review level
    associated with a known port.
    """

    if port in PORT_RISK:
        service, risk = PORT_RISK[port]
        return service, risk

    return "Unknown", "REVIEW"