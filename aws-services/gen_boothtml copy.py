import json
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

for entry in items:
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
    try:
        resp = requests.get(link, headers=headers, timeout=5)
        soup = BeautifulSoup(resp.text, "html.parser")

        scripts = soup.find_all("script", {"type": "application/json"})

        if scripts:
            raw = scripts[0].string.strip()
            parsed = json.loads(raw)

            # Just show partial preview
            extracted_json_preview = json.dumps(parsed)[:200]

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
    <small><b>Extracted JSON Preview:</b> {extracted_json_preview}</small>
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
