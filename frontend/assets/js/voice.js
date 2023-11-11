const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;
  
const stat = document.getElementById("status"),
    output = document.getElementById("result");

function startRecognition() {
    if (SpeechRecognition !== undefined) {
    let recognition = new SpeechRecognition();

    recognition.onstart = () => {
        stat.innerHTML = `Currently listening: `;
        output.classList.add("hide");
    };

    recognition.onspeechend = () => { // CHENGYU LOOK HERE!!! CHANGE THIS BEHAVIOR!!!
        stat.innerHTML = `Stopped listening.`;
        recognition.stop();
    };

    recognition.onresult = (result) => {
        const userInputField = $('#userInput');
        output.classList.remove("hide");
        //output.innerHTML = `I'm ${Math.floor(
        //result.results[0][0].confidence * 100
        //)}% certain you just said: <b>${result.results[0][0].transcript}</b>`;
        userInputField.val(result.results[0][0].transcript);
        submitUserInput();

    };

    recognition.start();
    } else {
    stat.innerHTML = "sorry not supported 😭";
    }
};