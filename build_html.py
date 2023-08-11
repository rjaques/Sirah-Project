"""
Convert witness txt files into html and create an index page with links to all witness html files.

To run this script: 
* Provide the path to a changed text file as an argument in the module call on the command line:
`python readArabicToHtml.py path/to/my/changed/file`
* OR if you want to convert all files in a folder, provide the folder path:
`python readArabicToHtml.py path/to/folder`

NB: To read the script: start at the bottom!

"""

import os
import re
import shutil
import sys
import unicodedata
import pandas as pd
import markdown

####################
# GLOBAL VARIABLES #
####################

# Define the symbol to be used for a page number in the text:
PAGE_SYMBOL = "§"

# create an empty set to which we will add the ID numbers that have already been mentioned;
# we'll use this to check whether a paragraph is a variant of a previous report or not:
all_ids = set()

# create regular expressions we will use to split the text
# into pieces we can convert to html
# NB: the regexes will have to be rebuilt, I didn't have the witness texts!

# define a regex pattern that will match the start of a paragraph:
#paragraph_regex = r"(?:\r*\n\r*){2,}# (?=@)(?!@COMM)"
paragraph_regex = r"[\n ]*# +(?=@)(?!@COMM)"

# define a regex pattern that will match any ID in a paragraph
# PV: the IDs look like this: `@HSNXV01P653A_BEG_WZATB`:
# - HSNX = the ID of the source
# - V01 = volume 1
# - P635 = page 635
# - A = the first quote from this page; B is the second, C the third, etc.
# 
# At the beginning and end of a paragraph, a number of elements are added: `@HSNXV01P653A_BEG_WZATB`
# - _BEG_ = beginning of the report (_END_ for end of the report)
# - WZATB = name of the current witness file
#
# Variant readings are indicated like this: `VAR_HSNXV01P653A`
id_regex = r"(?:VAR_|@)([A-Z]{4,}?V\d+P\d+[A-Z]*)"  # @ZTTHV01P155B, VAR_ZTTHV01P386A

# define a regex pattern for the end of a report witness,
# including the final page number (in a capture group!)
#id_end_regex = r"@[A-Z]{4,}?V\d+P\d+[A-Z]*_END_[A-Z]{4,}[\r\n ]*(PageV\d+P\d+[AB]?)"
id_end_regex = r"@[A-Z]{4,}?V\d+P\d+[A-Z]*_END_[A-Z]{4,}\W+(PageV\d+P\d+[AB]?)"  # this catches situations where the ID is followed by a period

# define a regex pattern for the start of a paragraph's comment:
comm_regex = r"# @COMMENT:"

# Create a dictionary that contains verbose definition of each witness code:
root_folder = os.getcwd()
df = pd.read_excel(os.path.join(root_folder, "data", "meta", "Witness_list_sheet.xlsx"))
selected_columns = df[['Arabic name', 'Witness ']]
witness_dict = {}
for index, row in selected_columns.iterrows():
    key = row['Witness ']
    value = str(row['Arabic name'])
    witness_dict[key] = value

# create a dictionary that contains a verbose citation for each citation code: 
df = pd.read_excel(os.path.join(root_folder, "data", "meta", "Kevin Bibliography.xlsx"))
selected_columns = df[['ID', 'short_author', 'short_title']]
bibliography_dict = {}
for index, row in selected_columns.iterrows():
    key = row['ID']
    value = f"<span class='ref-author'>{row['short_author']}</span>, <span class='ref-title'>{row['short_title']}</span>"
    bibliography_dict[key] = value


#########################################################################################################################
        
def create_html_path(file_name, html_folder):
    html_fn = file_name.split('.')[0] + '.html'
    html_path = os.path.join(html_folder, html_fn)
    return html_path

def clean_filename(fn, lowercase=False):
    """Remove non-ascii letter characters and spaces from filenames"""
    # replace spaces with hyphens:
    fn = re.sub(r"\s+", "-", fn)
    # separate combining characters:
    fn = unicodedata.normalize("NFD", fn)
    # remove anything that is not an ASCII word character or hypen:
    fn = re.sub(r"[^a-zA-Z0-9\-.]+", "", fn)
    # convert to lowercase:
    if lowercase:
        fn = fn.lower()
    return fn
    

