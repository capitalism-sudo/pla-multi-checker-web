import {
  DEFAULT_MAP,
  MESSAGE_ERROR,
  MESSAGE_INFO,
  showMessage,
  showModalMessage,
  clearMessages,
  clearModalMessages,
  doSearch,
  showNoResultsFound,
  saveIntToStorage,
  readIntFromStorage,
  saveBoolToStorage,
  readBoolFromStorage,
  setupExpandables,
  showPokemonIVs,
  showPokemonInformation,
  showPokemonHiddenInformation,
  initializeApp,
} from "./modules/common.mjs";

const resultTemplate = document.querySelector("[data-pla-results-template]");
const resultsArea = document.querySelector("[data-pla-results]");

// options
const inputS0 = document.getElementById("inputs0");
const inputS1 = document.getElementById("inputs1");
const inputS2 = document.getElementById("inputs2");
const inputS3 = document.getElementById("inputs3");
const advances = document.getElementById("advances");
const gameVer = document.getElementById("version");
const storyFlag = document.getElementById("storyflags");
const roomID = document.getElementById("roomid");
const diglettMode = document.getElementById("diglett");
const minAdv = document.getElementById("minadvances");

// filters
const distSelectFilter = document.getElementById("selectfilter");
/*const distShinyOrAlphaCheckbox = document.getElementById(
  "mmoShinyOrAlphaFilter"
);*/
const distShinyCheckbox = document.getElementById("mmoShinyFilter");
//const distAlphaCheckbox = document.getElementById("mmoAlphaFilter");
const mmoSpeciesText = document.getElementById("mmoSpeciesFilter");
const advanceText = document.getElementById("advanceFilter");

//distShinyOrAlphaCheckbox.addEventListener("change", setFilter);
distShinyCheckbox.addEventListener("change", setFilter);
//distAlphaCheckbox.addEventListener("change", setFilter);
mmoSpeciesText.addEventListener("input", setFilter);
advanceText.addEventListener("input", setFilter);

// actions
const checkUGButton = document.getElementById("pla-button-checkug");
checkUGButton.addEventListener("click", checkUnderground);

loadPreferences();
setupPreferenceSaving();
setupExpandables();
//setupTabs();

const results = [];

// Setup tabs

// Save and load user preferences
function loadPreferences() {
  distShinyCheckbox.checked = readBoolFromStorage("mmoShinyFilter", false);
  advances.value = localStorage.getItem("advances") ?? "0";
  minAdv.value = localStorage.getItem("minadvances") ?? "0";
  storyFlag.value = localStorage.getItem("storyflags") ?? "6";
  gameVer.value = localStorage.getItem("version") ?? "1";
}

function setupPreferenceSaving() {
  advances.addEventListener("change", (e) =>
    localStorage.setItem("advances", e.target.value)
  );
  minAdv.addEventListener("change", (e) =>
    localStorage.setItem("minadvances", e.target.value)
  );
  distShinyCheckbox.addEventListener("change", (e) =>
    saveBoolToStorage("mmoShinyFilter", e.target.checked)
  );
  storyFlag.addEventListener("change", (e) =>
    localStorage.setItem("storyflags", e.target.value)
  );
  gameVer.addEventListener("change", (e) =>
	localStorage.setItem("version", e.target.value)
  );
}

/*function setupTabs() {
  document.querySelectorAll(".tablinks").forEach((element) => {
    element.addEventListener("click", (event) =>
      openTab(event, element.dataset.plaTabFor)
    );
  });
}

function openTab(evt, tabName) {
  let i, tabcontent, tablinks;

  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }

  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }

  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.className += " active";
}*/

function setFilter(event) {
  if (event.target.checked) {
    if (event.target == distShinyCheckbox) {
      //distShinyOrAlphaCheckbox.checked = false;
    }
  }

  showFilteredResults();
}

function validateFilters() {
}

function filter(
  result,
  shinyFilter,
  speciesFilter,
  advanceFilter
) {

  console.log("advancefilter");
  console.log(advanceFilter);
  
  if (shinyFilter && !result.shiny) {
    return false;
  }

  if (
    speciesFilter.length != 0 &&
    !result.species.toLowerCase().includes(speciesFilter.toLowerCase())
  ) {
    return false;
  }
  
  if (
	advanceFilter.length != 0 &&
	result.advances != parseInt(advanceFilter)
  ) {
	  return false;
  }

  return true;
}

