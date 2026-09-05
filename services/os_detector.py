import nmap


class OSDetector:

    def detect(self, ip):

        scanner = nmap.PortScanner()

        try:

            scanner.scan(
                ip,
                arguments="-O"
            )

            if ip in scanner.all_hosts():

                matches = scanner[ip].get("osmatch", [])

                if matches:

                    return matches[0]["name"]

            return "Unknown"

        except Exception:

            return "Detection Failed"