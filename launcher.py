import os
import re
import sys
import time
import json
import socket
import subprocess
import urllib.request
import urllib.parse
import urllib.error

from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

load_dotenv(
    os.path.join(
        BASE_DIR,
        ".env"
    )
)


# ============================================================
# NETGUARD AUTOMATIC LAUNCHER
# ============================================================

PYTHON_EXE = sys.executable

FLASK_SCRIPT = os.path.join(
    BASE_DIR,
    "telegram_server",
    "server.py"
)

MAIN_SCRIPT = os.path.join(
    BASE_DIR,
    "main.py"
)

CLOUDFLARED_EXE = (
    r"C:\Cloudflared\cloudflared.exe.exe"
)

LOCAL_SERVER = (
    "http://127.0.0.1:5050"
)

TUNNEL_CONFIG = os.path.join(
    BASE_DIR,
    "telegram_tunnel.json"
)


# ============================================================
# SETTINGS
# ============================================================

FLASK_TIMEOUT = 30

TUNNEL_DNS_TIMEOUT = 90

TUNNEL_CHECK_INTERVAL = 5

TELEGRAM_RETRIES = 12

TELEGRAM_RETRY_INTERVAL = 5

MAX_TUNNEL_ATTEMPTS = 5


# ============================================================
# PROCESSES
# ============================================================

flask_process = None
cloudflare_process = None
gui_process = None


# ============================================================
# UTILITY
# ============================================================

def print_header(title):

    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


# ============================================================
# START FLASK
# ============================================================

def start_flask():

    global flask_process

    print_header(
        "Starting NETGUARD Telegram server..."
    )

    if not os.path.exists(
        FLASK_SCRIPT
    ):

        print(
            "❌ Telegram server script not found:"
        )

        print(
            FLASK_SCRIPT
        )

        return False

    try:

        flask_process = subprocess.Popen(
            [
                PYTHON_EXE,
                FLASK_SCRIPT
            ],
            cwd=BASE_DIR
        )

        return True

    except Exception as error:

        print(
            "❌ Failed to start Telegram server:"
        )

        print(
            error
        )

        return False


# ============================================================
# WAIT FOR FLASK
# ============================================================

def wait_for_flask(
    timeout=FLASK_TIMEOUT
):

    print(
        "Waiting for Telegram server..."
    )

    start_time = time.time()

    while (
        time.time() - start_time
        < timeout
    ):

        # Detect early process failure.

        if (
            flask_process is not None
            and flask_process.poll()
            is not None
        ):

            print(
                "❌ Telegram server stopped unexpectedly."
            )

            return False

        try:

            with urllib.request.urlopen(
                LOCAL_SERVER,
                timeout=2
            ) as response:

                if response.status == 200:

                    print(
                        "Telegram server is ready."
                    )

                    return True

        except Exception:

            pass

        time.sleep(1)

    print(
        "❌ Telegram server did not become ready."
    )

    return False


# ============================================================
# STOP CLOUDFLARE
# ============================================================

def stop_cloudflare():

    global cloudflare_process

    if cloudflare_process is None:

        return

    try:

        if (
            cloudflare_process.poll()
            is None
        ):

            print(
                "Stopping Cloudflare tunnel..."
            )

            cloudflare_process.terminate()

            try:

                cloudflare_process.wait(
                    timeout=5
                )

            except subprocess.TimeoutExpired:

                cloudflare_process.kill()

    except Exception as error:

        print(
            "⚠ Could not stop Cloudflare:",
            error
        )

    finally:

        cloudflare_process = None


# ============================================================
# START CLOUDFLARE
# ============================================================

