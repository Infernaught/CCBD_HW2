// Wait for the document to be ready
$(document).ready(function() {
    var sdk = apigClientFactory.newClient({});
    const userInputField = $('#userInput');
    const submitButton = $('#submitButton');
    const userMessageDiv = $('#userMessage');

    function callChatbotApi(message) {
        // params, body, additionalParams
        console.log(message)
        return sdk.searchGet({q: message});
    }

    // Function to handle user input submission
    function submitUserInput() {
      const userInput = userInputField.val();
      if ($.trim(userInput) !== '') {
        // send the message to API
        callChatbotApi(userInput)
            .then((response) => {
                console.log(response);
                var data = response.data;

                if (data.messages && data.messages.length > 0) {
                console.log('received ' + data.messages.length + ' messages');

                var messages = data.messages;

                for (var message of messages) {
                    appendDisplay(message.labels);
                }
                } else {
                insertResponseMessage('Oops, something went wrong. Please try again.');
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
});