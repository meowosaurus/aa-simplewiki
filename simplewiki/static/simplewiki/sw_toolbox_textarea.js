function insertTag(prefix, suffix) {
    const textarea = document.getElementById('editable');
    const startPos = textarea.selectionStart;
    const endPos = textarea.selectionEnd;

    textarea.append()

    console.log(startPos);
    console.log(endPos);
}

function wrapSelectedTextWithPTagsInTextarea() {
    const textarea = document.getElementById('editable');
    const startPos = textarea.selectionStart;
    const endPos = textarea.selectionEnd;
    const selectedText = textarea.value.substring(startPos, endPos);

    // Concatenate new value
    const beforeText = textarea.value.substring(0, startPos);
    const afterText = textarea.value.substring(endPos);
    const newValue = beforeText + '<h1>' + selectedText + '</h1>' + afterText;

    // Set the new value back to the textarea
    textarea.value = newValue;

    // Optional: Set selection to just after the inserted </p>
    textarea.setSelectionRange(endPos + 4, endPos + 4); // 4 characters for '</p>'
    textarea.focus(); // Bring focus back to the textarea
}

document.getElementById('makeTextAlignLeft').addEventListener('click', function() {
    var editable = document.getElementById('editable');

    var virtualTextarea = document.createElement('textarea');
    virtualTextarea.value = 'Some initial text for the textarea. Select a portion of this text.';

    // To "select" text programmatically in this virtual textarea, you would set selectionStart and selectionEnd    
    virtualTextarea.selectionStart = 5; // Start of the selection
    virtualTextarea.selectionEnd = 12; // End of the selection

    // Accessing the selected text
    var selectedText = virtualTextarea.value.substring(virtualTextarea.selectionStart, virtualTextarea.selectionEnd);
    console.log('Selected text:', selectedText);
})