def clean_text(text, fn):
    """Clean the text to remove tags that we don't want to display and to make working with regular expressions easier.
    The function will flag important inconsistencies in the text files that should be corrected in the data."""
    
    # remove @EC... tags (e.g., @EC_12/30/22@):
    text = re.sub(" *@EC_[\d/]+@", "", text)
    # remove Kevin's personal tags:
    #text = re.sub("SEE_\w+(?: *to +\w+)?", "", text)
    text = format_SEE(text)

    # remove carriage return (in Windows, a new line starts with both carriage return \r and newline \n character)
    text = re.sub(r"\r", "", text)
    # Fix lines that start with a space:
    text = re.sub("\n +", "\n", text)
    # remove left-to-right mark:
    text = re.sub("\u200e", "", text)
    # remove backslashes:
    backslashes = re.findall(r"\\.{,100}", text)
    if backslashes:
        print(fn, "contains backslashes. Please remove them:")
        for p in backslashes:
            print("-", p.strip())
        # temporarily fix the issue:
        text = re.sub(r"\\", "", text)

    # fix paragraphs that start with an end tag instead of a beginning tag:
    paragraphs_that_start_with_end_tag = re.findall("# @\w+_END_\w+", text)
    if paragraphs_that_start_with_end_tag:
        print(fn, ": the following paragraphs start with an _END_ tag instead of a _BEG_ tag:")
        for p in paragraphs_that_start_with_end_tag:
            print("-", p)
        # temporarily fix the issue:
        text = re.sub(r"(\n\n# @\w+)_END_", r"\1_BEG_", text)

    # fix paragraphs that end with a _BEG_ tag instead of an _END_ tag:
    paragraphs_that_end_with_start_tag = re.findall("(@\w+_BEG_\w+) *\n+Page", text)
    if paragraphs_that_end_with_start_tag:
        print(fn, ": the following paragraphs end with a _BEG_ tag instead of an _END_ tag:")
        for p in paragraphs_that_end_with_start_tag:
            print("-", p)
        # temporarily fix the issue:
        text = re.sub(r"(@\w+)_BEG_(\w+ *\n+Page)", r"\1_END_\2", text)

    # fix paragraphs that end with a "naked" tag instead of an _END_ tag:
    paragraphs_that_end_with_naked_tag = re.findall("(@\w{4,}?V\d+P\d+[A-Z]?) *\n+Page", text)
    if paragraphs_that_end_with_naked_tag:
        print(fn, ": the following paragraphs end with a 'naked' tag instead of an _END_ tag:")
        for p in paragraphs_that_end_with_naked_tag:
            print("-", p)
        # temporarily fix the issue:
        text = re.sub(r"(@\w{4,}?V\d+P\d+[A-Z]?) *\n+Page", r"\1_END_XXXX\nPage", text)

    # fix paragraphs that do not start with double new line:
    paragraphs_without_double_new_line = re.findall("[^\n]\n# (@\w+_BEG_\+)", text)
    if paragraphs_without_double_new_line:
        print(fn, ": the following paragraphs do not start with a double new line:")
        for p in paragraphs_without_double_new_line:
            print("-", p)
        # temporarily fix the issue:
        text = re.sub(r"[\n ]+(# @\w+_BEG_)", r"\n\n\1", text)

    # fix paragraphs that do not start with hash tag:
    paragraphs_that_dont_start_with_hash = re.findall(".*(?<!# )(@\w+_BEG_\w+)", text)
    if paragraphs_that_dont_start_with_hash:
        print(fn, ": the following paragraphs do not start with a hashtag:")
        for p in paragraphs_that_dont_start_with_hash:
            print("-", p)
        # temporarily fix the issue:
        text = re.sub(r".*(?<!# )(@\w+_BEG_)", r"# \1", text)

    # Fix inconsistencies with the COMMENT tag: 
    # - make sure there's no additional new lines before any comment section, 
    #   so that we can use double new lines as paragraph pattern
    # - remove spaces between "@" and "COMMENT"
    # - fix typo "COMENT"
    # - fix type "NOTE" instead of "COMMENT"
    # - fix lowercase tag ("@Comment")

    space_in_tag = re.findall("# @ +(?:COMM?ENT|NOTE).{,50}", text)
    typo_in_tag = re.findall("# @ *(?:CO(?!MMENT)|NOTE).{,50}", text)
    multiple_lines = re.findall("\n\n# @ *(?:CO(?!MMENT)|NOTE).{,50}", text)
    lower_case = re.findall("# @ *(?:[cC]omm?ent).{,50}", text)

    inconsistent_comment_tags = space_in_tag + typo_in_tag + multiple_lines + lower_case
    if inconsistent_comment_tags:
        print(fn, ": the following comment tags contain inconsistencies")
        if space_in_tag:
            print("* a space in between '@' and 'COMMENT':")
            for p in space_in_tag:
                print("  -", p.strip())
        if typo_in_tag:
            print("* a typo in the tag itself:")
            for p in typo_in_tag:
                print("  -", p.strip())
        if multiple_lines:
            print("* a typo in the tag itself:")
            for p in multiple_lines:
                print("  -", p.strip())
        if lower_case:
            print("* lower case is used instead of upper case in the tag:")
            for p in lower_case:
                print("  -", p.strip())
        # temporarily fix the issues:
        text = re.sub(r"\n+# @ *(?:COMM?ENT|NOTE)", "\n# @COMMENT", text, flags=re.IGNORECASE)

    # Fix paragraphs where the page number is after the comments:
    page_number_after_comments = re.findall("(\w+_END_.+[\n]+)# @COMMENT.+[\n]+PageV\d+P\d+[A-Z]*", text)
    if page_number_after_comments:
        print(fn, ": in these paragraphs, the page numbers are erroneously located after the comments:")
        for p in page_number_after_comments:
            print("-", p.strip())
        # fix the issue temporarily:
        text = re.sub("(_END_.+[\n]+)(# @COMMENT.+[\n]+)(PageV\d+P\d+[A-Z]*)", r"\1\3\2", text)

    # Fix missing page numbers:
    missing_page_numbers = re.findall("(\w+_END_.+[\n ]+)(?=[^P\n ])", text)
    if missing_page_numbers:
        print(fn, ": the current sections do not have a page number following the text:")
        for p in missing_page_numbers:
            print("-", p.strip())
        # fix the issue temporarily:
        text = re.sub("(\w+?)(V\d+P\d+)([A-Z]*_END_\w+)[\n ]+(?=[^P\n ])", r"\1\2\3\nPage\2\n", text)

    return text

