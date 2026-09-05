def analyze_device(device):
    """
    Calculate a simple, explainable NETGUARD
    security risk score for one device.
    """

    score = 0
    findings = []
    actions = []

    # ---------------------------------
    # Rogue device
    # ---------------------------------

    security_status = str(
        device.get("security_status", "")
    ).upper()

    if security_status == "ROGUE":

        score += 40

        findings.append(
            "Device is marked as rogue."
        )

        actions.append(
            "Verify that this device is authorized."
        )

    elif security_status != "TRUSTED":

        score += 15

        findings.append(
            "Device has not been explicitly trusted."
        )

        actions.append(
            "Verify the device and consider marking it trusted."
        )

    # ---------------------------------
    # Port findings
    # ---------------------------------

    ports = device.get("open_ports", [])

    high_ports = 0
    review_ports = 0

    for port in ports:

        risk = str(
            port.get("risk", "")
        ).upper()

        if risk == "HIGH":
            high_ports += 1

        elif risk == "REVIEW":
            review_ports += 1

    if high_ports:

        score += min(high_ports * 12, 36)

        findings.append(
            f"{high_ports} high-risk open port(s) detected."
        )

        actions.append(
            "Review and disable unnecessary high-risk services."
        )

    if review_ports:

        score += min(review_ports * 5, 15)

        findings.append(
            f"{review_ports} port(s) require security review."
        )

        actions.append(
            "Review services running on exposed ports."
        )

    # ---------------------------------
    # Existing security alerts
    # ---------------------------------

    if device.get("arp_spoofing"):

        score += 45

        findings.append(
            "Possible ARP spoofing activity detected."
        )

        actions.append(
            "Investigate the device and verify the network gateway."
        )

    # ---------------------------------
    # Limit score
    # ---------------------------------

    score = min(score, 100)

    # ---------------------------------
    # Risk level
    # ---------------------------------

    if score >= 80:

        level = "CRITICAL"

    elif score >= 60:

        level = "HIGH"

    elif score >= 30:

        level = "MEDIUM"

    else:

        level = "LOW"

    # ---------------------------------
    # Healthy device
    # ---------------------------------

    if not findings:

        findings.append(
            "No significant security findings detected."
        )

        actions.append(
            "Continue normal monitoring."
        )

    return {
        "score": score,
        "level": level,
        "findings": findings,
        "actions": actions
    }