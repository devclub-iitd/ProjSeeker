const intList = $('.search-suggestions');
let suggestions = document.querySelectorAll('.suggestion');

const intDummy = $('input[name="intDummy"]');

// focus out function for suggestion list
// TODO Optimize this
$(document).click((e) => {
    if (!$(e.target).hasClass('suggestion'))
        intList.css('display', 'none');
})

let index = -1;
intDummy.keyup((e) => {
    intList.css('display', 'block')
    // arrow key navigation logic
    if (e.keyCode == 40 || e.keyCode == 38 || e.keyCode == 13) {
        if (e.keyCode == 40) {
            if (index == -1) {
                index = index + 1;
                document.querySelector('.suggestion:first-child').classList.add('active');
            } else if (index < suggestions.length - 1) {
                suggestions[index].classList.remove('active');
                suggestions[++index].classList.add('active');
            } else return;
        } else if (e.keyCode == 38 && index != -1) {
            suggestions[index--].classList.remove('active');
            if (index != -1)
                suggestions[index].classList.add('active');
        } else if (e.keyCode == 13 && index != -1) {
            createTag(suggestions[index].innerText);
            index = -1;
            intList.css('display', 'none');
        }
        return;
    }
    // if the key pressed is a character, get suggested tags
    if(e.target.value.length > 0) {
        findTags(e.target.value, (res) => {
            intList.html('');
            res.unshift(e.target.value);
            res.forEach((sug) => {
                intList.append(`<li class="suggestion">${sug}</li>`);
            });
            suggestions = document.querySelectorAll('.suggestion');
        })
    }
    index = -1;
});

// suggestions click handler
$('.search-suggestions').on('click', '.suggestion', (e) => {
    createTag(e.target.textContent);
    intList.css('display', 'none');
});

const createTag = (tagVal) => {
    const tagContainer = document.querySelector('.tag-container');
    const tag = document.createElement('div');
    const interests = document.getElementById('interests');
    tag.textContent = tagVal;
    tag.classList.add('tag');
    tag.addEventListener('click', (e) => handleTagDelete(tag));
    tagContainer.appendChild(tag);
    if (interests.value != '')
        interests.value = interests.value + ', ' + tagVal;
    else interests.value = tagVal;
    intDummy.val('');
}

const handleTagDelete = (tag) => {
    var text = tag.textContent;
    console.log(text);
    tag.remove();
    var interests = $('#interests').val();
    interests = interests.split(', ')
    console.log(interests);
    interests = interests.filter((e) => {
        return e != text;
    });
    console.log(interests.join(", "));

    $('#interests').val(interests.join(", "));
}

// Provide a starting text and this will call the function callback(searchResults) where search_resulsts is the array of matched tags
const findTags = (startingText, callback = function () { }) => {
    const queryTag = 'research_field__startswith';
    $.ajax({
        url: `/interests?${queryTag}=${startingText}`,
        method: 'GET',
        success: (respData) => {
            var searchResults = [];
            respData.forEach((r) => {
                searchResults.push(r.research_field);
            })
            // console.log(searchResults);
            callback(searchResults);
        },
        error: (e) => {
            console.log(e);
        }
    });
}