def build_toc(toc_list, toc_template, indentation):
    # deal with empty toc:
    if not toc_list:
        return ""
    # merge all the substrings of the toc_list into a single string:
    toc_str = "".join(toc_list)
    # close last list item:
    toc_str += "</li>\n"
    # close open list levels:
    prev_spaces = " " * len(re.findall("( +)<li>", toc_list[-1])[-1])
    while prev_spaces:
        ul_spaces = " " * (len(prev_spaces) - int(indentation/2))
        li_spaces = " " * (len(prev_spaces) - indentation)
        toc_str += f'{ul_spaces}</ul>\n{li_spaces}</li>\n'
        prev_spaces = li_spaces
    # add the "toc-list" ID to the first ul tag:
    toc_str = re.sub("<ul>", "<ul id='toc-list'>", toc_str, count=1)
    # wrap the list in the table of contents template:
    toc_str = re.sub("TABLE_OF_CONTENTS_HERE", toc_str, toc_template)
    return toc_str



def check_unicode_characters(text):
    import unicodedata
    print("This is a list of all unicode characters used in the text:")
    for char in sorted(list(set(text))):
        try:
            print([char], unicodedata.name(char))
        except:
            print([char], "NO NAME FOUND!")

def convert_to_html(text_file_path, html_folder, template_str, toc_template, indentation=4): 
    """
    Convert a single witness text file to html and store it in the html folder

    Args:
        text_file_path (str): path to a witness text file
        html_folder (str): path to the html folder
        template_str (str): path to the html template for the web pages
    """
    print("********************************************************")
    print("converting", text_file_path)
    print("********************************************************")
    # create an empty string that will contain the markdown code for the table of contents:
    toc_list = []
    # load the text:
    with open(text_file_path, 'r', encoding='utf-8') as file: 
        text = file.read()

    #check_unicode_characters(text)

    # clean the text from inconsistencies:
    data_folder, text_file_name = os.path.split(text_file_path)
    text = clean_text(text, text_file_name)

    # split the text on section headers and convert each part to html:
    body = ""  # this will contain the html body
    meta_header = True
    for section in re.split("(### \|+ .+[\r\n]+)", text):
        # NB: the parentheses make sure the section headers are not discarded:
        #   re.split("(b)", "abc")  > ["a", "b", "c"]
        #   re.split("b", "abc")    > ["a", "c"]
        #print("Section:", len(section), "characters")
        if meta_header: # anything before the first header tag is metadata
            #print("-------> meta_header!")
            body += format_meta(section)
            meta_header = False
            # remove all the metadata and extract any paragraphs that precede the first section header:
            section = re.sub("#META#.+|#OpenITI-RKJ#", "", section)
            body += format_section_content(section)
        elif section.startswith("### |"): # this section is a section header
            #print("-------> section_header!")
            #print(section)
            section_title, toc_list = format_section_title(section, toc_list)
            body += section_title
        else: # this section contains the witness reports
            #print("-------> witness report!")
            body += format_section_content(section)

    # replace the placeholder body tag in the template with the converted witness html:
    #print(len(body), "characters in body")
    #html_str = re.sub("<body>\s*</body>", f"<body>%s</body>" % body, html_str)
    #html_str = re.sub('<div id="pageContent">\s*</div>', f'<div id="pageContent">%s</div>' % body, html_str)
    html_str = re.sub("PAGE_CONTENT_HERE", body, template_str)

    # build the table of contents and add it to the page:
    toc_html = build_toc(toc_list, toc_template, indentation)
    html_str = re.sub("TABLE_OF_CONTENTS_HERE", toc_html, html_str)
    
    # save the witness html:
    html_fp = create_html_path(text_file_name, html_folder)
    with open(html_fp, mode="w", encoding="utf-8") as file:
        file.write(html_str)

    return html_fp

def format_meta(section):
    """Extract the relevant metadata keys from the mARkdown header
    and convert them to html

    Args:
        section (str): the first part of the text file,
            before the first section header
    """
    s = ""

    english_title = re.findall("Transliterated Name: *(.+)", section)
    if english_title:
        s += "<h2 dir='ltr'>The witness version of " + english_title[0].strip() + "</h2>\n"

    arabic_title = re.findall("#META# الكتاب: *(.+)", section)
    if arabic_title:
        s += "<h1>" + arabic_title[0].strip() + "</h1>\n"

    arabic_author = re.findall("#META# المؤلف: *(.+)", section)
    if arabic_author:
        s += "<h2>" + arabic_author[0].strip() + "</h2>\n"
    
    s += "<br/><br/>"
    return s

