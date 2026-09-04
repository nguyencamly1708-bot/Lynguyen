import sys

sys.stdout.reconfigure(encoding="utf-8")

from server import fetch_and_parse_sheet, generate_st_table_image, find_dc_group_for_st, load_json, GROUPS_FILE

data = fetch_and_parse_sheet()
print(f"Total grouped ST: {len(data)}")
groups = load_json(GROUPS_FILE, {})

for st, items in list(data.items())[:5]:
    gid, title = find_dc_group_for_st(groups, st)
    print(f"ST: {st:5} | Items: {len(items):2} | DC Group: {title} ({gid})")

if "AV4" in data:
    img = generate_st_table_image("AV4", data["AV4"], "test_server_output.png")
    print(f"✅ Generated AV4 test image: {img}")
