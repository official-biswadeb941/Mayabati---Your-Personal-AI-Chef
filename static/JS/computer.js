document.addEventListener("DOMContentLoaded", function () {
  var logoContainer = document.querySelector('.logo-container');
  var messageInput = document.getElementById('user_input');
  var cursorElement = createCursorElement();

  // WebRTC
  const socket = io.connect('http://' + document.domain + ':' + location.port);
  socket.on('connect', function () {
    console.log('Socket.io connected');
  });

  const peer = new SimplePeer({ initiator: location.hash === '#init' });

  peer.on('data', function (data) {
    const message = data.toString();
    displayBotResponse(message);
  });

  peer.on('iceConnectionStateChange', handleICEConnectionStateChange);

  messageInput.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      hideLogoContainer();
      sendMessageIfNotEmpty();
    }
  });

  observeNewMessages();
  blinkCursor(cursorElement);
  function createCursorElement() {
    const cursorElement = document.createElement('span');
    cursorElement.className = 'cursor';
    cursorElement.innerHTML = '|';
    document.querySelector('.type_msg').appendChild(cursorElement);
    return cursorElement;
  }

  function hideLogoContainer() {
    logoContainer.style.display = 'none';
    document.removeEventListener('keydown', hideLogoContainer);
  }

  function observeNewMessages() {
    var targetNode = document.getElementById('chatbox');
    var observer = new MutationObserver(function (mutations) {
      mutations.forEach(function (mutation) {
        if (mutation.type === 'childList') {
          var addedNodes = mutation.addedNodes;
          addedNodes.forEach(function (node) {
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

    var config = { childList: true };
    observer.observe(targetNode, config);
  }

  function simulateTyping(message, element) {
    let index = 0;
    const typingSpeed = 25;
    function type() {
      if (index < message.length) {
        element.innerHTML += message.charAt(index);
        index++;
        setTimeout(type, typingSpeed);
      }
    }
    type();
  }

  function sendMessageIfNotEmpty() {
    const userMessage = messageInput.value.trim();
    if (userMessage !== '') {
      sendMessage(userMessage);
    }
  }

  function sendMessage(userMessage) {
    messageInput.value = '';
    const userDiv = createMessageDiv('user-message');
    const userAvatar = createAvatar('https://cdn-icons-png.flaticon.com/512/6596/6596121.png');
    userDiv.appendChild(userAvatar);
    simulateTyping(userMessage, userDiv);

    fetch('/chat', {
      method: 'POST',
      body: JSON.stringify({ message: userMessage }),
      headers: { 'Content-Type': 'application/json' },
    })
    .then(response => response.json())
    .then(data => {
      const botResponse = data.message;
      if (Array.isArray(botResponse)) {
        displayBotResponseSequentially(botResponse);
      } else {
        displayBotResponse(botResponse);
      }
    });
  }

  function createMessageDiv(className) {
    const messageDiv = document.createElement('div');
    messageDiv.className = className;
    document.getElementById('chatbox').appendChild(messageDiv);
    return messageDiv;
  }

  function createAvatar(src) {
    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.innerHTML = `<img src="${src}" alt="User Avatar">`;
    return avatar;
  }

  function displayBotResponse(response) {
    const botDiv = createMessageDiv('bot-message');
    const botAvatar = createAvatar('https://cdn.leonardo.ai/users/5e0f042e-ecf8-40b4-b267-d22a266ffa23/generations/8489dd4d-4996-4248-a86e-5498af5af5ac/DreamShaper_v7_Mayabati_as_a_chef_in_kitchen_cooking_food_0.jpg');
    botDiv.appendChild(botAvatar);
    simulateTyping(response, botDiv);
    document.getElementById('chatbox').scrollTop = document.getElementById('chatbox').scrollHeight;
  }

  function displayBotResponseSequentially(responseList) {
    const chatbox = document.getElementById('chatbox');
    let currentIndex = 0;
    function displayNextLine() {
      if (currentIndex < responseList.length) {
        const botDiv = createMessageDiv('bot-message');
        // Display avatar only during the first line
        if (currentIndex === 0) {
          const botAvatar = createAvatar('https://cdn.leonardo.ai/users/5e0f042e-ecf8-40b4-b267-d22a266ffa23/generations/8489dd4d-4996-4248-a86e-5498af5af5ac/DreamShaper_v7_Mayabati_as_a_chef_in_kitchen_cooking_food_0.jpg');
          botDiv.appendChild(botAvatar);
        }
        simulateTyping(responseList[currentIndex], botDiv);
        currentIndex++;
        chatbox.scrollTop = chatbox.scrollHeight;
      } else {
        // Stop the interval after all lines are displayed
        clearInterval(intervalId);
      }
    }
    // Set interval to display the next line every 1000 milliseconds
    const intervalId = setInterval(displayNextLine, 1000);
  }
  
  function blinkCursor(cursorElement) {
    setInterval(function () {
      cursorElement.style.display = (cursorElement.style.display === 'none') ? 'inline' : 'none';
    }, 500);
  }

  function handleICEConnectionStateChange() {
    if (peer.iceConnectionState === 'connected') {
      sendWebRTCData('Hello, WebRTC!');
    }
  }

  function sendWebRTCData(message) {
    if (peer && peer.iceConnectionState === 'connected') {
      peer.send(message);
    }
  }
});
