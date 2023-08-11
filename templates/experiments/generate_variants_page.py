def make_variants_index(ids, refs):
    """Create html for the index card that contains checkboxes for each variant

    Args:
        ids (list): a list of ids of the variants of this text fragment
        refs (list): a list of full references (one for each fragment,
            in the same order as the ids list)
    """
    checkboxes = [make_index_checkbox(id_, ref) for id_, ref in zip(ids, refs)]
    checkboxes = "\n".join(checkboxes)
    return f"""
  <div class="index">
    <div class="plus">
      <span onclick="toggleIndex(this)">+</span>
    </div>
    <div class="card index-card hidden">
      <span class="hide" onclick="toggleIndex(this)">(hide)</span>
{checkboxes}
    </div>
  </div>
"""

def make_index_checkbox(id_, ref):
    return f"""
      <div class="cb-container">
        <input type="checkbox" class="index-check" name="{id_}" value="{id_}" id="{id_}-index-cb" onclick="toggleCard(this)" checked> 
        <label for="{id_}" title="{ref}">{id_}</a></label>
      </div>
"""

def make_variant_card(id_, text, checkbox=True):
    """Make the html for a card displaying a single variant of a text fragment
    that has more than one variant.

    Args:
        ids (list): a list of ids of the variants of this text fragment
        refs (list): a list of full references (one for each fragment,
            in the same order as the ids list)
        fragment_texts (list): a list of variant texts of the fragment
            (in the same order as the ids list)
    """
    if checkbox:
        return f"""
          <div class="card" id="{id_}">
            <p>
              {text}
            </p>
          </div>"""
    else:
        return f"""
          <div class="card" id="{id_}">
            <input type="checkbox" id="{id_}-card-cb" onclick="toggleCard(this)" checked>
            <p>
              {text}
            </p>
          </div>"""

def make_variant_scroll(ids, refs, variant_texts):
    """Make the html for the scrolling display for a text fragment that has more than one variant

    Args:
        ids (list): a list of ids of the variants of this text fragment
        refs (list): a list of full references (one for each fragment,
            in the same order as the ids list)
        fragment_texts (list): a list of variant texts of the fragment
            (in the same order as the ids list)
    """
    variants_index = make_variants_index(ids, refs)
    variant_cards = [make_variant_card(id_, text) for id_, text in zip(ids, variant_texts)]
    variant_cards = "\n".join(variant_cards)
    return f"""
<div class="scrolling-wrapper">
{variants_index}
{variant_cards}
</div>
"""

def make_html(ids, refs, variant_texts):
    """Create an html page that displays the different variant texts (for testing only)"""
    page = """
<html dir="rtl">

<header>
  <style>
    .scrolling-wrapper {
      overflow-x: scroll;
      //overflow-y: scroll;
      overflow-y: hidden;
      white-space: nowrap;
    }

    .card {
      display: inline-block;
      width: 30vw;
      //border: 2px solid grey;
      //border-radius: 10px;
      border-left: 1px solid grey;
      position: relative;
      vertical-align:top;
      resize:both;
      overflow:auto;
      padding-left: 5px;
      padding-right: 5px;
    }
    .index {
      vertical-align:top;
      display: inline-block;
    }
    .plus {
      display: inline-block;
      vertical-align: center;
      color: lightgreen;
      font-size: 50px;
      font-weight: bold;
      cursor: pointer;
    }
    .hide {
      cursor: pointer;
      color: grey;
      font-weight: italic;
    }

    .hidden {
      display: none;
    }
    p {
      word-wrap: break-word;
      white-space: wrap;
    }
    
  </style>
</header>
<body>

<h2>First fragment</h2>


%s


<script>

  function toggleCard(checkbox) {
    // get the id of the text fragment from the checkbox:
    var id0 = checkbox.id.split("-")[0];
    // get the value of the clicked checkbox:
    var thisChecked = checkbox.checked;
    // set both the internal and external checkboxes to the same:
    document.querySelector("#"+id0+"-index-cb").checked = thisChecked
    var cardCB = document.querySelector("#"+id0+"-card-cb")
    cardCB.checked = thisChecked
    // hide the card:
    let card = cardCB.parentNode;
    card.classList.toggle("hidden")
  }

  function toggleIndex(el) {
    console.log(el.parentNode);
    var index = el.parentNode.parentNode;
    index.querySelector(".plus").classList.toggle("hidden");
    index.querySelector(".index-card").classList.toggle("hidden")
  }
</script>
</body>
</html>
""" % make_variant_scroll(ids, refs, variant_texts)
    with open("test.html", mode="w", encoding="utf-8") as file:
        file.write(page)

if __name__ == "__main__":
    ids = ["id1","id2","id3"]
    refs = ["ref1", "ref2", "ref3"]
    texts = ["text1", "text2", "text3"]

    make_html(ids, refs, texts)
