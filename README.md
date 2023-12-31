# Sira project website

This is a prototype of a website for Kevin Jaques' Sira Project. 
It can be viewed here: [rjaques.github.io/Sirah-Project/](https://rjaques.github.io/Sirah-Project/)

The website is versioned: the index.html file in the root folder of the repository
will redirect to the latest released version (releases are dated: vYYYY-MM-DD).

External users should only use the released version, which is citable and does not change.
The latest changes (since the latest release) are visible under 
[rjaques.github.io/Sirah-Project/work-in-progress](https://rjaques.github.io/Sirah-Project/work-in-progress)

The goal is that Kevin can keep on working on his witness files and whenever he pushes his changes to GitHub,
the changes will be reflected in the work-in-progress page. When he's happy with the current state of the website
(or, every three months), he can create a new dated release. 

The GitHub Actions script that updates the website whenever a change is pushed to GitHub
also performs some consistency tests on the data. You can see the output reports ("logs") of the GitHub Actions 
script under the [Actions tab](https://github.com/rjaques/Sirah-Project/actions) in the github repo. In the left-hand column, click "Build website" to see
a report for all website updates. Click on the label of the latest run of the "Build website" workflow,
then click "build-html" and then on "rebuild website". The log lists all the inconsistencies the script found
in the witness files; you can fix these manually in the witness files. 


# Setup

(this should be done only once)

For this to work, you should:

1. enable GitHub Actions with the correct permissions:

* Under your repository name (Sirah-Project), click  Settings. If you cannot see the "Settings" tab, select the  dropdown menu, then click Settings.
* In the left sidebar, click  Actions, then click General.
* scroll down to "Workflow permissions", select "Read and write permissions" and press "save".

2. enable GitHub Pages:

* Under your repository name, click  Settings. If you cannot see the "Settings" tab, select the  dropdown menu, then click Settings.
* In the left sidebar, click  Pages
* Under "branch", choose "main", keep the default location as "root/"  and click "save"
The content of the root folder of your repo is now served under <your_github_name>.github.io/Sirah-Project
(and because we have put the index.html file in the root folder, that will be displayed by default when you go to that page)

# Folder structure

```
|- .github/
|     |- workflows/
|           |- build_website.yml: script that runs on github server anytime something is changed to the repo;
|                                 it uses the build_html.py script (in the root folder) to rebuild the website.
|           |- automated_release.yml: automatically creates a release every 3 months
|           |- manual_release.yml: creates a new release at the click of a button
|- data/ : contains the data from which the website is built
|     |- witness_files/ : contains the witness text files
|     |- top_menu/ : contains markdown files for each section in the horizontal menu on the top of the website. 
|     |              When you create a new markdown file here, a new section will be added to the menu bar. 
|     |- side_menu/ : contains markdown files for each section in the side menu on the website. 
|     |               When you create a new markdown file here, a new section will be added to the side menu.
|     |- landing_page/ contains the markdown file for the landing page (home): index.md
|     |- meta/ : contains the Excel files with the metadata for the witness codes and bibliography
|- work-in-progress/ : contains the generated witness html pages for the latest data
|     |- css/ : contains the css files that define the styling of the website
|     |- js/ : contains the javascript files that make the website interactive
|     |- ... : all html files of the website 
|- vYYYY-MM-DD/ : v for version, YYYY for year, MM for month, DD for day: stable releases of the website
|- images/ : contains all images needed for the website (photos of contributors, header image, funders' logos, ...)
|- templates/ : contains the templates used to build the website
|- index.html: web page that sends the user to the latest release version of the website
|- build_html.py: the python script that builds the website
|- requirements.txt: a list of all Python libraries used by the Python scripts
|- README.md: this documentation file
```

# How to use this repository? 

## A. Updating witness files

### 1. very basic: using GitHub online only

* download the file you want to edit to your computer. All relevant files are in the `data/` folder (`data/witness_files/`, `data/top_menu/`, `data/side_menu/`, `data/landing_page/`). To download a witness file, click its name in the list of files, then click the download button to the right above the contents of the file in the `data/witness_files/` folder (for very large files, no download button is shown; click the 'raw' button instead and then save using ctrl+s).
* Edit your file in EditPad Pro on your computer
* Once you're finished (or want to call it a day), go back to the same folder on GitHub (e.g., data/witness_files), click the
  "add file" button, and then "upload files" in the dropdown menu that opens.
  You can now drag and drop the updated/new file. You'll be asked
  to provide a descriptive "commit message" before the file is uploaded.
* GitHub will now automatically rebuild the website (this will take ca. 3 minutes; you can follow the progress in the [Actions tab](https://github.com/rjaques/Sirah-Project/actions) on the repo's GitHub page) and the changes will be visible on the [work-in-progress page](https://rjaques.github.io/Sirah-Project/work-in-progress) 

### 2. more flexible and stable: using the command line

* Anytime BEFORE you want to work on the texts on your computer, pull the latest changes from GitHub: 
  `git pull origin main`
  (alternatively, download the file directly from GitHub)
* The witness files are in the `data/witness_files` folder in your local copy of the repository: work on them there, and whenever you are ready, 
  push them to GitHub using the following series of commands:
  - `git status`  (shows you all files that have changed)
  - `git add .`   (this collects all changes you made)
  - `git commit -m "(write a message describing what you changed here)"`  (record your changes in your local git repo)
  - `git pull origin main`  (make sure you have the latest changes from GitHub)
  - `git push origin main`  (this sends your changes to GitHub)

## B. updating a descriptive page (project description, contributors, ...)

These pages are generated from markdown files (extension: .md).
The files have the same names as the buttons/links in the top and side menus on the website.

Use the same method as described above for the witness files to edit/update these documents.

### Adding a new button/link to the menus

This is done by uploading a new markdown file  (extension: .md) to the relevant folder: `data/top_menu/` or `data/side_menu/`.

The file name will become the name of the link/button in the menu, so choose your filename wisely.

The order of the links/buttons in the top menu is determined by a numerical prefix to the file name: 

```
1_Project overview.md
2_Overview of the sīrah tradition.md
...
```

If you want to change the order, change these prefixes.

After uploading your file, the website will be rebuilt automatically. 
Your changes will be displayed in the  [work-in-progress page](https://rjaques.github.io/Sirah-Project/work-in-progress)  after ca. 3 minutes. 
You can follow the progress in the [Actions tab](https://github.com/rjaques/Sirah-Project/actions) on the repo's GitHub page.

### Writing markdown

Formatting text in markdown files is done using a small amount of tags. For a short introduction, see [this page](https://www.markdownguide.org/basic-syntax/).

The most relevant tags for you are:

* headers: use hashtags to define headers (note the space after the last hashtag):
    - `# first level header`
    - `## second level`
    - ...
* paragraphs: are separated by a double new line (hit the Enter key twice). A single new line is ignored!
* lists: simply start each list item on a new line, preceded with an asterisk and a space. For example,
```
* this is the first item in my list
* a second item
```
* links: put the text you want to display between square brackets and the url between parentheses. For example, `[this link](https://example.com)` will be displayed as [this link](https://example.com)
* images: if you want to add an image to a page, first upload it to the `images/` folder. Then insert it into the markdown file using this pattern: `![caption](../images/imagefile)`. For example, if you uploaded a map of Mecca called `MeccaMap.jpg`, you could include it into the page like this: `![Map of Mecca](../images/MeccaMap.jpg)`

## C. Creating a new release

The changes you make will not be visible to visitors of your website. You will have to periodically create a public release of your website.

The advantage of this system is double: 

* it allows you to work on your website in relative privacy and make your changes public only when you are happy with them
* users can cite a specific version of your website.

### Automatic quarterly release

The website is currently set up in a way that four times per year, a release will automatically be created
(this is handled by the .github/workflows/automated_release.yml script).

This means that the current "work-in-progress" folder will be copied and be given a new name, based on the date (e.g., v2023-08-15). Visitors to your website (rjaques.github.io/sirah-project) will automatically be forwarded to the latest release (e.g., rjaques.github.io/sirah-project/v2023-08-15).


### Manual release

You can also decide to create a new release at any point yourself, by a simple button click:

* go to the Actions tab in this repo
* click on "manual release" in the left-hand column,
* click on the "Run workflow" dropdown on the right, and inside the dropdown on the "Run workflow" button.

This will create a copy of the current work-in-progress website, using today's date as the folder name. 
(this is handled by the .github/workflows/manual_release.yml script).
The script will also add links to the new release in the "Revision and Update Notes" page of each older release,
and redirect visitors of rjaques.github.io/sira-project to the latest release.
The updated website should be available in ca. 2 minutes.

NB: on Firefox, the redirection does not work immediately, because the browser caches the old link. 
One solution is to open the link in a private browsing window. 
Alternatively, follow these steps ([source](https://bugzilla.mozilla.org/show_bug.cgi?id=923952#ch-9): 
* Open Web Developer Tools (Ctrl+Shift+I), click there "Network" tab and check the checkbox "Disable Cache" (disabled only in that tab)
* Load the original URL, e.g. by pasting the URL into the address bar
* Enable the cache again (optional)

#### Adding version release notes: 

Before doing a manual release, you can add notes to the new release; this is not necessary, but may be useful for yourself and your users. 

Go to the `data/side_menu/Revision and Update Notes.md` file, and under "Release list", copy the first item in the list and paste it on a new line above it. 
Then replace the date in the file name with today's date. Finally, add your notes, and save the changes.

E.g., if you want to create a new version on 17 August 2023:

```
## Release list:
<!-- INSERT NEWER VERSION BELOW THIS -->
* [v2023-08-17](https://rjaques.github.io/Sirah-Project/v2023-08-16)
    - Added a new witness: WXXXX
    - Updated the "about" page
* [v2023-08-16](https://rjaques.github.io/Sirah-Project/v2023-08-16)
* [v2023-08-11](https://rjaques.github.io/Sirah-Project/v2023-08-11/)
* [v2023-08-07](https://rjaques.github.io/Sirah-Project/v2023-08-07/)
* [v2023-07-24](https://rjaques.github.io/Sirah-Project/v2023-07-24/)
```