def make_variant_card(id_, text, comment, checkbox=True, hidden=False):
    """Make the html for a card displaying a single variant of a text fragment
    that has more than one variant.

    Args:
        id_ (str): the ID of a paragraph
        text (str): the text of a paragraph (witness report)
        comment (str): the comment(s) to a paragraph
        checkbox (bool): if True, a checkbox will be added above the text 
          that makes it possible to hide the witness
        
    """
    if checkbox:
        #checkbox_html = f"""<input type="checkbox" id="{id_}-card-cb" class="card-cb" onclick="toggleCard(this)" checked>"""
        checkbox_html = f"""<input type="checkbox" id="{id_}-card-cb" class="card-cb" checked>"""
    else:
        checkbox_html = ""
    if hidden:
        hidden_str = " hidden"
    else:
        hidden_str = ""

    return f"""
        <div class="card{hidden_str}" id="{id_}">
            
            <div class="card-header">
                {checkbox_html}
                {format_reference(id_, text)}
                <div class="diff-buttons">
                  <button class="diffButton">Compare</button>
                  <button class="hideDiffButton hidden">Hide Diff</button>
                </div>
            </div>
            {format_witness_text(id_, text)}
            {format_comment(comment)}
        </div>"""

def make_variants_index(ids):
    """Create html for the index card that contains checkboxes for each variant

    Args:
        ids (list): a list of ids of the variants of this text fragment
    """
    
    #checkboxes = [make_index_checkbox(id_, lookup_ref_by_id(id_)) for id_ in ids]
    checkboxes = []
    for i, id_ in enumerate(ids):
        ref = lookup_ref_by_id(id_)
        if i < 2:
            checked = True
        else:
            checked = False
        checkboxes.append(make_index_checkbox(id_, ref, checked))
        
    checkboxes = "\n".join(checkboxes)
    return f"""
        <div class="index">
            <div class="plus">
              <span>+</span>
            </div>
            <div class="card index-card hidden">
              <span class="hide">(hide)</span>
              {checkboxes}
            </div>
        </div>"""

def make_index_checkbox(id_, ref, checked=True):
    if checked:
        checked_str = " checked"
    else:
        checked_str = ""
    return f"""
                <div class="cb-container">
                    <input type="checkbox" class="index-check" name="{id_}" value="{id_}" id="{id_}-index-cb" "{checked_str}> 
                    <label for="{id_}" title="{ref}">{id_}</a></label>
                </div>"""

def format_section_title(section_title, toc_list, indentation=4):
    """Format a section title as html tags (h3, h4, h5, ...)

    Args:
        section_title (str): a section title line from the witness text
        (introduced by mARkdown tag ### |, ### ||, ...)
        toc (dict): dictionary containing the table of contents 
            (keys: slug, values: section title)
    """
    # check the number of pipes to decide what html <h> tag should be used:
    level = section_title.count("|")
    h_tag = f"h{level+2}"
    # remove the mARkdown tag from the section title line:
    bare_section_title = re.sub("### \|+ *", "", section_title.strip())
    # create slug from title (to be used as id/anchor):
    title_without_tags = re.sub("[^ ء-ي]+", " ", bare_section_title).strip()
    slug = re.sub("\s+", "-", title_without_tags)
    # shorten long slugs: 
    if slug.count("-") > 5:
        slug = "-".join(slug.split("-")[:5])
    # make non-unique slugs unique by adding a serial number:
    slugs = re.findall('href="#([^"]+)', "".join(toc_list))
    i=0
    while slug in slugs:
        i+=1
        if i < 2:
            slug += "-01"
        slug = f"{slug[:-2]}{i:02}"

    # wrap the section in html tags:
    section_title_html = f"<{h_tag} id='{slug}'>{bare_section_title}</{h_tag}>\n"

    # add the title to the table of contents: 
    toc_list = add_to_toc(title_without_tags, slug, toc_list, level, indentation)

    return section_title_html, toc_list

def add_to_toc(title_without_tags, slug, toc_list, level, indentation):
    # get the indentation spaces for the current title:
    spaces = int(level * indentation) * " "
    # get the previous title's indentation spaces:
    try:
        prev_spaces = " " * len(re.findall("( +)<li>", toc_list[-1])[-1])
    except:
        prev_spaces = ""
    # add the title to the table of contents, based on its hierarchical level
    # (as measured by the indentation spaces):
    s = ""
    if len(spaces) == len(prev_spaces):
        # close previous list item:
        s += "</li>\n"
        # add new list item:
        s += f'{spaces}<li><a href="#{slug}">{title_without_tags}</a>'
    elif len(spaces) < len(prev_spaces):
        # close previous list item:
        s += "</li>\n"
        # close previous list levels:
        while len(prev_spaces) != len(spaces):
            ul_spaces = " " * (len(prev_spaces) - int(indentation/2))
            li_spaces = " " * (len(prev_spaces) - indentation)
            s += f'{ul_spaces}</ul>\n{li_spaces}</li>\n'
            prev_spaces = li_spaces
        # add new list item:
        s += f'{spaces}<li><a href="#{slug}">{title_without_tags}</a>'
    elif len(spaces) > len(prev_spaces):
        # add new list level(s):
        while prev_spaces != spaces:
            ul_spaces = " " * (len(prev_spaces) + int(indentation/2))
            li_spaces = " " * (len(prev_spaces) + indentation)
            s += f'\n{ul_spaces}<ul>\n{li_spaces}<li>'
            prev_spaces = li_spaces
        # add current line:
        s += f'<a href="#{slug}">{title_without_tags}</a>'
    toc_list.append(s)
    return toc_list

