import re
import sys

contents = ""

with open('README.md', 'r') as f:
    contents = f.read()
    match = re.search(r'([0-9]+)\%', contents)
    match_number = match.group()[:-1]
    cov_score_num = int(sys.argv[1].strip()[:-1])

# If numbers match, git push is good to go
if int(match_number) == cov_score_num:
    exit(0)
else:
    badge_color = "blueviolet"
    if cov_score_num == 100:
        badge_color = "brightgreen"
    elif cov_score_num >= 80:
        badge_color = "green"
    elif cov_score_num >= 60:
        badge_color = "yellowgreen"
    elif cov_score_num >= 40:
        badge_color = "yellow"
    elif cov_score_num >= 20:
        badge_color = "orange"
    else:
        badge_color = "red"
    re.sub(r"([0-9]+)\%", f"{cov_score_num}%", contents)
    re.sub(r"%25-([a-z]+)", f"%25-{badge_color}", contents)
    with open("README.md", 'w') as f:
        f.write(contents)
    exit(1)
