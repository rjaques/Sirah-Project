from datetime import datetime
import os
import re
import shutil
import sys




working_dir = "work-in-progress"
redirect_template_fp  = "templates/redirect.html"
base_url = "https://rjaques.github.io/Sirah-Project/"

try:
    release_folder = sys.argv[1]
    print("RELEASE NAME (from CL argument):", release_folder)
except:
    # create the name for the release folder:
    timestamp = datetime.now().strftime("%Y-%m-%d")
    release_folder = "v" + timestamp
    print("RELEASE NAME (generated in Python):", release_folder)

release_url = base_url + release_folder
release_link = f'<a href="{release_url}">{release_folder}</a>'

# add the new release to the release notes: 

# get the current version of the release notes:
revision_fp = "data/side_menu/Revision and Update Notes.md"
with open(revision_fp, mode="r", encoding="utf-8") as file:
    revision_text = file.read()

# make the new release version the current version:
revision_text = re.sub(r"The current release is.+", 
                       f"The current release is **[{release_folder}]({release_url})**",
                       revision_text)

# add the new release version to the release list (if it has not yet been manually added):
insert_note = "<!-- INSERT NEWER VERSION BELOW THIS -->"
if not re.findall(f"{insert_note}\s*\* \[{release_folder}", revision_text):
    revision_text = re.sub(insert_note, 
                           f"{insert_note}\n* [{release_folder}]({release_url})",
                           revision_text)

# store the current release notes:
with open(revision_fp, mode="w", encoding="utf-8") as file:
          file.write(revision_text)

# Add a reference to the new release in all previous release notes + work-in-progress html file:
for folder in sorted(os.listdir(".")):
    if re.findall("^v\d+", folder) or folder.startswith("work-in"):
        earlier_revision_fp = os.path.join(folder, "revision-and-update-notes.html")
        if not os.path.exists(earlier_revision_fp):
            continue
        with open(earlier_revision_fp, mode="r", encoding="utf-8") as file: 
            html = file.read()
        if release_link in html:
            continue
        html = re.sub(f'{insert_note}\s*<ul>',
                      f'{insert_note}\n<ul>\n<li>{release_link}</li>',
                      html)
        if folder == "work-in-progress":
            html = re.sub(r'The current release is\s*<strong>[\s\S]+?</strong>',
                          f'The current release is <strong>{release_link}</strong>',
                          html)
        with open(earlier_revision_fp, mode="w", encoding="utf-8") as file:
            file.write(html)


# copy the current working directory to the release folder:
if os.path.exists(release_folder):
    shutil.rmtree(release_folder)
shutil.copytree(working_dir, release_folder)

# reroute the user to the new release:
with open(redirect_template_fp, mode="r", encoding="utf-8") as file:
    html = file.read()
html = html.replace("LATEST_VERSION_URL", release_url)
with open("index.html", mode="w", encoding="utf-8") as file:
    file.write(html)



# print the name of the new folder so that it can be used by the workflow script:
print(f'::set-output name=release_folder::{release_folder}')
