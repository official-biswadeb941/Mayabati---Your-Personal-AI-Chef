// Simulate typing effect
function simulateTyping(message, element) {
    let index = 0;
    const typingSpeed = 25; // Adjust typing speed as needed
    function type() {
    if (index < message.length) {
    element.innerHTML += message.charAt(index);
    index++;
    setTimeout(type, typingSpeed);
    }
    }
    type();
    }
    
    // Function to toggle the "Send" button based on input field content
    function toggleSendButton(inputField) {
    const sendButton = document.getElementById('sendButton');
    if (inputField.value.trim() !== '') {
    sendButton.classList.add('active'); // Add the 'active' class for green color highlight
    } 
    else 
    {
    sendButton.classList.remove('active'); // Remove the 'active' class
    }
    }
    
    // Simulate blinking cursor
    function blinkCursor(cursorElement) {
    setInterval(function () {
    if (cursorElement.style.display === 'none') {
    cursorElement.style.display = 'inline';
    }
    else 
    {
    cursorElement.style.display = 'none';
    }
    }, 500); // Adjust blinking speed as needed
    }
    
    // Function to toggle the "Send" button based on input field content
    function toggleSendButton(inputField) {
    const sendButton = document.getElementById('sendButton');
    if (inputField.value.trim() !== '') {
    sendButton.removeAttribute('disabled');
    } 
    else 
    {
    sendButton.setAttribute('disabled', 'disabled');
    }
    }
    
    // Function to handle "Enter" key press and send message
    function handleKeyPress(event) {
    if (event.keyCode === 13) {
    event.preventDefault();
    sendMessageIfNotEmpty();
    }
    }
    
    // Function to send a message if the input is not empty
    function sendMessageIfNotEmpty() {
    const userMessage = document.getElementById('user_input').value.trim();
    if (userMessage !== '') {
    sendMessage();
    }
    }
    
    // Modify the sendMessage() function to only send non-empty messages
    function sendMessage() {
        const userMessage = document.getElementById('user_input').value.trim();
    
        if (userMessage !== '') {
          document.getElementById('user_input').value = '';
    
          // Append user's message to the chatbox with typing effect
          const userDiv = document.createElement('div');
          userDiv.className = 'user-message';
          document.getElementById('chatbox').appendChild(userDiv);
          simulateTyping(userMessage, userDiv);
        }
    
    // Send the user's message to the server for processing
    fetch('/api/chat', {
            method: 'POST',
            body: JSON.stringify({ message: userMessage }),
            headers: { 'Content-Type': 'application/json' },
          })
            .then((response) => response.json())
            .then((data) => {
              const botResponse = data.message;
    
              if (Array.isArray(botResponse)) {
                displayBotResponseSequentially(botResponse);
              } else {
                displayBotResponse(botResponse);
              }
            
            });
        }
    
    // Function to display bot's response
    function displayBotResponse(response) {
        const botDiv = document.createElement('div');
        botDiv.className = 'bot-message';
        document.getElementById('chatbox').appendChild(botDiv);
        simulateTyping(response, botDiv);
    
        // Scroll to the bottom of the chatbox to show the latest message
        document.getElementById('chatbox').scrollTop = document.getElementById('chatbox').scrollHeight;
    }
    
    // Function to display bot's response sequentially
    function displayBotResponseSequentially(responseList) {
        const chatbox = document.getElementById('chatbox');
        let currentIndex = 0;
        function displayNextLine() {
            if (currentIndex < responseList.length) {
                const botDiv = document.createElement('div');
                botDiv.className = 'bot-message';
                chatbox.appendChild(botDiv);
                simulateTyping(responseList[currentIndex], botDiv);
                currentIndex++;
                // Scroll to the bottom of the chatbox to show the latest message
                chatbox.scrollTop = chatbox.scrollHeight;
            }
        }
    
    // Start displaying lines one by one
    setInterval(displayNextLine, 1000); // Adjust the interval as needed
    }
    // Start the blinking cursor effect
    const cursorElement = document.createElement('span');
    cursorElement.className = 'cursor';
    cursorElement.innerHTML = '|';
    document.querySelector('.type_msg').appendChild(cursorElement);
    blinkCursor(cursorElement);
    
      // Hide the preloader when the page is fully loaded
      window.addEventListener('load', function() {
        const preloader = document.querySelector('.cyclic-preloader');
        preloader.style.display = 'none';
      });
    
      var botHtml = '<div class="d-flex justify-content-start mb-4">' +
        '<div class="img_cont_msg">' +
        '<img src="https://i.ibb.co/fSNP7Rz/icons8-chatgpt-512.png" class="rounded-circle user_img_msg">' +
        '<span class="message-indicator">🤖</span>' + // Add the indicator here
        '</div>' +
        '<div class="msg_cotainer">' + data +
        '</div>' +
        '</div>';
    $("#messageFormeight").append($.parseHTML(botHtml));
    