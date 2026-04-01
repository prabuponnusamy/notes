import json
from wsgiref import headers
import requests
from bs4 import BeautifulSoup


INPUT_FILE = "/Users/prabu/Documents/Dev/Git/cluade/aws-services/aws_services.json"
OUTPUT_FILE = "/Users/prabu/Documents/Dev/Git/cluade/aws-services/aws_table.html"

# Load JSON
with open(INPUT_FILE, "r") as f:
    data = json.load(f)

items = data.get("items", [])

rows = []
categories = set()

for entry in items:  # Limit to first 10 for testing
    item = entry.get("item", {})
    fields = item.get("additionalFields", {})
    tags = entry.get("tags", [])

    title = fields.get("title", "No Title")
    body = fields.get("body", "")
    category = fields.get("badge", "")
    link = fields.get("ctaLink", "#")
    # {"id": "GLOBAL#local-tags-series#aws-reinvent"}
    # read the id from tags and extract last two parts to get category
    categoriesArr = []
    for tag in tags:
        parts = tag["id"].split("#")
        if len(parts) >= 3:
            cat = parts[1] + ": " + parts[2].replace("-", " ").title()
            categoriesArr.append(cat)

    categories.add(category)

     # 🔥 Fetch ctaLink content (limit to avoid too many requests)
    extracted_json_preview = ""
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(link, headers=headers, timeout=5)
        soup = BeautifulSoup(resp.text, "html.parser")

        # find the content inside the tag <main> then extract all <script> tags with type="application/json"
        main_content = soup.find("main")
        scripts = main_content.find_all("script", {"type": "application/json"}) if main_content else []

        for script in scripts:
            raw = script.string.strip()
            parsed = json.loads(raw)

            # read data.items[].fields.(itemHeading, itemLongLoc, heading, subheading, body) if exists and add to preview
            # {"data":{"items":[{"fields":{"id":"ams#c1","itemHeading":"Introduction to AWS AppFabric","itemBoolean":"false","itemLongLoc":"<p>AWS AppFabric quickly connects software as a service (SaaS) applications across your organization. IT and security teams can then easily manage and secure applications using a standard schema. Use AWS AppFabric to natively connect SaaS productivity and security applications to each other and automatically normalize application data for administrators to set common policies.<br></p>","itemOption":"right"},"metadata":{"tags":[]}}]},"metadata":{"auth":{},"testAttributes":{}},"context":{"page":{"pageUrl":"https://aws.amazon.com/appfabric/"},"contentType":"page","environment":{"stage":"prod","region":"us-west-2"},"sdkVersion":"2.0.26"},"refMap":{"manifest.js":"84d224634a","rt-text-media-collection.js":"2960de332d","rt-text-media-collection.css":"3d7fceab9d","rt-text-media-collection.css.js":"f66482cb7c","rt-text-media-collection.rtl.css":"e19d2dc6d2","rt-text-media-collection.rtl.css.js":"5481fb8bdf"},"settings":{"templateMappings":{"hyperlinkText":"itemCTALabel","hyperlinkUrl":"itemCTAURL","heading":"itemHeading","dark":"itemBoolean","videoOverlayDark":"itemBoolean","mediaAltText":"itemMediaAltText","mediaPosition":"itemOption","mediaUrl":"itemMediaURL","subheader":"itemTextLoc","bodyContent":"itemLongLoc","videoThumbnailUrl":"itemMediaURL2","videoOverlayTitle":"itemMediaAltText2","videoPlayButtonText":"itemTextLoc2"}}}
            def extract_fields(obj):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        if k in ["itemHeading", "itemLongLoc", "heading", "subheading", "body"]:
                            # trim the value if it's a string and return and remove double quotes from first and last character if exists
                            if isinstance(v, str):
                                return  v.replace('"', '').strip()
                            return v.replace('"', '').strip()
                        else:
                            res = extract_fields(v)
                            if res:
                                return res
                elif isinstance(obj, list):
                    for i in obj:
                        res = extract_fields(i)
                        if res:
                            return res
                return ""
            
            # Delete field metadata, breadcrumbs, settings, and other non-essential info to keep it concise at any level
            def clean_json(obj):
                if isinstance(obj, dict):
                    return {k: clean_json(v) for k, v in obj.items() if k not in ["metadata", "breadcrumbs", "settings", "config", "props"]}
                elif isinstance(obj, list):
                    return [clean_json(i) for i in obj]
                else:
                    return obj

            # Just show partial preview
            #extracted_json_preview = extracted_json_preview + "<br/>" + json.dumps(extract_fields(clean_json(parsed)))
            extracted = extract_fields(clean_json(parsed))
            # Convert to single line 
            extracted = extracted.replace("\n", " ").replace("\r", " ").strip()
            # If extracted is not empty, add to preview
            if extracted and extracted != "":
                extracted_json_preview = extracted_json_preview + extracted
            

    except Exception as e:
        extracted_json_preview = "Failed to fetch - " + str(e) + " for URL: " + link


    rows.append((title, body, link, category, extracted_json_preview))