def format_report(witness_texts, comments, ids):
    if len(witness_texts) == 0:
        #print("NO WITNESS TEXT FOUND IN THIS PARAGRAPH UNTIL NOW!")
        return ""
    elif len(witness_texts) == 1:
        return f"""
        <div class="report">
          <div class="single-witness">
          {format_reference(ids[0], witness_texts[0])}
          {format_witness_text(ids[0], witness_texts[0])}
          {format_comment(comments[0])}
          <br>
          </div>
        </div>
        """
    
    elif len(witness_texts) > 2 :
        # create index card if there are more than 3 witnesses:
        variants_index = make_variants_index(ids)
        checkbox = True
    else:
        variants_index = ""
        checkbox = False
    
    variant_cards = []
    i = 0
    hidden = False
    for id_, text, comment in zip(ids, witness_texts, comments):
        i += 1
        if i > 2:
            hidden = True
        card = make_variant_card(id_, text, comment, checkbox=checkbox, hidden=hidden)
        variant_cards.append(card)
    variant_cards = "\n".join(variant_cards)

    return  f"""
    <div class="report">
        <div class="scrolling-wrapper">
            <div class="centered-wrapper">
                {variants_index}
                {variant_cards}
            </div>
        </div>
    </div>
    """


def format_section_content(section):
    """Convert the content of a section (chapter, subchapter) into report divs
    Html structure of the sections:

    <div class="report">
      <div class="card">
        <div class="witn-text"></div>
        <div class="witn-comm"></div>
        <div class="witn-ref"></div>
      </div>
    </div>
    """
    # remove any whitespace (new lines, spaces) at the beginning of the section:
    section =  section.lstrip()

    # do not process empty sections:
    if not section:
        return ""
    
    # initialize the string that will contain the html code for the entire section:
    s = ""

    # deal with sections that start with a comment: 
    if section.startswith("# @COMMENT"):
        #print("SECTION STARTS WITH # @COMMENT:")
        #print(section[:100])
        first_comment = re.findall(".+?\n\n+", section)[0]
        s += format_comment(first_comment.strip())
        section = section[len(first_comment)-1].strip()

    # initialize the lists that will contain the data for a single report (possibly multiple variants!)
    witness_texts = []
    comments = []
    ids = []
    
    # split the content of the section into paragraphs: 
    paragraphs = re.split(paragraph_regex, section)
    #print("this section contains", len(paragraphs), "paragraphs")
    for paragraph in paragraphs:
        if paragraph.strip() == "":
            continue # don't process empty paragraphs

        # split each paragraph into its witness_text and comment sections:
        #print("*************")
        #print(paragraph)
        #print("=============")
        try:
            witness_text, end_page, comment = re.split(id_end_regex, paragraph)
        except Exception as e:
            print(e)
            print("µµµµµµµµµµµµµµµµµµµµ")
            print(paragraph)
            print("--------------------")
            try:
                witness_text, comment = re.split("\w+_END_\w*", paragraph)
                end_page = "PageV00P000"
            except Exception as e:
                print(e)
                print("µµµµµµµµµµµµµµµµµµµµ")
                print(paragraph)
                print("--------------------")
            
            witness_text = paragraph
            end_page = "PageV00P000"
            comment = ""

        # get all witness IDs mentioned in the witness_text:
        paragraph_ids = re.findall(id_regex, witness_text)
        
        # check whether this paragraph is a variant of a previous report
        # (by checking whether its ID is already in the all_ids set):
        try:
            main_id = paragraph_ids[0]
            #print("main_id:", main_id)
            if main_id not in all_ids: # that means, this is the first variant of a report

                # close previous report subsection (if there is one):
                s += format_report(witness_texts, comments, ids)

                # initialize a new report subsection:
                witness_texts = []
                comments = []
                ids = []
                
        except Exception as e:
            print("NO ID FOUND?", e)
            print("witness text:")
            print(witness_text)
            main_id = "@XXX"

        # make sure that variant texts of the current report are recognized as variants, not new reports:
        for id_ in paragraph_ids:
            all_ids.add(id_)

        # add the paragraph's data to the report's lists:
        witness_texts.append(witness_text+end_page)
        comments.append(comment)
        ids.append(main_id)

    # close last open report div:
    if witness_texts:
        s += format_report(witness_texts, comments, ids)

    return s


def format_page_number(page_no):
    """Convert a mARkdown page number to HTML"""
    # TO DO
    vol, page = re.findall("PageV0*([1-9]\d*)P0*([1-9]\d*)", page_no)[0]
    page_no = f"(Page {page} of vol. {vol})"
    return page_no

def format_page_number_sub(match_obj):
    """This function can be used in a re.sub replacement
    to convert a mARkdown page number to HTML.
    The idea is to convert any page number inside a paragraph
    with a pilcrow; if you hover over it, it will show the volume and page number
    
    The way this is displayed may have to be adapted!
    """
    # TO DO
    vol, page = (match_obj.group(1), match_obj.group(2))
    a = f"<a class='page-no' href='javascript:void(0);' title='end of page {page} of vol. {vol}'>{PAGE_SYMBOL}</a>"
    return a


