document.addEventListener('DOMContentLoaded', function() {
    var editable = document.getElementById('editable');
    var textarea = document.getElementById('htmltextarea');
    
    textarea.value = editable.innerHTML;
});


// Watch for changes from text editor and apply it to html editor
document.getElementById('editable').addEventListener('input', function() {
    var editable = document.getElementById('editable');
    var textarea = document.getElementById('htmltextarea');
    
    textarea.value = editable.innerHTML;
});

// Watch for changes from html editor and apply it to text editor
document.getElementById('htmltextarea').addEventListener('input', function() {
    var editable = document.getElementById('editable');
    var textarea = document.getElementById('htmltextarea');
    
    editable.innerHTML = textarea.value;
});

function updateHTMLEditor() {
    var editable = document.getElementById('editable');
    var textarea = document.getElementById('htmltextarea');
    
    textarea.value = editable.innerHTML;
}

// Get the selected text
function getSelectedText() {
    if (window.getSelection) {
        return window.getSelection().toString();
    } else if (document.selection && document.selection.type != "Control") {
        // For older versions of IE
        return document.selection.createRange().text;
    }
    return '';
}

// Get the selected text and replace it with arg1
function replaceSelectedText(replacementText) {
    var sel, range;
    if (window.getSelection) {
        sel = window.getSelection();
        if (sel.rangeCount) {
            range = sel.getRangeAt(0);
            range.deleteContents();
            range.insertNode(document.createTextNode(replacementText));
        }
    } else if (document.selection && document.selection.createRange) {
        range = document.selection.createRange();
        range.text = replacementText;
    }
}

// Get the selected text and replace it with replacementText, wrapped with prefixTag and suffixTag
function replaceSelectedTextHtmlSuf(replacementText, prefixTag, suffixTag) {
    var sel, range;
    if (window.getSelection) {
        sel = window.getSelection();
        if (sel.rangeCount) {
            range = sel.getRangeAt(0);
            range.deleteContents();
            
            // Create a temporary container for the HTML content
            var tempDiv = document.createElement("div");
            tempDiv.innerHTML = `<${prefixTag}>${replacementText}</${suffixTag}>`;
            
            // Extract the child nodes from the temporary div and insert them into the range
            var frag = document.createDocumentFragment(), child;
            while ((child = tempDiv.firstChild)) {
                frag.appendChild(child);
            }
            range.insertNode(frag);
        }
    } else if (document.selection && document.selection.createRange) {
        // For IE < 9
        range = document.selection.createRange();
        var taggedText = `<${prefixTag}>${replacementText}</${suffixTag}>`;
        range.pasteHTML(taggedText);
    }
}

// Get the selected text and replace it with arg1 with arg2 as HTML tags
function replaceSelectedTextHtml(replacementText, prefixTag) {
    var sel, range;
    if (window.getSelection) {
        sel = window.getSelection();
        if (sel.rangeCount) {
            range = sel.getRangeAt(0);
            range.deleteContents();
            
            var wrapper = document.createElement(prefixTag);
            wrapper.innerHTML = replacementText;
            range.insertNode(wrapper);
        }
    } else if (document.selection && document.selection.createRange) {
        // For IE < 9
        range = document.selection.createRange();
        var taggedText = '<' + prefixTag + '>' + replacementText + '</' + prefixTag + '>';
        range.pasteHTML(taggedText);
    }
}

// Get the selected text and insert a new line after the selection
function insertNewLineAtSelection() {
    var sel, range, br;
    if (window.getSelection) {
        // Non-IE browsers
        sel = window.getSelection();
        if (sel.getRangeAt && sel.rangeCount) {
            range = sel.getRangeAt(0);
            range.deleteContents(); // Optional: Deletes the current selection

            // Create the break (new line) element
            br = document.createElement("br");
            range.insertNode(br);

            // Move the caret immediately after the inserted break
            range.setStartAfter(br);
            range.setEndAfter(br);
            sel.removeAllRanges();
            sel.addRange(range);
        }
    } else if (document.selection && document.selection.createRange) {
        // IE < 9
        range = document.selection.createRange();
        range.pasteHTML('<br>');
    }
}

// Get the selected text and delete it
function deleteSelectedText() {
    var sel, range;
    if (window.getSelection) {
        // Non-IE browsers
        sel = window.getSelection();
        if (sel.rangeCount) {
            range = sel.getRangeAt(0);
            range.deleteContents();
            
            // Collapse the range to the start point to move the cursor there
            range.collapse(true);
            sel.removeAllRanges();
            sel.addRange(range);
        }
    } else if (document.selection && document.selection.createRange) {
        // IE < 9
        range = document.selection.createRange();
        range.text = ""; // Setting the text content of the range to an empty string effectively deletes it
        
        // Optionally, to mimic non-IE behavior, collapse the selection to the start
        range.collapse(true);
        range.select();
    }
}

function getSelectedHtml() {
    var sel = window.getSelection();
    if (sel.rangeCount) {
        var container = document.createElement("div");
        for (var i = 0, len = sel.rangeCount; i < len; ++i) {
            container.appendChild(sel.getRangeAt(i).cloneContents());
        }
        return container.innerHTML;
    }
    return "";
}

