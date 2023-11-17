
import requests
import xml.etree.ElementTree as ET
import re

def bnakaran_sitemap_apartments():

    # URL of the sitemap
    sitemap_url = "https://www.bnakaran.com/en/sitemap.xml"

    # Initialize an empty list to store the filtered URLs
    filtered_urls = []

    try:
        # Fetch the sitemap
        response = requests.get(sitemap_url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the XML
            root = ET.fromstring(response.content)

            # Regex pattern to match URLs ending with -d<number>
            pattern = re.compile(r".*-d\d+$")

            # Extract URLs matching the pattern
            filtered_urls = [elem.text for elem in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
                            if pattern.match(elem.text)]

    except Exception as e:
        error_message = str(e)
        
    ap_links = [link for link in filtered_urls if "apartment" in link]
    return ap_links