def format_witness_text(main_id, witness_text):
    """Convert a witness report paragraph to HTML.

    Args:
        main_id (str): the ID of the current witness report
        witness_text (str): the content of the current witness report
    """
    # remove witness IDs from witness_text:
    t = re.sub(id_regex+"\w*", "", witness_text)
    # remove hashtags:
    t = re.sub("# *", "", t)
    # remove the page number attached to the end of the text:
    t = re.sub(r"PageV\d+P\d+[A-Z]*\Z", "", t)
    # format page numbers inside text:
    t = re.sub("PageV0*([1-9]\d*)P0*([1-9]\d*)[A-Z]*", format_page_number_sub, t)
    
    # TO DO: add links to persons mentioned in the text (currently hiding them)
    t = re.sub(r"(@TR\w+@)", r'<a class="hidden" href="#">\1</a>', t)

    # format Quran quotations:
    t = re.sub(r"@QURS(\d+)A(\d+)_BEG([^@]+?)@QURS\1A(\d+)_END", 
               r'<a href="https://quran.com/\1/\2" class="quran" title="Qurʾān \1.\2-\4" target="_blank">\3</a>', t)
    # remove end aya if it's the same as start aya:
    t = re.sub(r"(Qurʾān \d+\.)(\d+)-\2", r"\1\2", t)

    # format poetry:
    t = re.sub(r"\n(.+?) %~% (.+)", r"\n<span class='poetry-line'><span class='hemistich1'>\1</span>  <span class='hemistich2'>\2</span></span>", t)
    
    # assemble the html:
    return f"""\
        <div class='witness-text-container'>
          <p class='witness-text'>
            {t.strip()}
          </p>
          <p class='diff hidden'></p>
        </div>"""


def format_SEE(s):
    """Format "SEE_" references"""
    def expand_reference(m):
        """Expand a reference abbreviation (e.g., "HSNXV01P233B") into a full reference.
        
        Args:
            m (re.matchobj): matching object for the regex "([A-Z]{4,5})V(\d+)P(\d+)([A-Z]*)"
        """
        ref = m.group(0)
        abb = m.group(1)
        vol = m.group(2).lstrip('0')
        page = m.group(3).lstrip('0')
        to_page = m.group(5)
        try:
            expanded = bibliography_dict[abb]
        except:
            print("REFERENCE NOT FOUND IN BIBLIOGRAPHY:", abb)
            expanded = "[REFERENCE NOT FOUND IN BIBLIOGRAPHY]"
        # remove any html tags inside the expanded reference:
        expanded = re.sub("<[^>]+?>", "", expanded)
        return f'<span class="see_reference" title="See {expanded}, vol. {vol} p. {page}{to_page}">*</span>'
    
    s = re.sub("SEE_([A-Z]{4,5})V(\d+)P(\d+)([A-Z]*)((?: *to +\w+)?)", expand_reference, s)
    if "SEE_" in s:
        print("INCORRECTLY FORMATTED 'SEE_' TAGS:")
        for tag in re.findall("SEE_\w+(?: *to +\w+)?", s):
            print("* ", tag)
        s = re.sub("SEE_(\w+(?: *to +\w+)?)", r'<span class="see_reference" title="See \1">*</span>', s)
    return s


def format_comment(comment):
    """Convert a paragraph's comment(s) to HTML
    NB: the comment will be visible when you hover your mouse over the word COMMENT
    and remain visible when you click on it.

    Args:
        comment (str): a comment on a witness report paragraph
    """

    def expand_reference(m):
        """Expand a reference abbreviation (e.g., "HSNXV01P233B") into a full reference.
        
        Args:
            m (re.matchobj): matching object for the regex "([A-Z]{4,5})V(\d+)P(\d+)([A-Z]*)"
        """
        ref = m.group(0)
        abb = m.group(1)
        vol = m.group(2).lstrip('0')
        page = m.group(3).lstrip('0')
        try:
            expanded = bibliography_dict[abb]
        except:
            print("REFERENCE NOT FOUND IN BIBLIOGRAPHY:", abb)
            expanded = "[REFERENCE NOT FOUND IN BIBLIOGRAPHY]"
        return f"{ref} ({expanded}, vol. {vol} p. {page})"

    def expand_witness(m):
        """Expand a witness abbreviation (e.g., WSACD) into a full reference.
        
        Args:
            m (re.matchobj): matching object for the regex r"\b([A-Z]{4,5})\b"
        """
        abb = m.group(0)
        try:
            expanded = witness_dict[abb]
        except:
            print("WITNESS NOT FOUND IN DICTIONARY:", abb)
            expanded = "WITNESS NOT FOUND"

        return f'<a href="{abb}.html" target="_blank">{abb}</a> ({expanded})'



    # remove the comment tag:
    comment = re.sub(comm_regex, "", comment)

    # remove empty comments:
    if comment.strip() == "":
        return ""
    
    # replace witness abbreviations with their full names:
    comment = re.sub(r"\bW[A-Z]{4}\b", expand_witness, comment)

    # replace reference IDs with the full reference:
    comment = re.sub("([A-Z]{4,5})V(\d+)P(\d+)([A-Z]*)", expand_reference, comment)

    # remove all tags inside the comment:
    comment_without_tags = re.sub(" *<[^>]+?> *", " ", comment)

    # split comment into paragraphs:
    split_comment = re.split(" *\n+ *", comment.strip())
    comment = "\n    ".join([f'<p dir="auto">{p}</p>' for p in split_comment if p.split()])
    
    return f"""\
<div class='comment-container'>
  <a title='{comment_without_tags}' href="javascript:void(0);" class="comment-link">COMMENT</a>
  <div class='comment hidden'>
    {comment}
  </div>
</div>
"""


