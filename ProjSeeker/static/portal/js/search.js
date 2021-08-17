var multiChoiceFilters = {
  dept: {
    queryTerm: "prof__dept",
    selections: [],
  },
  degree: {
    queryTerm: "degree__icontains",
    selections: [],
  },
  type: {
    queryTerm: "project_type__icontains",
    selections: [],
  },
  tag: {
    queryTerm: "tags__research_field",
    selections: [],
  },
  duration: {
    queryTerm: "duration__icontains",
    selections: [],
  },
  is_paid: {
    queryTerm: "is_paid",
    selections: [],
  },
  exclude_passed: {
    queryTerm: "exclude_passed",
    selections: [],
  },
};
const searchQueryTerm = "search";
var searchTerm = "";
var visibleData = {};

var projGrid = $(".project-grid");
const cardTemplate = $("#cardTemplate");

$(function () {
  searchProjects();
  $("#loader").fadeOut(200);
  $(".project-grid").delay(200).fadeIn(200);
});

const createCheckbox = (tagVal) => {
  const tagBox = `<label for="${tagVal}"><input type="checkbox" name="${tagVal}" id="${tagVal}" onchange="applyFilter('tag')">${tagVal}</label>`;
  $("#tag-filter").append(tagBox);
};

const deleteCheckbox = (tagVal) => {
  $(`#tag-filter label[for="${tagVal}"]`).remove();
  const index = multiChoiceFilters["tag"].selections.indexOf(tagVal);
  if (index > -1) multiChoiceFilters["tag"].selections.splice(index, 1);

  applyFilter("tag");
};

const applyFilter = (filter) => {
  if (!Object.keys(multiChoiceFilters).includes(filter)) return;

  const value = this.event.target.id;
  var selections = multiChoiceFilters[filter].selections;
  if (this.event.target.checked) {
    if (!selections.includes(value)) {
      selections.push(value);
    }
  } else {
    selections = selections.filter((d) => d != value);
  }
  multiChoiceFilters[filter].selections = selections;

  sendRequest();
  return false;
};
const searchProjects = () => {
  try {
    searchTerm = this.event.target.value;
  } catch (error) {
    searchTerm = "";
  }
  sendRequest();
  return false;
};

const queryBuilder = () => {
  let query = `${searchQueryTerm}=${searchTerm}`;
  Object.keys(multiChoiceFilters).forEach((key) => {
    const filter = multiChoiceFilters[key];
    const qTerm = `&${filter.queryTerm}=`;
    const selections = filter.selections;

    if (selections.length !== 0) {
      query += qTerm;
      query += selections.join(qTerm);
    }
  });
  return query;
};

const sendRequest = () => {
  $.ajax({
    method: "GET",
    url: `/projects?${queryBuilder()}`,

    success: (r) => {
      updateData(r);
    },
    error: (e) => {
      console.error(e);
    },
  });
};

const truncate = (str, no_words) => {
  return str.split(" ").splice(0, no_words).join(" ") + " ...";
};

const updateData = (data) => {
  visibleData = data;
  console.log(visibleData);

  displayData();
};

const displayData = () => {
  var projGridChildren = projGrid.children();
  for (let i = 0; i < projGridChildren.length; i++) {
    const c = projGridChildren[i];
    if (c.style.display != "none") {
      c.remove();
    }
  }

  if (visibleData.projects.length == 0) {
    projGrid.append(
      '<h2 style="color:white;">No projects found for this search term!</h2>'
    );
    return;
  }
  visibleData.projects.forEach((proj) => {
    var newNode = cardTemplate.clone();
    newNode[0].style.display = "flex";
    var children = newNode.children();
    children[0].innerText = truncate(proj.title, 4);
    children[1].innerText = `Prof. ${proj.prof.user.first_name} ${proj.prof.user.last_name}`;
    children[2].innerText = truncate(proj.description, 30);
    children[3].href = `/projects/${proj.id}/`;
    projGrid[0].appendChild(newNode[0]);
  });
};

$("#filterBtn").click(() => {
  $(".sort-list").fadeToggle(100);
});

const sortBy = (key, elem) => {
  $(".sort-list").fadeOut(100);
  var reverse = $(elem).attr("data-reverse");
  if (!key) key = "id";

  if (visibleData.projects.length == 0) return;

  const isDate = key.search("date") !== -1;

  visibleData.projects.sort((a, b) => {
    const aKey = isDate ? new Date(a[key]) : a[key];
    const bKey = isDate ? new Date(b[key]) : b[key];

    if (aKey < bKey) {
      return reverse === "true" ? 1 : -1;
    }
    if (aKey > bKey) {
      return reverse === "true" ? -1 : 1;
    }
    return 0;
  });

  if (reverse === "false") $(elem).attr("data-reverse", "true");
  else $(elem).attr("data-reverse", "false");

  displayData();
};
