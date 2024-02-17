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

// HEADERS

// ALIGN
document.getElementById('makeTextAlignLeft').addEventListener('click', function() {
    replaceSelectedTextHtmlSuf(getSelectedText(), 'p class="text-left"', 'p');
})

document.getElementById('makeTextAlignCenter').addEventListener('click', function() {
    replaceSelectedTextHtmlSuf(getSelectedText(), 'p class="text-center"', 'p');
})

document.getElementById('makeTextAlignRight').addEventListener('click', function() {
    replaceSelectedTextHtmlSuf(getSelectedText(), 'p class="text-right"', 'p');
})

document.getElementById('makeTextAlignJustify').addEventListener('click', function() {
    replaceSelectedTextHtmlSuf(getSelectedText(), 'p class="text-justify"', 'p');
})

// TEXT
document.getElementById('makeTextBold').addEventListener('click', function() {
    replaceSelectedTextHtml(getSelectedText(), 'b');
})

document.getElementById('makeTextItalic').addEventListener('click', function() {
    replaceSelectedTextHtml(getSelectedText(), 'i');
})

document.getElementById('makeTextUnderline').addEventListener('click', function() {
    replaceSelectedTextHtml(getSelectedText(), 'u');
})

document.getElementById('makeTextStrikethrough').addEventListener('click', function() {
    replaceSelectedTextHtml(getSelectedText(), 's');
})

// BOXES
document.getElementById('makeTextQuote').addEventListener('click', function() {
    replaceSelectedTextHtmlSuf(getSelectedText(), 'blockquote', 'blockquote');
})

document.getElementById('makeCodeBox').addEventListener('click', function() {
    replaceSelectedTextHtmlSuf(getSelectedText(), 'div class="well" style="color: white;"', 'div');
})

document.getElementById('makeAlertSuccess').addEventListener('click', function() {
    replaceSelectedTextHtmlSuf(getSelectedText(), 'div class="alert alert-success" role="alert"', 'div');
})

// LINK & EXTRA LINE


