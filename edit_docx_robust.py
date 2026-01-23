#!/usr/bin/env python3
"""
Robust script to edit .docx files by working with concatenated text
"""
import zipfile
import os
import shutil
import xml.etree.ElementTree as ET
import re

def edit_docx_robust(input_file, output_file, replacements):
    """
    Edit a .docx file by finding and replacing text, handling XML formatting

    Args:
        input_file: Path to input .docx file
        output_file: Path to output .docx file
        replacements: List of tuples (old_pattern, new_text, is_regex)
    """
    temp_dir = input_file.replace('.docx', '_temp_robust')
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

    # Extract the .docx file
    with zipfile.ZipFile(input_file, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    # Parse the document.xml
    doc_xml_path = os.path.join(temp_dir, 'word', 'document.xml')

    # Register namespace
    ET.register_namespace('w', 'http://schemas.openxmlformats.org/wordprocessingml/2006/main')
    ET.register_namespace('r', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships')
    ET.register_namespace('wp', 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing')

    # Read as raw text for regex replacement
    with open(doc_xml_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Apply each replacement
    for old_pattern, new_text, use_regex in replacements:
        if use_regex:
            content = re.sub(old_pattern, new_text, content, flags=re.DOTALL)
        else:
            # For non-regex, escape XML and try direct replacement
            content = content.replace(old_pattern, new_text)

    # Write back
    with open(doc_xml_path, 'w', encoding='utf-8') as f:
        f.write(content)

    # Repackage as .docx
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zip_out:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = file_path[len(temp_dir):].lstrip(os.sep).lstrip('/')
                zip_out.write(file_path, arcname)

    # Clean up
    shutil.rmtree(temp_dir)
    print(f"Successfully created {output_file}")


# EPF 3.4 replacements - using regex patterns to handle XML formatting
epf34_replacements = [
    # Requirement 3 - match with flexible whitespace
    (
        r'Mr\. Chris HUGHES had a Senior Analyst role at the British Army DCSU \(Defence Cultural Specialist Unit\) as senior OF2 including acting OF3 responsibilities from 2016 to 2019\.(\s|</w:t>|<w:t[^>]*>)*In addition, he had 1 year at Defence Intelligence as senior OF2 in Collection Management\.',

        'Mr. Chris HUGHES has over 4 years of OF3-level experience in Senior Analyst and operational intelligence roles supporting formations equivalent to 2-star HQ and higher:\n\n'
        'Senior Analyst positions (4 years total):\n'
        '• Political Advisor for Latin America / Lead Human Terrain Analyst, British Army (Apr 2017 - Dec 2019): Senior Analyst role at Defence Cultural Specialist Unit (DCSU), subordinate to 77th Brigade (Information Operations Brigade). Led team of analysts providing cultural and human terrain intelligence to support strategic decision-making at 2-star level and above. Acted at OF3 level advising senior commanders on political-military affairs across Latin America. Contributed to high-profile multinational operations including HMS Protector South Atlantic mission supporting search for missing Argentine submarine, establishing liaison between Royal Navy and Argentine Navy.\n\n'
        '• Collection Manager (Russia Team Lead), UK Defence Intelligence (Feb 2021 - Apr 2022): Senior OF2 Collection Manager working at strategic level, managing intelligence requirements for senior government customers. Led Russia-focused team of 25 analysts during Ukraine invasion, translating strategic requirements into collection tasks. Reported to senior Defence Intelligence leadership equivalent to 2-star+ level.\n\n'
        'Equivalent to Senior Case Officer/Analyst roles within national Military Intelligence Agency (Defence Intelligence) and strategic formation (77th Brigade) supporting 2-star and higher command.',

        True  # Use regex
    ),

    # Requirement 5 - match with flexible whitespace
    (
        r'Mr\. Chris HUGHES is UK MOD Joint Information Operations Course qualified\.(\s|</w:t>|<w:t[^>]*>)*He has conducted Collection Requirements for counter hybrid threat operations at UK Defence Intelligence\.(\s|</w:t>|<w:t[^>]*>)*Visiting Research Fellowship, University of Oxford on Information Operations\.(\s|</w:t>|<w:t[^>]*>)*He has conducted a Grey Zone study whilst at the Defence Cultural Specialist Unit as part of the unit.s subordination to 77X \(Information Operations Brigade\)',

        'Mr. Chris HUGHES has extensive operational and academic experience in hybrid threats at strategic and operational levels:\n\n'
        'Operational experience with hybrid threats:\n'
        '• Collection Manager, UK Defence Intelligence (2021-2022): Managed intelligence collection requirements for counter-hybrid threat operations during the Russian invasion of Ukraine. Led Russia-focused team translating strategic intelligence requirements into collection tasks against adversary employing full spectrum of hybrid warfare tactics (conventional military, cyber, information operations, political warfare).\n\n'
        '• Op SCORPIUS (2022): Provided intelligence support to UK assistance to Ukraine during active hybrid warfare environment, managing requirements and supporting UKSF operations.\n\n'
        '• Political Advisor for Latin America / DCSU (2017-2019): Conducted Grey Zone conflict analysis as part of Defence Cultural Specialist Unit\'s subordination to 77th Brigade (UK Information Operations Brigade). Analyzed state and non-state hybrid threats across Latin America including Venezuelan information operations and regional destabilization.\n\n'
        'Academic research on hybrid threats:\n'
        '• Visiting Research Fellow, University of Oxford, Changing Character of War Centre (Jan-Sept 2021): Independent research into state-run information operations in Venezuela, analyzing technologically-enabled media manipulation, social media analytics, and hybrid tactics employed in grey zone conflict.\n\n'
        'Formal qualification:\n'
        '• UK MOD Joint Information Operations Course qualified\n\n'
        'Working knowledge spans: disinformation campaigns, grey zone operations, political warfare, cyber-enabled operations, and integration of conventional and unconventional tactics at operational and strategic levels.',

        True  # Use regex
    )
]

# EPF 7.3 replacement - using regex pattern
epf73_replacements = [
    # Requirement 2
    (
        r'Mr\. Chris HUGHES has significant experience of working at the senior levels\.(\s|</w:t>|<w:t[^>]*>)*He has engaged in 3 x Ex WARFIGHTER as SME support to Cdr, briefing 2\* level and conducting liaison with US Army \(2015, 2017, 2019\)(\s|</w:t>|<w:t[^>]*>)*In addition he has 14 years experience as a commissioned officer in the British Army working in Intelligence, ISR, Info Ops and Human Terrain analysis\. 11 regular and 4 reserve\.',

        'Mr. Chris HUGHES has over 7 years of experience working at senior levels within the last 10 years, including:\n\n'
        'Direct engagement with 2-star (OF7) and senior command levels:\n'
        '• Provided SME support and briefed 2-star commanders at 3 x Ex WARFIGHTER exercises (2015, 2017, 2019 - US Corps Level training events)\n'
        '• Currently serves as Major (OF3) in Joint CIMIC Group, Army Special Operations Brigade, advising on Human Security and Gender issues at operational level\n'
        '• Oct 2025: JISR Collection Manager at NATO exercise STEADFAST DUEL 2025 (STDU25) at Joint Warfare Centre, Stavanger\n\n'
        'Senior analytical and advisory positions (2017-2022):\n'
        '• Political Advisor for Latin America, British Army (2017-2019): Advised senior commanders on political-military affairs, represented UK in defence diplomacy, led human terrain analysis team\n'
        '• Collection Manager (Russia Team Lead), UK Defence Intelligence (2021-2022): Led 25-person team during Ukraine invasion, reported directly to senior intelligence leadership\n'
        '• Operations Manager, 32 Regiment Royal Artillery (2012-2015): Directed 30+ multinational ISR teams, briefed senior commanders in high-pressure operational environment in Afghanistan\n\n'
        'Total: 14 years as commissioned officer (11 regular + 4 reserve), with sustained engagement at operational and strategic levels throughout career.',

        True  # Use regex
    )
]

if __name__ == "__main__":
    base_dir = "/Users/chris/Documents/Claude"

    # Edit EPF 3.4
    input_34 = os.path.join(base_dir, "EPF 3.4_HUGHES_Jan26.docx")
    if os.path.exists(input_34):
        print(f"Editing {input_34}...")
        edit_docx_robust(input_34, input_34, epf34_replacements)
    else:
        print(f"File not found: {input_34}")

    # Edit EPF 7.3
    input_73 = os.path.join(base_dir, "EPF 7.3_HUGHES_Jan26.docx")
    if os.path.exists(input_73):
        print(f"Editing {input_73}...")
        edit_docx_robust(input_73, input_73, epf73_replacements)
    else:
        print(f"File not found: {input_73}")

    print("\nAll edits complete!")
