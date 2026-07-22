import csv
import os

# Define the stories
stories = [
    {
        "Issue Type": "Story",
        "Summary": "Gather Hydrology & Climate Data",
        "Description": (
            "**As** a hydropower analyst,\n"
            "**I want** accurate long-term flow and climate data from the Kamala Basin,\n"
            "**So that** we can estimate available energy and optimize design.\n\n"
            "**Acceptance Criteria:**\n"
            "- Daily/monthly discharge data for past 10–20 years\n"
            "- Rainfall, temperature, sediment data collected\n"
            "- Flow duration curve (FDC) created\n"
            "- Extreme flow events identified\n\n"
            "**Tasks:**\n"
            "- Fetch data from DHM, WECS, NEA\n"
            "- Use satellite rainfall/snowmelt\n"
            "- Review GLOF/flood hazard maps\n"
            "- Build FDC using HEC-HMS or SWAT"
        ),
        "Sprint": "Sprint 1",
        "Epic Link": "EPIC-KP-01",
        "Priority": "High"
    },
    {
        "Issue Type": "Story",
        "Summary": "Topographic Mapping & Head-Site Identification",
        "Description": (
            "**As** a project engineer,\n"
            "**I want** to identify viable hydropower sites with sufficient head,\n"
            "**So that** we can propose ROR or low-head schemes accurately.\n\n"
            "**Acceptance Criteria:**\n"
            "- High-res DEM (≤10 m) processed\n"
            "- Identify zones with >50 m drop\n"
            "- Shortlist 3 potential head sites\n"
            "- Overlay land-use and infrastructure\n\n"
            "**Tasks:**\n"
            "- Obtain DEM/topo maps\n"
            "- Run slope analysis in QGIS\n"
            "- Overlay roads, grid lines\n"
            "- Check conservation areas"
        ),
        "Sprint": "Sprint 2",
        "Epic Link": "EPIC-KP-01",
        "Priority": "High"
    },
    {
        "Issue Type": "Story",
        "Summary": "Site Reconnaissance & Stakeholder Engagement",
        "Description": (
            "**As** a field planner,\n"
            "**I want** to validate shortlisted sites and engage stakeholders,\n"
            "**So that** social and environmental issues are identified early.\n\n"
            "**Acceptance Criteria:**\n"
            "- Ground-truthing of 3 sites\n"
            "- Stakeholder meetings held\n"
            "- Risk register created\n"
            "- Photo log of access/terrain\n\n"
            "**Tasks:**\n"
            "- Field survey team dispatched\n"
            "- Prepare engagement schedule\n"
            "- Coordinate with local bodies\n"
            "- Upload findings to GIS platform"
        ),
        "Sprint": "Sprint 3",
        "Epic Link": "EPIC-KP-01",
        "Priority": "Medium"
    }
]

# File path
file_path = "/mnt/data/Kamala_Hydro_Stories.csv"

# Fieldnames for CSV
fieldnames = ["Issue Type", "Summary", "Description", "Sprint", "Epic Link", "Priority"]

# Write to CSV
with open(file_path, mode='w', newline='', encoding='utf-8') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for story in stories:
        writer.writerow(story)

file_path
