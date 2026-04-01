import json

# Input / Output files
INPUT_FILE = "/Users/prabu/Documents/Dev/Git/cluade/aws-services/aws_services.json"
OUTPUT_FILE = "/Users/prabu/Documents/Dev/Git/cluade/aws-services/aws_tiles.html"

# Load JSON
with open(INPUT_FILE, "r") as f:
    data = json.load(f)

items = data.get("items", [])

# Start HTML
html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>AWS Products</title>
<style>
body {
    font-family: Arial;
    background: #f5f5f5;
    margin: 20px;
}

.container {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
}

.card {
    background: white;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    transition: transform 0.2s;
}

.card:hover {
    transform: scale(1.03);
}

.title {
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 10px;
}


.badge {
    font-size: 16px;
    font-weight: bold;
    margin-bottom: 10px;
}

.body {
    font-size: 14px;
    margin-bottom: 15px;
}

a {
    text-decoration: none;
    color: #0073bb;
    font-weight: bold;
}
</style>
</head>
<body>

<h2>AWS Products</h2>
<div class="container">
"""

# Add cards
for entry in items:
    item = entry.get("item", {})
    fields = item.get("additionalFields", {})

    title = fields.get("title", "No Title")
    badge = fields.get("badge", "No Badge")
    body = fields.get("body", "")
    link = fields.get("ctaLink", "#")

    card = f"""
    <div class="card" data-category="{badge}">
        <div class="title">{title}</div>
        <div class="badge">{badge}</div>
        <div class="body">{body}</div>
        <a href="{link}" target="_blank">Learn More →</a>
    </div>
    """

    html += card

# Close HTML
html += """
</div>
</body>
</html>
"""

# Write output
with open(OUTPUT_FILE, "w") as f:
    f.write(html)

print(f"✅ HTML generated: {OUTPUT_FILE}")