import { kitabDiff} from "./kitabDiff.js"


// toggle visibility of the sidebar:

function toggleSidebar() {
  // toggle the dashboard sidebar:
  var dashboard = document.getElementById("dashboard");
  dashboard.classList.toggle("hidden");
  // adapt the width of the main content of the page:
  console.log(document.getElementById("pageContent"));
  if (dashboard.classList.contains("hidden")) {
    console.log("DASHBOARD HIDDEN");
    document.getElementById("pageContent").style.marginLeft = "5%";
  } else {
    console.log("DASHBOARD DISPLAYED");
    document.getElementById("pageContent").style.marginLeft = "20%";
  }
  // toggle the menu button:
  document.getElementById("openSidebarBtn").classList.toggle("hidden");
}

document.getElementById("closeSidebarBtn").addEventListener('click', toggleSidebar);
document.getElementById("openSidebarBtn").addEventListener('click', toggleSidebar);



// toggle visibility of the list of witnesses:
document.getElementById("witnessListLink").addEventListener('click', function () {
    var listDiv = document.getElementById("witnessList");
    listDiv.classList.toggle("hidden");
});


// add event listeners to buttons that display/hide the diff:

var diffButtons = document.querySelectorAll(".diffButton");
Array.from(diffButtons).forEach(function(element) {
    element.addEventListener('click', viewDiff);
});

var hideDiffButtons = document.querySelectorAll(".hideDiffButton");
Array.from(hideDiffButtons).forEach(function(element) {
      element.addEventListener('click', hideDiff);
});


// add event listeners to the checkboxes that hide/show variant cards:



// add event listeners to buttons that display/hide the list of variants:

var plusButtons = document.querySelectorAll(".plus");
Array.from(plusButtons).forEach(function(element) {
    element.addEventListener('click', toggleIndex);
});

var indexChecks = document.querySelectorAll(".index-check");
Array.from(indexChecks).forEach(function(element) {
        element.addEventListener('click', toggleCard);
});


var hideButtons = document.querySelectorAll(".hide");
Array.from(hideButtons).forEach(function(element) {
        element.addEventListener('click', toggleIndex);
});

var cardCheckboxes = document.querySelectorAll(".card-cb");
Array.from(cardCheckboxes).forEach(function(element) {
        element.addEventListener('click', toggleCard);
});


function toggleCard(e) {
    let checkbox = e.target;
    console.log(checkbox);
    // get the id of the text fragment from the checkbox:
    var id0 = checkbox.id.split("-")[0];
    // get the value of the clicked checkbox:
    var thisChecked = checkbox.checked;
    // set both the internal and external checkboxes to the same:
    document.querySelector("#"+id0+"-index-cb").checked = thisChecked;
    var cardCB = document.querySelector("#"+id0+"-card-cb")
    cardCB.checked = thisChecked;
    // hide the card:
    let card = cardCB.parentNode.parentNode;
    card.classList.toggle("hidden");
}


function toggleIndex(e) {
    var index = e.target.parentNode.parentNode;
    console.log("toggleIndex target:");
    console.log(e.target);
    index.querySelector(".plus").classList.toggle("hidden");
    index.querySelector(".index-card").classList.toggle("hidden")
}


var commentLinks = document.querySelectorAll(".comment-link");
Array.from(commentLinks).forEach(function(element) {
        element.addEventListener('click', toggleSiblingVisibility);
});
var refLinks = document.querySelectorAll(".ref-link");
Array.from(refLinks).forEach(function(element) {
    element.addEventListener('click', toggleSiblingVisibility);
});

// toggle the visibility of the next element
// (used to toggle visibility of comments and references):
function toggleSiblingVisibility(event) {
    // select the element immediately following the clicked element:
    let div = event.target.nextElementSibling;
    // add a hidden class if the div does not already have it;
    // or remove its hidden class if it does have it:
    div.classList.toggle('hidden'); 
}

function cleanText(el) {
  // create a clone of the element:
  let elClone = el.cloneNode(true);
  // remove all hidden child elements:
  elClone.querySelectorAll(".hidden").forEach(el => el.remove());
  // convert to text and trim whitespace:
  let text = elClone.textContent.trim();
  return text;
}

async function viewDiff(e) {
  const thisCard = e.target.parentNode.parentNode.parentNode;
  console.log(thisCard);
  const thisCardText = thisCard.querySelector(".witness-text");
  const thisCardDiff = thisCard.querySelector(".diff");
  // make sure the main variant's normal text is shown and its diff is hidden:
  thisCardText.classList.remove("hidden");
  thisCardDiff.classList.add("hidden");
  // display the hideDiff button instead of the view diff button:
  thisCard.querySelector(".diffButton").classList.add("hidden");
  thisCard.querySelector(".hideDiffButton").classList.remove("hidden");
  
  // display the diff with the main text on all other cards:
  const wrapper = thisCard.parentNode;
  for (const card of wrapper.children){
    //if ( (card != thisCard) && !(card.classList.contains("hidden") ) ) {
    //if (card != thisCard) {
      if ( (card != thisCard) && !(card.classList.contains("index") ) ) {
      // calculate the diff of this card's text with the main card's text:
      let cardText = card.querySelector(".witness-text");
      // TO DO: CLEAN THE STRINGS THAT ARE FED TO THE DIFF VIEWER!
      let textA = cleanText(thisCardText);
      let textB = cleanText(cardText);
      let [singleHtml, aHtml, bHtml] = await kitabDiff(textA, textB);
      console.log(bHtml);
      // put the formatted diff into the diff element and display it:
      let cardDiff = card.querySelector(".diff");
      cardDiff.innerHTML = singleHtml;
      cardDiff.classList.remove("hidden");
      // hide the normal text on the card:
      cardText.classList.add("hidden");

      // make sure the View Diff button is visible and the Hide Diff is hidden:
      card.querySelector(".diffButton").classList.remove("hidden");
      card.querySelector(".hideDiffButton").classList.add("hidden");
    }
  }
}



async function hideDiff(e) {
    const thisCard = e.target.parentNode.parentNode.parentNode;
    console.log(thisCard);
    const wrapper = thisCard.parentNode;
    for (const card of wrapper.children){
        if (!(card.classList.contains("index"))) {
            card.querySelector(".witness-text").classList.remove("hidden");
            card.querySelector(".diff").classList.add("hidden");
            card.querySelector(".diffButton").classList.remove("hidden");
            card.querySelector(".hideDiffButton").classList.add("hidden");
        }
    }
}