function removeTags() {
    var sel = window.getSelection();
    const selection = getSelectedText();
    if (sel.rangeCount) {
        var container = document.createElement("div");
        for (var i = 0, len = sel.rangeCount; i < len; ++i) {
            sel.getRangeAt(i).deleteContents();
            sel.getRangeAt(i).insertNode(document.createTextNode(selection));
        }
    }
}


// HEADERS
document.getElementById('makeTextHeading1').addEventListener('click', function() {
    replaceSelectedTextHtml(getSelectedText(), 'h1')
    updateHTMLEditor();
})

document.getElementById('makeTextHeading2').addEventListener('click', function() {
    replaceSelectedTextHtml(getSelectedText(), 'h2')
    updateHTMLEditor();
})

document.getElementById('makeTextHeading3').addEventListener('click', function() {
    replaceSelectedTextHtml(getSelectedText(), 'h3')
    updateHTMLEditor();
})

document.getElementById('makeTextHeading4').addEventListener('click', function() {
    replaceSelectedTextHtml(getSelectedText(), 'h4')
    updateHTMLEditor();
})

// ALIGN
document.getElementById('makeTextAlignLeft').addEventListener('click', function() {
    replaceSelectedTextHtmlSuf(getSelectedText(), 'p class="text-left"', 'p');
    updateHTMLEditor();
})

document.getElementById('makeTextAlignCenter').addEventListener('click', function() {
    replaceSelectedTextHtmlSuf(getSelectedText(), 'p class="text-center"', 'p');
    updateHTMLEditor();
})

document.getElementById('makeTextAlignRight').addEventListener('click', function() {
    replaceSelectedTextHtmlSuf(getSelectedText(), 'p class="text-right"', 'p');
    updateHTMLEditor();
})

document.getElementById('makeTextAlignJustify').addEventListener('click', function() {
    replaceSelectedTextHtmlSuf(getSelectedText(), 'p class="text-justify"', 'p');
    updateHTMLEditor();
})

// TEXT
document.getElementById('makeTextBold').addEventListener('click', function() {
    replaceSelectedTextHtml(getSelectedText(), 'b');
    updateHTMLEditor();
})

document.getElementById('makeTextItalic').addEventListener('click', function() {
    replaceSelectedTextHtml(getSelectedText(), 'i');
    updateHTMLEditor();
})

document.getElementById('makeTextUnderline').addEventListener('click', function() {
    replaceSelectedTextHtml(getSelectedText(), 'u');
    updateHTMLEditor();
})

document.getElementById('makeTextStrikethrough').addEventListener('click', function() {
    replaceSelectedTextHtml(getSelectedText(), 's');
    updateHTMLEditor();
})

// BOXES
document.getElementById('makeTextQuote').addEventListener('click', function() {
    insertNewLineAtSelection();
    replaceSelectedTextHtmlSuf(getSelectedText(), 'blockquote', 'blockquote');
    updateHTMLEditor();
})

document.getElementById('makeCodeBox').addEventListener('click', function() {
    replaceSelectedTextHtmlSuf(getSelectedText(), 'div class="well" style="color: white;"', 'div');
    updateHTMLEditor();
})

document.getElementById('makeTextAlertSuccess').addEventListener('click', function() {
    replaceSelectedTextHtmlSuf(getSelectedText(), 'div class="alert alert-success" role="alert"', 'div');
    updateHTMLEditor();
})

document.getElementById('makeTextAlertInfo').addEventListener('click', function() {
    replaceSelectedTextHtmlSuf(getSelectedText(), 'div class="alert alert-info" role="alert"', 'div');
    updateHTMLEditor();
})

document.getElementById('makeTextAlertWarning').addEventListener('click', function() {
    replaceSelectedTextHtmlSuf(getSelectedText(), 'div class="alert alert-warning" role="alert"', 'div');
    updateHTMLEditor();
})

document.getElementById('makeTextAlertDanger').addEventListener('click', function() {
    replaceSelectedTextHtmlSuf(getSelectedText(), 'div class="alert alert-danger" role="alert"', 'div');
    updateHTMLEditor();
})

// LINK & EXTRA LINE
document.getElementById('makeTextClickableLink').addEventListener('click', function() {
    var link = "https://google.com/"
    replaceSelectedTextHtmlSuf(getSelectedText(), 'a target="_blank" href="' + link + '"', 'a');
    updateHTMLEditor();
})

// TABLE, IMAGE, VIDEO and CLOUD
document.getElementById('insertImage').addEventListener('click', function() {
    var link = "https://images.evetech.net/characters/2115356431/portrait?size=128"
    replaceSelectedTextHtmlSuf(getSelectedText(), 'img src="' + link + '" class="img-responsive"', 'img');
    updateHTMLEditor();
})

// Remove tags
document.getElementById('remoteTextTags').addEventListener('click', function() {
    removeTags();
    updateHTMLEditor();
})