# Sort categories
categories = sorted(categories)

# HTML
html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>AWS Products Table</title>

<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

<style>
body {{
    padding: 20px;
}}
</style>

<script>
function filterCategory() {{
    let selected = document.getElementById("categoryFilter").value.toLowerCase();
    let rows = document.querySelectorAll("#awsTable tbody tr");

    rows.forEach(row => {{
        let category = row.getAttribute("data-category").toLowerCase();
        if (selected === "all" || category.includes(selected)) {{
            row.style.display = "";
        }} else {{
            row.style.display = "none";
        }}
    }});
}}

function searchTable() {{
    let input = document.getElementById("search").value.toLowerCase();
    let rows = document.querySelectorAll("#awsTable tbody tr");

    rows.forEach(row => {{
        let text = row.innerText.toLowerCase();
        row.style.display = text.includes(input) ? "" : "none";
    }});
}}
</script>

</head>

<body>

<h2 class="mb-4">AWS Products</h2>

<div class="row mb-3">
    <div class="col-md-4">
        <input type="text" id="search" class="form-control" placeholder="Search..." onkeyup="searchTable()">
    </div>

    <div class="col-md-4">
        <select id="categoryFilter" class="form-select" onchange="filterCategory()">
            <option value="all">All Categories</option>
"""

# Add category options
for cat in categories:
    html += f'<option value="{cat}">{cat}</option>'

html += """
        </select>
    </div>
</div>

<table id="awsTable" class="table table-bordered table-striped table-hover">
<thead class="table-dark">
<tr>
<th>Service</th>
<th>Description</th>
<th>Category</th>
<th>Link</th>
</tr>
</thead>
<tbody>
"""

# Add rows
# print categoies in bullet points
for title, body, link, category, extracted_json_preview in rows:
    html += f"""
<tr data-category="{category}">
<td><strong>{title}</strong></td>
<td>
    {body}
    <ul class="list-unstyled" style="font-size: 11px; margin-top: 10px; background: #f8f9fa; padding: 5px; border-radius: 5px;">
        {"".join(f"<li style='margin: 2px 0;'>{tag}</li>" for tag in categoriesArr)}
    </ul>
    <small>{extracted_json_preview}</small>
</td>
<td><span class="badge bg-primary">{category}</span></td>
<td><a href="{link}" target="_blank" class="btn btn-sm btn-outline-primary">Open</a></td>
</tr>
"""

html += """
</tbody>
</table>

</body>
</html>
"""

# Write file
with open(OUTPUT_FILE, "w") as f:
    f.write(html)

print(f"✅ Bootstrap table generated: {OUTPUT_FILE}")


# data-rg-n TitleText
# data-rg-n BodyText
# data-rg-n HeadingText
# data-rg-n SubheadingText
