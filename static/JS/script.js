document.addEventListener("DOMContentLoaded", function () {
  var messages = document.querySelectorAll(".message");
  var logoContainer = document.querySelector('.logo-container');

  // Select the target node
  var targetNode = document.getElementById('chatbox'); // Replace 'chatbox' with the actual ID of your chatbox element

  // Create an observer instance
  var observer = new MutationObserver(function (mutations) {
    mutations.forEach(function (mutation) {
      if (mutation.type === 'childList') {
        var addedNodes = mutation.addedNodes;
        addedNodes.forEach(function (node) {
          // Check if the added node is a message
          if (node.classList.contains('message')) {
            var label = node.querySelector(".message-text-label");
            if (label) {
              label.style.display = "inline";
              hideLogoContainer();
            }
          }
        });
      }
    });
  });

  // Configuration of the observer
  var config = { childList: true };

  // Start observing the target node for configured mutations
  observer.observe(targetNode, config);

  function hideLogoContainer() {
    logoContainer.style.display = 'none';
    document.removeEventListener('keydown', hideLogoContainer);
  }

  document.addEventListener('keydown', function (event) {
    if (event.keyCode === 13) { // Check for Enter key
      hideLogoContainer();
      sendMessageIfNotEmpty();
    }
  });

  function simulateTyping(message, element) {
    // Simulate typing effect
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

  function toggleSendButton(inputField) {
    // Function to toggle the "Send" button based on input field content
    const sendButton = document.getElementById('sendButton');
    if (inputField.value.trim() !== '') {
      sendButton.removeAttribute('disabled');
      sendButton.classList.add('active'); // Add the 'active' class for green color highlight
    } else {
      sendButton.setAttribute('disabled', 'disabled');
      sendButton.classList.remove('active'); // Remove the 'active' class
    }
  }

  function blinkCursor(cursorElement) {
    // Simulate blinking cursor
    setInterval(function () {
      if (cursorElement.style.display === 'none') {
        cursorElement.style.display = 'inline';
      } else {
        cursorElement.style.display = 'none';
      }
    }, 500); // Adjust blinking speed as needed
  }

  function sendMessageIfNotEmpty() {
    // Function to send a message if the input is not empty
    const userMessage = document.getElementById('user_input').value.trim();
    if (userMessage !== '') {
      sendMessage();
    }
  }

  function sendMessage() {
    // Modify the sendMessage() function to only send non-empty messages
    const userMessage = document.getElementById('user_input').value.trim();

    if (userMessage !== '') {
      document.getElementById('user_input').value = '';

      // Append user's message to the chatbox with typing effect and user avatar
      const userDiv = document.createElement('div');
      userDiv.className = 'user-message';
      document.getElementById('chatbox').appendChild(userDiv);

      // Avatar for user
      const userAvatar = document.createElement('div');
      userAvatar.className = 'avatar';
      userAvatar.innerHTML = '<img src="https://cdn-icons-png.flaticon.com/512/6596/6596121.png" alt=" User Avatar">';
      userDiv.appendChild(userAvatar);

      // Typing effect for user message
      simulateTyping(userMessage, userDiv);
    }

    // Send the user's message to the server for processing
    fetch('/chat', {
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

  function displayBotResponse(response) {
    // Function to display bot's response
    const botDiv = document.createElement('div');
    botDiv.className = 'bot-message';
    document.getElementById('chatbox').appendChild(botDiv);

    // Avatar for bot
    const botAvatar = document.createElement('div');
    botAvatar.className = 'avatar';
    botAvatar.innerHTML = '<img src="https://cdn.leonardo.ai/users/5e0f042e-ecf8-40b4-b267-d22a266ffa23/generations/8489dd4d-4996-4248-a86e-5498af5af5ac/DreamShaper_v7_Mayabati_as_a_chef_in_kitchen_cooking_food_0.jpg" alt="  Bot Avatar">';
    botDiv.appendChild(botAvatar);

    // Typing effect for bot response
    simulateTyping(response, botDiv);

    // Scroll to the bottom of the chatbox to show the latest message
    document.getElementById('chatbox').scrollTop = document.getElementById('chatbox').scrollHeight;
  }

  function displayBotResponseSequentially(responseList) {
    // Function to display bot's response sequentially
    const chatbox = document.getElementById('chatbox');
    let currentIndex = 0;

    function displayNextLine() {
      if (currentIndex < responseList.length) {
        const botDiv = document.createElement('div');
        botDiv.className = 'bot-message';
        chatbox.appendChild(botDiv);

        // Avatar for bot (add this block only for the first line)
        if (currentIndex === 0) {
          const botAvatar = document.createElement('div');
          botAvatar.className = 'avatar';
          botAvatar.innerHTML = '<img src="https://cdn.leonardo.ai/users/5e0f042e-ecf8-40b4-b267-d22a266ffa23/generations/8489dd4d-4996-4248-a86e-5498af5af5ac/DreamShaper_v7_Mayabati_as_a_chef_in_kitchen_cooking_food_0.jpg" alt="Bot Avatar">';
          botDiv.appendChild(botAvatar);
        }

        // Typing effect for bot response
        simulateTyping(responseList[currentIndex], botDiv);
        currentIndex++;

        // Scroll to the bottom of the chatbox to show the latest message
        chatbox.scrollTop = chatbox.scrollHeight;
      }
    }

    // Start displaying lines one by one
    setInterval(displayNextLine, 1000); // Adjust the interval as needed
  }

  const cursorElement = document.createElement('span');
  cursorElement.className = 'cursor';
  cursorElement.innerHTML = '|';
  document.querySelector('.type_msg').appendChild(cursorElement);
  blinkCursor(cursorElement);

});

