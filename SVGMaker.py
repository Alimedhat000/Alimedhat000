import xml.etree.ElementTree as ET
from typing import Dict


def create_svg(ascii_art_file: str,
               info: Dict[str, str],
               output_file: str = "profile.svg"):
    # Read ASCII art
    with open(ascii_art_file, 'r') as f:
        ascii_lines = f.readlines()

    # Create SVG root
    svg = ET.Element('svg')
    svg.set('xmlns', 'http://www.w3.org/2000/svg')
    svg.set('font-family', 'Andale Mono,AndaleMono,Consolas,monospace')
    svg.set('width', '1380px')
    svg.set('height', '690px')
    svg.set('font-size', '16px')

    # Add styles
    style = ET.SubElement(svg, 'style')
    style.text = """
        .keyColor {fill: #ffa657;}
        .valueColor {fill: #a5d6ff;}
        .ascii {fill: #c9d1d9;}
        text, tspan {white-space: pre;}
    """

    # Add background
    rect = ET.SubElement(svg, 'rect')
    rect.set('width', '1380px')
    rect.set('height', '690px')
    rect.set('fill', '#161b22')
    rect.set('rx', '15')

    # Add ASCII art
    ascii_text = ET.SubElement(svg, 'text')
    ascii_text.set('x', '15')
    ascii_text.set('y', '30')
    ascii_text.set('class', 'ascii')

    # Add each line of ASCII art
    for i, line in enumerate(ascii_lines):
        tspan = ET.SubElement(ascii_text, 'tspan')
        tspan.set('x', '15')
        tspan.set('y', str(30 + i * 20))
        tspan.text = line.rstrip()

    # Add info section
    info_text = ET.SubElement(svg, 'text')
    info_text.set('x', '750')
    info_text.set('y', '30')
    info_text.set('fill', '#c9d1d9')

    # Add info items
    y_pos = 30
    for key, value in info.items():
        tspan_key = ET.SubElement(info_text, 'tspan')
        tspan_key.set('x', '750')
        tspan_key.set('y', str(y_pos))
        tspan_key.set('class', 'keyColor')

        if value:
            tspan_key.text = f"{key}: "

            tspan_value = ET.SubElement(info_text, 'tspan')
            tspan_value.set('class', 'valueColor')
            tspan_value.text = value
        else:
            tspan_key.text = key

        y_pos += 20

    # Write to file
    tree = ET.ElementTree(svg)
    ET.register_namespace('', "http://www.w3.org/2000/svg")
    tree.write(output_file, encoding='utf-8', xml_declaration=True)


# Example usage
info = {
    'YourName@user': None,  # Username header
    '——————': None,  # Separator
    'OS': 'Windows 11, Linux',
    'Uptime': '25 years, 3 months, 15 days',
    'Host': 'University Name',
    'Kernel': 'Department Name',
    'IDE': 'VSCode, NeoVim',
    ' ': None,  # Empty line for spacing
    'Languages.Programming': 'Python, JavaScript, C++, Java',
    'Languages.Computer': 'HTML, CSS, JSON, Markdown',
    '  ': None,  # Empty line
    'Hobbies.Software': 'Web Development, Data Science',
    'Hobbies.Hardware': 'Arduino, Raspberry Pi',
    '   ': None,  # Empty line
    'Contact': None,  # Contact header
    '————': None,  # Separator
    'Email': 'your.email@domain.com',
    'LinkedIn': 'yourprofile',
    'Discord': 'yourdiscord',
    'LeetCode': 'yourhandle',
    '    ': None,  # Empty line
    'GitHub Stats': None,  # Stats header
    '—————': None,  # Separator
    'Repos': '30',
    'Commits': '500',
    'Lines of Code': 'Many, Many Lines'
}

create_svg('output.txt', info, 'profile.svg')