def start_cloudflare():

    global cloudflare_process

    print_header(
        "Starting Cloudflare Quick Tunnel..."
    )

    if not os.path.exists(
        CLOUDFLARED_EXE
    ):

        print(
            "❌ cloudflared executable not found:"
        )

        print(
            CLOUDFLARED_EXE
        )

        return None

    try:

        cloudflare_process = subprocess.Popen(
            [
                CLOUDFLARED_EXE,
                "tunnel",
                "--url",
                LOCAL_SERVER
            ],
            cwd=os.path.dirname(
                CLOUDFLARED_EXE
            ),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

    except Exception as error:

        print(
            "❌ Failed to start Cloudflare:"
        )

        print(
            error
        )

        return None

    pattern = re.compile(
        r"https://[a-zA-Z0-9-]+\.trycloudflare\.com"
    )

    start_time = time.time()

    while (
        time.time() - start_time
        < 60
    ):

        if (
            cloudflare_process.poll()
            is not None
        ):

            print(
                "❌ Cloudflare stopped unexpectedly."
            )

            return None

        line = (
            cloudflare_process.stdout.readline()
        )

        if not line:

            time.sleep(0.2)

            continue

        line = line.strip()

        print(
            "[Cloudflare]",
            line
        )

        match = pattern.search(
            line
        )

        if match:

            tunnel_url = (
                match.group(0)
                .rstrip("/")
            )

            print()

            print(
                "✅ Cloudflare tunnel detected:"
            )

            print(
                tunnel_url
            )

            return tunnel_url

    print(
        "❌ Cloudflare tunnel URL "
        "was not detected."
    )

    return None


# ============================================================
# PUBLIC DNS CHECK
#
# We use Cloudflare DNS-over-HTTPS instead of relying only
# on Windows/Python local DNS.
#
# This is important because Telegram uses public DNS too.
# ============================================================

def public_dns_resolves(
    hostname
):

    try:

        query = urllib.parse.urlencode(
            {
                "name": hostname,
                "type": "A"
            }
        )

        url = (
            "https://cloudflare-dns.com/dns-query?"
            + query
        )

        request = urllib.request.Request(
            url,
            headers={
                "Accept":
                "application/dns-json"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=10
        ) as response:

            data = json.loads(
                response.read().decode(
                    "utf-8"
                )
            )

        answers = data.get(
            "Answer",
            []
        )

        for answer in answers:

            if answer.get(
                "type"
            ) == 1:

                ip_address = answer.get(
                    "data"
                )

                if ip_address:

                    print(
                        f"✅ Public DNS resolved "
                        f"{hostname} → {ip_address}"
                    )

                    return True

        return False

    except Exception as error:

        print(
            "⚠ Public DNS check failed:",
            error
        )

        return False


# ============================================================
# LOCAL DNS CHECK
# ============================================================

def local_dns_resolves(
    hostname
):

    try:

        results = socket.getaddrinfo(
            hostname,
            443,
            type=socket.SOCK_STREAM
        )

        if results:

            print(
                f"✅ Local DNS resolved {hostname}"
            )

            return True

    except socket.gaierror:

        pass

    except Exception as error:

        print(
            "⚠ Local DNS check error:",
            error
        )

    return False


# ============================================================
# CHECK PUBLIC WEBHOOK
# ============================================================

def check_public_webhook(
    tunnel_url
):

    webhook_url = (
        tunnel_url.rstrip("/")
        + "/telegram/webhook"
    )

    try:

        request = urllib.request.Request(
            webhook_url,
            method="GET"
        )

        with urllib.request.urlopen(
            request,
            timeout=10
        ) as response:

            print(
                "✅ Public webhook reachable."
            )

            print(
                "HTTP status:",
                response.status
            )

            return True

    except urllib.error.HTTPError as error:

        # 405 is GOOD here.
        #
        # It means the request reached Flask,
        # but Flask rejected GET because the
        # webhook expects POST.

        if error.code == 405:

            print(
                "✅ Public webhook reached Flask."
            )

            print(
                "HTTP 405 is expected for GET."
            )

            return True

        print(
            f"⚠ Public webhook returned "
            f"HTTP {error.code}"
        )

        return False

    except Exception as error:

        print(
            "⚠ Public webhook is not reachable:",
            error
        )

        return False


# ============================================================
# WAIT FOR TUNNEL TO BECOME PUBLIC
# ============================================================

def wait_for_public_tunnel(
    tunnel_url,
    timeout=TUNNEL_DNS_TIMEOUT
):

    print_header(
        "Waiting for public Cloudflare tunnel..."
    )

    parsed = urllib.parse.urlparse(
        tunnel_url
    )

    hostname = parsed.hostname

    if not hostname:

        print(
            "❌ Invalid Cloudflare tunnel URL:"
        )

        print(
            tunnel_url
        )

        return False

    start_time = time.time()

    attempt = 0

    while (
        time.time() - start_time
        < timeout
    ):

        attempt += 1

        print()

        print(
            f"Tunnel readiness check "
            f"{attempt}..."
        )

        # ----------------------------------------------------
        # STEP 1: Public DNS
        # ----------------------------------------------------

        if not public_dns_resolves(
            hostname
        ):

            print(
                "⚠ Public DNS does not know "
                "this hostname yet."
            )

            print(
                "⏳ Waiting "
                f"{TUNNEL_CHECK_INTERVAL} seconds..."
            )

            time.sleep(
                TUNNEL_CHECK_INTERVAL
            )

            continue

        # ----------------------------------------------------
        # STEP 2: Local DNS
        # ----------------------------------------------------

        local_dns_resolves(
            hostname
        )

        # ----------------------------------------------------
        # STEP 3: Public HTTPS endpoint
        # ----------------------------------------------------

        if check_public_webhook(
            tunnel_url
        ):

            print()

            print(
                "✅ Cloudflare tunnel is "
                "publicly reachable."
            )

            return True

        print(
            "⚠ DNS exists but HTTPS endpoint "
            "is not ready yet."
        )

        print(
            "⏳ Waiting "
            f"{TUNNEL_CHECK_INTERVAL} seconds..."
        )

        time.sleep(
            TUNNEL_CHECK_INTERVAL
        )

    print()

    print(
        "❌ Cloudflare tunnel did not become "
        "publicly reachable."
    )

    return False


# ============================================================
# SAVE CURRENT TUNNEL URL
# ============================================================

def save_tunnel_url(
    tunnel_url
):

    tunnel_url = (
        tunnel_url.rstrip("/")
    )

    data = {

        "tunnel_url":
            tunnel_url,

        "webhook_url":
            tunnel_url
            + "/telegram/webhook"

    }

    try:

        with open(
            TUNNEL_CONFIG,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4
            )

        print(
            "✅ Current tunnel URL saved."
        )

        return True

    except Exception as error:

        print(
            "❌ Failed to save tunnel URL:"
        )

        print(
            error
        )

        return False


# ============================================================
# TELEGRAM WEBHOOK
# ============================================================

def set_telegram_webhook(
    tunnel_url
):

    print_header(
        "Updating Telegram webhook..."
    )

    token = os.getenv(
        "NETGUARD_TELEGRAM_TOKEN"
    )

    if not token:

        print(
            "❌ NETGUARD_TELEGRAM_TOKEN "
            "is not configured."
        )

        return False

    webhook_url = (
        tunnel_url.rstrip("/")
        + "/telegram/webhook"
    )

    print(
        "Public webhook URL:"
    )

    print(
        webhook_url
    )

    params = urllib.parse.urlencode(
        {
            "url": webhook_url
        }
    )

    telegram_url = (
        "https://api.telegram.org/"
        f"bot{token}/setWebhook?"
        f"{params}"
    )

    for attempt in range(
        1,
        TELEGRAM_RETRIES + 1
    ):

        print()

        print(
            f"Telegram webhook attempt "
            f"{attempt}/{TELEGRAM_RETRIES}..."
        )

        try:

            with urllib.request.urlopen(
                telegram_url,
                timeout=20
            ) as response:

                result = json.loads(
                    response.read().decode(
                        "utf-8"
                    )
                )

            if result.get(
                "ok"
            ):

                print()

                print(
                    "✅ Telegram webhook updated."
                )

                print(
                    webhook_url
                )

                return True

            description = result.get(
                "description",
                "Unknown Telegram error"
            )

            print(
                "⚠ Telegram rejected webhook:"
            )

            print(
                description
            )

        except urllib.error.HTTPError as error:

            print(
                f"⚠ Telegram HTTP error "
                f"{error.code}"
            )

            try:

                details = (
                    error.read()
                    .decode("utf-8")
                )

                print(
                    "Telegram response:",
                    details
                )

                # ------------------------------------------------
                # DNS failure
                #
                # We retry because Telegram's resolver may need
                # additional time to see the newly created tunnel.
                # ------------------------------------------------

                if (
                    "Failed to resolve host"
                    in details
                ):

                    print(
                        "⏳ Telegram cannot resolve "
                        "the tunnel yet."
                    )

                else:

                    # Other Telegram HTTP errors are not
                    # necessarily transient.

                    if attempt >= 3:

                        return False

            except Exception:

                pass

        except Exception as error:

            print(
                "⚠ Telegram webhook request failed:"
            )

            print(
                error
            )

        if attempt < TELEGRAM_RETRIES:

            print(
                "⏳ Waiting "
                f"{TELEGRAM_RETRY_INTERVAL} "
                "seconds before retry..."
            )

            time.sleep(
                TELEGRAM_RETRY_INTERVAL
            )

    print()

    print(
        "❌ Telegram webhook could not be updated."
    )

    return False


# ============================================================
# VERIFY WEBHOOK
# ============================================================

def verify_webhook():

    token = os.getenv(
        "NETGUARD_TELEGRAM_TOKEN"
    )

    if not token:

        return False

    url = (
        "https://api.telegram.org/"
        f"bot{token}/getWebhookInfo"
    )

    try:

        with urllib.request.urlopen(
            url,
            timeout=15
        ) as response:

            result = json.loads(
                response.read().decode(
                    "utf-8"
                )
            )

        if not result.get(
            "ok"
        ):

            print(
                "❌ Could not verify Telegram webhook."
            )

            return False

        webhook = (
            result
            .get("result", {})
            .get("url")
        )

        print()

        print(
            "✅ Telegram webhook verified:"
        )

        print(
            webhook
        )

        return True

    except urllib.error.HTTPError as error:

        print(
            "❌ Telegram webhook verification failed."
        )

        print(
            "HTTP status:",
            error.code
        )

        try:

            details = (
                error.read()
                .decode("utf-8")
            )

            print(
                "Telegram response:",
                details
            )

        except Exception:

            pass

        return False

    except Exception as error:

        print(
            "❌ Telegram webhook verification failed:"
        )

        print(
            error
        )

        return False


# ============================================================
# START GUI
# ============================================================

def start_gui():

    global gui_process

    print_header(
        "Starting NETGUARD GUI..."
    )

    if not os.path.exists(
        MAIN_SCRIPT
    ):

        print(
            "❌ NETGUARD main.py not found:"
        )

        print(
            MAIN_SCRIPT
        )

        return None

    try:

        gui_process = subprocess.Popen(
            [
                PYTHON_EXE,
                MAIN_SCRIPT
            ],
            cwd=BASE_DIR
        )

        return gui_process

    except Exception as error:

        print(
            "❌ Failed to start NETGUARD GUI:"
        )

        print(
            error
        )

        return None


# ============================================================
# STOP PROCESS
# ============================================================

def stop_process(
    process,
    name
):

    if process is None:

        return

    try:

        if process.poll() is None:

            print(
                f"Stopping {name}..."
            )

            process.terminate()

            try:

                process.wait(
                    timeout=5
                )

            except subprocess.TimeoutExpired:

                print(
                    f"⚠ {name} did not stop. "
                    "Forcing termination..."
                )

                process.kill()

                try:

                    process.wait(
                        timeout=3
                    )

                except Exception:

                    pass

    except Exception as error:

        print(
            f"⚠ Could not stop {name}:",
            error
        )


# ============================================================
# CLEANUP
# ============================================================

def cleanup():

    print()

    print(
        "Stopping NETGUARD background services..."
    )

    # GUI first

    stop_process(
        gui_process,
        "NETGUARD GUI"
    )

    # Cloudflare second

    stop_process(
        cloudflare_process,
        "Cloudflare tunnel"
    )

    # Flask last

    stop_process(
        flask_process,
        "Telegram server"
    )

    print(
        "✅ NETGUARD services stopped."
    )


# ============================================================
# CREATE A VALID TUNNEL
#
# This is the important recovery mechanism.
#
# If Cloudflare gives us a hostname that never becomes
# publicly resolvable, we throw that tunnel away and request
# another one.
# ============================================================

def create_working_tunnel():

    for tunnel_attempt in range(
        1,
        MAX_TUNNEL_ATTEMPTS + 1
    ):

        print()

        print(
            "=" * 60
        )

        print(
            "Cloudflare tunnel attempt "
            f"{tunnel_attempt}/{MAX_TUNNEL_ATTEMPTS}"
        )

        print(
            "=" * 60
        )

        # ----------------------------------------------------
        # Make sure previous tunnel is gone.
        # ----------------------------------------------------

        stop_cloudflare()

        # ----------------------------------------------------
        # Create a new Quick Tunnel.
        # ----------------------------------------------------

        tunnel_url = start_cloudflare()

        if not tunnel_url:

            print(
                "⚠ Could not obtain a Cloudflare URL."
            )

            continue

        # ----------------------------------------------------
        # Save it immediately so other NETGUARD components
        # can see the current URL.
        # ----------------------------------------------------

        save_tunnel_url(
            tunnel_url
        )

        # ----------------------------------------------------
        # Wait until public DNS + HTTPS work.
        # ----------------------------------------------------

        if not wait_for_public_tunnel(
            tunnel_url
        ):

            print()

            print(
                "⚠ This Quick Tunnel appears "
                "to be unusable."
            )

            print(
                "🔄 Discarding it and requesting "
                "a new Quick Tunnel..."
            )

            stop_cloudflare()

            time.sleep(2)

            continue

        # ----------------------------------------------------
        # Tunnel is publicly reachable.
        # ----------------------------------------------------

        print()

        print(
            "✅ Working Cloudflare tunnel found:"
        )

        print(
            tunnel_url
        )

        # ----------------------------------------------------
        # Telegram webhook
        # ----------------------------------------------------

        if set_telegram_webhook(
            tunnel_url
        ):

            # ------------------------------------------------
            # Verify Telegram
            # ------------------------------------------------

            if verify_webhook():

                print()

                print(
                    "✅ Cloudflare + Telegram "
                    "are fully configured."
                )

                return tunnel_url

            print(
                "⚠ Telegram webhook was set "
                "but verification failed."
            )

            # We can still try another tunnel.
            # This is safer than running with a
            # potentially stale webhook.

            stop_cloudflare()

            time.sleep(2)

            continue

        # ----------------------------------------------------
        # Telegram rejected the working tunnel.
        # ----------------------------------------------------

        print()

        print(
            "⚠ Telegram webhook registration failed."
        )

        print(
            "🔄 Trying a fresh Cloudflare tunnel..."
        )

        stop_cloudflare()

        time.sleep(2)

    print()

    print(
        "❌ NETGUARD could not create a "
        "working Telegram tunnel."
    )

    return None


# ============================================================
# MAIN
# ============================================================

def main():

    global gui_process

    print()

    print(
        "=" * 60
    )

    print(
        "       NETGUARD AUTOMATIC LAUNCHER"
    )

    print(
        "=" * 60
    )

    try:

        # ====================================================
        # 1. START FLASK
        # ====================================================

        if not start_flask():

            cleanup()

            return

        if not wait_for_flask():

            cleanup()

            return

        # ====================================================
        # 2. CREATE WORKING CLOUDFLARE + TELEGRAM SETUP
        # ====================================================

        tunnel_url = (
            create_working_tunnel()
        )

        if not tunnel_url:

            print()

            print(
                "⚠ NETGUARD cannot establish "
                "Telegram connectivity."
            )

            print(
                "⚠ NETGUARD will continue "
                "without Telegram notifications."
            )

        # ====================================================
        # 3. START GUI
        # ====================================================

        gui_process = start_gui()

        if gui_process is None:

            cleanup()

            return

        print()

        print(
            "=" * 60
        )

        print(
            "✅ NETGUARD IS FULLY RUNNING"
        )

        print(
            "=" * 60
        )

        print(
            "Flask:      ",
            LOCAL_SERVER
        )

        if tunnel_url:

            print(
                "Cloudflare: ",
                tunnel_url
            )

        else:

            print(
                "Cloudflare:  Not available"
            )

        print()

        # ====================================================
        # 4. KEEP LAUNCHER ALIVE
        # ====================================================

        gui_process.wait()

    except KeyboardInterrupt:

        print()

        print(
            "NETGUARD launcher stopped."
        )

    except Exception as error:

        print()

        print(
            "❌ NETGUARD launcher error:"
        )

        print(
            error
        )

    finally:

        cleanup()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()