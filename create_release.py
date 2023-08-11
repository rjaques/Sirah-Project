from datetime import datetime
import shutil
import sys




working_dir = "work-in-progress"
redirect_template_fp  = "templates/redirect.html"
base_url = "https://pverkind.github.io/sira-project-pv/"

try:
    release_folder = sys.argv[1]
    print("RELEASE NAME (from CL argument):", release_folder)
except:
    # create the name for the release folder:
    timestamp = datetime.now().strftime("%Y-%m-%d")
    release_folder = "v" + timestamp
    print("RELEASE NAME (generated in Python):", release_folder)

# copy the current working directory to the release folder:
shutil.copytree(working_dir, release_folder)

# reroute the user to the new release:
release_url = base_url + release_folder
with open(redirect_template_fp, mode="r", encoding="utf-8") as file:
    html = file.read()
html = html.replace("LATEST_VERSION_URL", release_url)
with open("index.html", mode="w", encoding="utf-8") as file:
    file.write(html)

# print the name of the new folder so that it can be used by the workflow script:
print(f'::set-output name=release_folder::{release_folder}')