def lookup_ref_by_id(id_):
    """Look up the ID number in the reference list; return a reference
    TO DO!"""
    return id_

def format_reference(id_, text):
    """Convert a paragraph's reference(s) to HTML
    NB: the reference will be visible when you hover your mouse over the word REFERENCE
    and remain visible when you click on it.

    Args:
        id_ (str): id_ of the paragraph (e.g., TKXXV04P096B)
    """
    #book_ref = lookup_ref_by_id(id_)
    try:
        book_ref = bibliography_dict[id_[:4]]
    except:
        book_ref = id_[:4]
        print(f"{book_ref} (from {id_}) not found in bibliography dict")
    try:
        vol_no, first_page = re.findall("V0*([1-9]\d*)P0*([1-9]\d*)", id_)[-1]
    except:
        vol_no = "?"
        first_page = "?"
        print("no vol and page number found in this ID:")
        print(id_)
    #last_page = re.findall("P(\d+[A-Z]*)", id_)[-1]
    try:
        last_page = re.findall("P0*([1-9]\d*)", text)[-1]
    except:
        last_page = "?"
        print("No last page found in the text:")
        print(text)
        input()
        return ""
    if last_page != first_page:
        reference = f"{book_ref}, vol. {vol_no} p. {first_page}-{last_page}"
    else:
        reference = f"{book_ref}, vol. {vol_no} p. {last_page}"
    
    # remove any html tags inside the reference:
    reference_without_tags = re.sub(" *<[^>]+?> *", " ", reference)

    return f"""
        <div class="reference-container">
            <a title="{reference_without_tags}" href="javascript:void(0);" class="ref-link">{id_}</a>
            <div class="reference hidden">
              <p dir="ltr">{reference}</p>
            </div>
        </div>
        """

def generate_file_list(data_folder, html_folder, relative_paths=True):
    """
    Args:
        data_folder (str): path to folder containing all data files
        html_folder (str): path to folder containing all data files
    """
    # create a list of all (future) html files in the html folder:
    file_paths = []
    for file_name in os.listdir(data_folder):
        if os.path.isfile(os.path.join(data_folder, file_name)):
            if not file_name.endswith((".csv", ".tsv", ".xlsx")):
                #html_path = html_folder + "/" + file_name
                #file_paths.append(html_path)
                if relative_paths:
                    file_paths.append(file_name + ".html")
                else:
                    html_path = os.path.join(html_folder, file_name + ".html")
                    file_paths.append(html_path)
    return file_paths

def generate_witness_list(file_paths):
    """Create an unordered list (ul) of links to the witness pages
    
    Args:
        file_paths (list): list of the paths to the witness pages
    """
    # create a list of all html files in the html folder:

    ul = "<ul>\n"
    for file_path in file_paths:
        id_ = file_path.split("/")[-1].split(".")[0]
        try:
            label = witness_dict[id_]
        except:
            label = id_
        ul += f"<li><a href='{file_path}'>{label} ({id_})</a></li>\n"
    ul += "</ul>\n"
    return ul

def convert_markdown_file(fp):
    """Open a markdown file and convert it into an html string.
    
    Args:
        fp (str): path to the markdown file
    """
    with open(fp, mode="r", encoding="utf-8") as file:
        md = file.read()
    html = markdown.markdown(md)
    if not html:
        html = "<p>COMING SOON...</p>"
    return html

def generate_info_page(template_str, md_fp, html_fp, direction="ltr"):
    """
    Create the content for an info page
    
    Args:
        template_str (str): the template for every page in the website
        md_fp (str): path to the markdown file containing the material for this page
        html_fp (str): path to the output html file
        direction (str): general text direction ("ltr" or "rtl") for this info page.
            Default: "ltr".
    """
    print("generating", html_fp, "from", md_fp)
    
    # change the main text direction of the page to left-to-right if the text is in English:
    if direction == "ltr":
        template_str = re.sub("""dir=['"]rtl['"]""", 'dir="ltr"', template_str)

    # check if a specific css file exists for this file (a css file with the same filename)
    # and insert a link to that css file in the html header if it exists:
    html_folder, html_fn = os.path.split(html_fp)
    css_fn = html_fn[:-5] + ".css"
    css_fp = os.path.join(html_folder, "css", css_fn)
    if os.path.exists(css_fp):
        placeholder = "<!--INSERT_PAGE_SPECIFIC_CSS_HERE-->"
        style_sheet_link = f'<link rel="stylesheet" type="text/css" href="./css/{css_fn}">'
        template_str = re.sub(placeholder, style_sheet_link, template_str)

    # convert the index.md markdown file to html:
    if md_fp.endswith("md"):
        html = convert_markdown_file(md_fp)
    else:
        with open(md_fp, mode="r", encoding="utf-8") as file:
            html = file.read()
    
    # paste it into the template:
    html_content = re.sub("PAGE_CONTENT_HERE", html, template_str)

    # remove the TOC placeholder
    html_content = re.sub("TABLE_OF_CONTENTS_HERE", "", html_content)

    # save it into the html folder:
    with open(html_fp, "w", encoding="utf-8") as html_file:
        html_file.write(html_content)

