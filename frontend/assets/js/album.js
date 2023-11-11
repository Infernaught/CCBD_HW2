// Wait for the document to be ready
$(document).ready(function() {
    var sdk = apigClientFactory.newClient({});
    const userInputField = $('#userInput');
    const submitButton = $('#submitButton');
    const userMessageDiv = $('#userMessage');
    const displayCanvas = $('.canvas');
    const maxWidth = 50;
    const maxHeight = 50;

    function callChatbotApi(message) {
        // params, body, additionalParams
        console.log(message)
        return sdk.searchGet({q: message});
    }

    // Function to handle user input submission
    window.submitUserInput = function() {
      const userInput = userInputField.val();
      //userInputField.val('');
      if ($.trim(userInput) !== '') {
        // send the message to API
        displayCanvas.empty();
        callChatbotApi(userInput)
            .then((response) => {
                console.log(response);
                var data = response.data.results;
                if (data && data.length > 1) {
                    console.log('received ' + (data.length - 1) + ' matches');
                    var displaySet = new Set();
                    labels = data[0].labels;
                    var label_text = 'Image with label "';
                    if (labels.length == 1) {
                        label_text += labels[0] + '"';
                    } else {
                        label_text += labels[0] + '" and "' + labels[1] + '"';
                    }
                    displayCanvas.append($('<h2>').text(label_text));
                    for (let i = 1; i < data.length; i++) {
                        if (displaySet.has(data[i].url)) {
                            continue;
                        } else {
                            displaySet.add(data[i].url);
                            var img = $('<img>')
                            img.attr('src', data[i].url);
                            img.attr('title', data[i].labels);
                            // img.load(function(){
                            //     var ratio = Math.min(maxWidth / $(this).width(), maxHeight / $(this).height());
                            //     console.log(ratio);
                            //     console.log($(this).height());
                            //     $(this).attr('width', $(this).width() * ratio);
                            //     $(this).attr('height', $(this).height() * ratio);
                            // });
                            img.appendTo(displayCanvas);
                        }
                    }
                } else {
                    console.log('Oops, something went wrong. Please try again.');
                }
            })
            .catch((error) => {
                console.log('an error occurred', error);
            });
      }
    }

    function appendDisplay(text) {
        const userMessage = $('<p>').text(text);
        userMessageDiv.append(userMessage);
        userInputField.val('');
    }

    // Add event listeners for button click and Enter key press
    submitButton.click(submitUserInput);
    userInputField.keydown(function(event) {
      if (event.key === 'Enter') {
        submitUserInput();
      }
    });

    $('input[name=imgUpload]').change(function () {
        var input_label = $('<input>');
        input_label.attr('type', 'text');
        input_label.attr('id','labelInput');
        input_label.attr('placeholder', '(optional) add custom label');
        input_label.attr("style", 'width:200px;');
        $('#uploadResult').append(input_label);
        var upload_button = $('<button>')
        upload_button.attr('id', 'upload');
        upload_button.html('Upload');
        $('#uploadResult').append(upload_button);
    });

    $('#upload').on('click', function () {
        var file_data = $('#file').prop('files');
        // TODO - gateway and upload to S3
        console.log("hi");
    });
});