function getOptions() {
  return {
    s0: inputS0.value,
	s1: inputS1.value,
	s2: inputS2.value,
	s3: inputS3.value,
    advances: parseInt(advances.value),
    story: parseInt(storyFlag.value),
    version: parseInt(gameVer.value),
    diglett: diglettMode.checked,
	room: parseInt(roomID.value),
	filter: distSelectFilter.value,
	minadv: parseInt(minAdv.value),
    //	inmap: inmapCheck.checked
  };
}

function checkUnderground() {
  doSearch(
    "/api/check-underground",
    results,
    getOptions(),
    showFilteredResults,
    checkUGButton
  );
}

function showFilteredResults() {
  //validateFilters();
  
  //let shinyOrAlphaFilter = distShinyOrAlphaCheckbox.checked;
  let shinyFilter = distShinyCheckbox.checked;
  //let alphaFilter = distAlphaCheckbox.checked;
  let speciesFilter = mmoSpeciesText.value;
  //let defaultFilter = distDefaultCheckbox.checked;
  //let multiFilter = distMultiCheckbox.checked;
  let advanceFilter = advanceText.value;

  const filteredResults = results.filter((result) =>
    filter(
      result,
      shinyFilter,
      speciesFilter,
	  advanceFilter
    )
  );

  console.log("Filtered Results:");
  console.log(filteredResults);
  
  if (filteredResults.length > 0) {
    resultsArea.innerHTML =
      "<section><h3>D = Despawn. Despawn Multiple Pokemon by either Multibattles (for aggressive) or Scaring (for skittish) pokemon.</h3></section>";
    filteredResults.forEach((result) => showResult(result));
  } else {
    showNoResultsFound();
  }
}


function showResult(result) {
  const resultContainer = resultTemplate.content.cloneNode(true);
  
  let sprite = document.createElement("img");
  sprite.src = "static/img/spritebig/" + result.sprite;
  resultContainer.querySelector(".pla-results-sprite").appendChild(sprite);
  
  resultContainer.querySelector("[data-pla-results-species]").innerHTML =
    result.species;

  resultContainer.querySelector("[data-pla-results-spawn]").textContent =
	result.spawn;
	
  let resultShiny = resultContainer.querySelector("[data-pla-results-shiny]");
  let sparkle = "";
  let sparklesprite = document.createElement("img");
  sparklesprite.className = "pla-results-sparklesprite";
  sparklesprite.src =
    "data:image/svg+xml;charset=utf8,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%3E%3C/svg%3E";
  sparklesprite.height = "10";
  sparklesprite.width = "10";
  sparklesprite.style.cssText =
    "pull-left;display:inline-block;margin-left:0px;";
	
  if (result.shiny) {
    sparklesprite.src = "static/img/shiny.png";
    sparkle = "Shiny!";
  } else {
    sparkle = "Not Shiny";
  }
  resultContainer
    .querySelector("[data-pla-results-shinysprite]")
    .appendChild(sparklesprite);
  resultShiny.textContent = sparkle;
  resultShiny.classList.toggle("pla-result-true", result.shiny);
  resultShiny.classList.toggle("pla-result-false", !result.shiny);

  resultContainer.querySelector("[data-pla-results-adv]").textContent =
    result.advances;
  resultContainer.querySelector("[data-pla-results-nature]").textContent =
    result.nature;
	
  let gender = 'male';
  if (result.gender == 1){
	  gender = 'female';
  }
  else if (result.gender == 2){
	  gender = 'genderless';
  }
  
  const genderStrings = {
  male: "Male <i class='fa-solid fa-mars' style='color:blue'/>",
  female: "Female <i class='fa-solid fa-venus' style='color:pink'/>",
  genderless: "Genderless <i class='fa-solid fa-genderless'/>",
  };

  resultContainer.querySelector("[data-pla-results-gender]").innerHTML =
    genderStrings[gender];

  resultContainer.querySelector("[data-pla-results-ability]").textContent =
    result.ability;
  resultContainer.querySelector("[data-pla-results-egg]").textContent =
    result.eggmove;
	
  showPokemonIVs(resultContainer, result);
  showPokemonHiddenInformation(resultContainer, result);

  resultsArea.appendChild(resultContainer);
}