def generate_menu_bar(menu_folder, html_folder):
    """Generate html pages from markdown files in the menu_folder 
    and links to those files in the menu bar"""
    menu_bar = ""
    for fn in os.listdir(menu_folder):
        fp = os.path.join(menu_folder, fn)
        if fn.endswith(("md", "html")) and os.path.isfile(fp):
            html_fn = fn.replace(".md", ".html")
            #html_fn = html_fn.replace(" ", "-").lower()
            html_fn = clean_filename(html_fn, lowercase=True)
            html_fp = os.path.join(html_folder, html_fn)
            label = re.sub("\.html|\.md", "", fn).lower()
            if fn != "index.md":
                menu_bar += f'      <div><a href="{html_fn}">{label}</a></div>\n'
    return menu_bar
    
def main():
    """Build the website"""

    # get the file or folder path that is given as an argument in the module call
    # (see https://www.google.com/amp/s/www.geeksforgeeks.org/how-to-use-sys-argv-in-python/amp/)
    try:
        path = sys.argv[1]
    except:
        print("provide a path to a text file or the folder containing all text files")
        sys.exit(1) # abort the execution

    # get the ouptut folder path (may be given as a second command-line argument).
    # If no output folder path was given, use the default: "work-in-progress"
    try:
        html_folder = sys.argv[2]
    except: 
        html_folder = "work-in-progress"

    # create a safety copy of the output folder:
    if os.path.exists(html_folder):
        if os.path.exists("safety_copy"): 
            shutil.rmtree("safety_copy") # create existing temp folder
        shutil.copytree(html_folder, "safety_copy")
    else:
        os.makedirs(html_folder)
        os.makedirs("safety_copy")

    try:
        # load the html templates for the web pages:
        root_folder = os.path.dirname(html_folder)
        template_folder = os.path.join(root_folder, "templates")
        page_template_fp =  os.path.join(template_folder, "page_template.html")
        with open(page_template_fp, mode="r", encoding="utf-8") as file:
            template_str = file.read()
        toc_template_fp = os.path.join(template_folder, "table_of_contents.html")
        with open(toc_template_fp, mode="r", encoding="utf-8") as file:
            toc_template = file.read()

        # Step 1: generate the list of paths to all html files and add it to the template:
        
        # get the path to the data folder:
        if os.path.isdir(path):
            data_folder = path
            # remove the html files currently in the output folder:
            for fn in os.listdir(html_folder):
                if fn.endswith("html"):
                    os.remove(os.path.join(html_folder, fn))
        elif os.path.isfile(path):
            data_folder = os.path.dirname(path)
        else:
            print(path)
            print("is not a valid path to a file or folder")
            sys.exit(1) # abort the execution
        # create a list of output filepaths based on the contents of the data_folder:
        file_list = generate_file_list(data_folder, html_folder)
        # add the links to the witness pages to the sidebar in the html template:
        witness_list = generate_witness_list(file_list)
        template_str = re.sub("WITNESS_LIST_HERE", witness_list, template_str)

        # step 2: generate the menu bars based on the files in the "data/top_menu" and "data/side_menu" folders
        # and add them to the template:
        
        top_menu_folder = os.path.join(root_folder, "data", "top_menu")
        top_menu_bar = generate_menu_bar(top_menu_folder, html_folder)
        template_str = re.sub("TOP_MENU_BAR_HERE", top_menu_bar, template_str)

        side_menu_folder = os.path.join(root_folder, "data", "side_menu")
        side_menu_bar = generate_menu_bar(side_menu_folder, html_folder)
        template_str = re.sub("SIDE_MENU_BAR_HERE", side_menu_bar, template_str)

        # step 3: generate the index page and other info pages:
        
        all_info_fps = []
        for folder in [top_menu_folder, side_menu_folder]:
            for fn in os.listdir(folder):
                fp = os.path.join(folder, fn)
                all_info_fps.append((fp, fn))

        for fp, fn in all_info_fps:
            print(fp, fn)
            if fn.endswith("md") and os.path.isfile(fp):
                html_fn = fn.replace(".md", ".html")
                #html_fn = html_fn.replace(" ", "-").lower()
                html_fn = clean_filename(html_fn, lowercase=True)
                html_fp = os.path.join(html_folder, html_fn)
                # generate the html page:
                generate_info_page(template_str, fp, html_fp)


        # Step 4: convert the witness file(s) to html:
        
        if os.path.isdir(path):
            # if the argument is a folder, convert all files in it to html:
            for fn in os.listdir(path):
                fp = os.path.join(path, fn)
                html_path = convert_to_html(fp, html_folder, template_str, toc_template)
        elif os.path.isfile(path):
            # if the argument is a file, convert that file only:
            html_path = convert_to_html(path, html_folder, template_str, toc_template)
    
    except:
        # print the full exception traceback:
        import traceback
        traceback.print_exc()
        # restore the output folder:
        print("restoring safety copy")
        shutil.rmtree(html_folder)
        shutil.copytree("safety_copy", html_folder)
        shutil.rmtree("safety_copy")
        # abort script:
        sys.exit(1)

    # clean up safety copy:
    shutil.rmtree("safety_copy")

    
if __name__ == "__main__":
    main()
