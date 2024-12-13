import requests
import xml.etree.ElementTree as ET
import re


class SVGParser:
    def __init__(self):
        self.namespace = {"svg": "http://www.w3.org/2000/svg"}

    def fetch_svg(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching SVG: {e}")
            return None

    def parse_svg(self, svg_content):
        try:
            root = ET.fromstring(svg_content)

            data_index = {
                6: "Total Stars",
                7: "Commits",
                8: "Total PRs",
                9: "Total Issues",
                10: "Contributions",
            }
            parsed_data = {}

            text_elements = root.findall(".//svg:text", self.namespace)
            for i, text_element in enumerate(text_elements):
                content = text_element.text.strip() if text_element.text else ""

                # Collect all numbers in the SVG, skipping the first
                if i > 2:
                    number_match = re.search(r"\d+", content)
                    if number_match:
                        parsed_data[data_index[i]] = int(number_match.group())
            return parsed_data

        except ET.ParseError as e:
            print(f"Error parsing SVG: {e}")
            return None


# Example Usage
if __name__ == "__main__":
    parser = SVGParser()
    url = 'https://github-profile-summary-cards.vercel.app/api/cards/stats?username=Alimedhat000'

    svg_content = parser.fetch_svg(url)
    if svg_content:
        parsed_data = parser.parse_svg(svg_content)
        print(parsed_data)
