$(document).ready(function () {
    $(window).keydown(function (event) {
        if (event.keyCode == 13) {
            event.preventDefault();
            return false;
        }
    });
});
const checkJpeg = (input) => {
    var file = input.files[0];
    if (file.type != 'image/jpeg') {
        alert("Only jpg files are allowed");
        input.value = "";
    }
}

const checkPdf = (input) => {
    var file = input.files[0];
    if (file.type != 'application/pdf') {
        alert('Only PDF files are allowed');
        input.value = "";
    }
}


const intList = $('.search-suggestions');
let suggestions = document.querySelectorAll('.suggestion');

const intDummy = $('input[name="intDummy"]');
intDummy.focusout(() => {
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
            e.preventDefault();
        }
        return;
    }
    // if the key pressed is a character, get suggested tags
    findTags(e.target.value, (res) => {
        if (res.length > 0) {
            intList.html('');
            res.forEach((sug) => {
                intList.append(`<option class="suggestion">${sug}</option>`)
            })
        } else {
            intList.html(`<option class="suggestion">No results found</option>`)
        }
        suggestions = document.querySelectorAll('.suggestion');
    })
});

const createTag = (tagVal) => {
    const tagContainer = document.querySelector('.tag-container');
    const tag = document.createElement('div');
    tag.textContent = tagVal;
    tag.classList.add('tag');
    tag.addEventListener('click', (e) => handleTagDelete(tag));
    tagContainer.appendChild(tag);
    interests.value = interests.value + ', ' + tagVal;
    intDummy.val('');
}

const deleteDoc = (doc_type) => {
    if (doc_type != 'pic' && doc_type != 'cv' && doc_type != 'transcript')
        return

    $.ajax({
        url: '/delete-student-doc',
        method: 'POST',
        data: {
            'type': doc_type,
            'csrfmiddlewaretoken': $('body > div.dashboard-wrapper > div.profile-container > form > input[type=hidden]:nth-child(1)').val(),
        },
        success: (r) => {
            console.log(r);
            // TODO add some loading screen in these.
            setTimeout(() => {
                location.reload();
            }, 1000);
        },
        error: (e) => {
            console.error(e);
        }
    });
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
    $.ajax({
        url: `/find-interests?q=${startingText}`,
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

$(function () {
    $('#profile-form').submit(function (event) {
        $.ajax({
            method: $(this).attr('method'),
            url: $(this).attr('action'),
            data: new FormData($('form')[0]),

            cache: false,
            contentType: false,
            processData: false,

            headers: {
                'X-CSRFTOKEN': $('body > div.dashboard-wrapper > div.profile-container > form > input[type=hidden]:nth-child(1)').val(),
            },
            success: (r) => {
                console.log(r);
                // TODO add some loading screen in these.
                setTimeout(() => {
                    location.reload();
                }, 1000);
            },
            error: (e) => {
                console.error(e);
            }

        });


        return false;
    });
});