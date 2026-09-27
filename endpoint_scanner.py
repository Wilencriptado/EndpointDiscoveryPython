import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlsplit, urldefrag


def discover_endpoints(target_website):
    # Make sure the URL has a scheme
    if not target_website.startswith(("http://", "https://")):
        target_website = "https://" + target_website

    target_website = target_website.rstrip("/")
    target_host = urlsplit(target_website).hostname

    print(f"\n[*] Target: {target_website}")
    print("[*] Connecting to website...")

    try:
        with requests.Session() as session:
            session.headers.update({
                "User-Agent": "EndpointDiscoveryPython/1.0"
            })

            response = session.get(
                target_website,
                timeout=(5, 15)
            )

            response.raise_for_status()

    except requests.Timeout:
        print("[!] Request timed out.")
        return

    except requests.RequestException as error:
        print(f"[!] Request failed: {error}")
        return

    print(f"[+] Website retrieved successfully ({response.status_code})")
    print("[*] Analyzing HTML links...\n")

    soup = BeautifulSoup(response.text, "html.parser")
    endpoints = set()

    for link in soup.find_all("a", href=True):
        href = link["href"].strip()

        if not href:
            continue

        # Convert relative URLs into absolute URLs
        endpoint = urljoin(response.url, href)

        # Remove #fragments
        endpoint, _ = urldefrag(endpoint)

        parsed_endpoint = urlsplit(endpoint)

        # Only keep HTTP/HTTPS links
        if parsed_endpoint.scheme not in ("http", "https"):
            continue

        # Only keep endpoints belonging to the target host
        if parsed_endpoint.hostname != target_host:
            continue

        endpoints.add(endpoint)

    print("[*] Endpoint discovery complete.")
    print(f"[+] Discovered {len(endpoints)} endpoint(s):\n")

    for endpoint in sorted(endpoints):
        print(endpoint)


# Get target website
target_website = input("Enter the target website URL: ").strip()

# Start discovery
discover_endpoints(target_website)