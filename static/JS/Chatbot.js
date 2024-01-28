document.addEventListener("DOMContentLoaded", function() {
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const chatMessages = document.getElementById('chat-messages');
    let selectedImage = null;

    // Send message when send button clicked or enter pressed
    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault(); // Prevent the default form submission behavior
            
            if (userInput.value.trim() !== '' || selectedImage) {
                sendMessage();
            }
        }
    });

    // Camera button functionality
    const cameraBtn = document.querySelector('.camera-btn');
    const fileInput = document.getElementById('file-input');
    cameraBtn.addEventListener('click', function() {
        fileInput.click();
    });

    fileInput.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            // Display the selected image in the text box
            displayImageInTextBox(file);
            selectedImage = file;
            
            // Clear placeholder text
            userInput.placeholder = '';
            
            // Add class to input to adjust styling
            userInput.classList.add('with-image');
            
            // Set focus on the text box
            userInput.focus();
        } else {
            // Remove the image-related class when no image is selected
            userInput.classList.remove('with-image');
        }
    });

    function sendMessage() {
        let userMessage = userInput.value.trim();
        if (!userMessage && !selectedImage) return;
    
        // Hide the logo container
        document.querySelector('.logo-container').style.display = 'none';
    
        // Disable the text box
        userInput.disabled = true;
    
        if (selectedImage) {
            // Send the selected image with description
            appendMessage('You', userMessage, true, selectedImage);
        } else {
            // Send text message only
            appendMessage('You', userMessage, true);
        }
    
        userInput.value = ''; // Clear the input box after sending a message
        userInput.style.backgroundImage = ''; // Clear any background image
    
        // Reset selected image
        selectedImage = null;
        userInput.classList.remove('with-image');
    
        // Simulate Bot response
        simulateBotResponse(userMessage);
    }
    
    function simulateBotResponse(userMessage) {
        // Display "Bot is thinking" message
        const thinkingMessage = document.createElement('div');
        thinkingMessage.classList.add('thinking-message');
        thinkingMessage.textContent = "Bot is thinking...";
        chatMessages.appendChild(thinkingMessage);
    
        // Simulate Bot response after a delay
        setTimeout(() => {
            if (selectedImage) {
                // If an image is selected, handle sending the image to the bot
                sendImageToBot(selectedImage, userMessage);
            } else {
                // If it's a text message, make an API call to Flask backend
                fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ message: userMessage })
                })
                .then(response => response.json())
                .then(data => {
                    // Remove "Bot is thinking" message
                    chatMessages.removeChild(thinkingMessage);
                    
                    // Append bot response to chat window
                    appendMessage('Mayabati', data.message, false);
    
                    // Re-enable the text box after bot response is complete
                    userInput.disabled = false;
                })
                .catch(error => {
                    console.error('Error:', error);
    
                    // Re-enable the text box if an error occurs during bot response
                    userInput.disabled = false;
                });
            }
        }, Math.random() * 2000 + 1000); // Simulated delay between 1 to 3 seconds
    }
    

    function appendMessage(sender, message, fromMe, image, senderAvatarType, senderAvatar) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message');
        if (fromMe) {
            messageElement.classList.add('from-me');
        } else {
            messageElement.classList.add('from-user');
        }
        const timestamp = `<span class="timestamp">${getCurrentTime()}</span>`;
        let messageContent = '';
        if (image) {
            messageContent = `<div class="avatar ${fromMe ? 'user-img' : ''}">
                                <img src="${fromMe ? senderAvatar : 'chatgpt_avatar.png'}" alt="${sender}">
                              </div>
                              <span class="user">${sender}</span>
                              <span class="text">${message}</span>
                              <img src="${URL.createObjectURL(image)}" style="max-width: 100px;">`;
        } else {
            messageContent = `<div class="avatar ${fromMe ? 'user-img' : ''}">
                                <img src="${senderAvatarType === 'online' ? senderAvatar : 'chatgpt_avatar.png'}" alt="${sender}">
                              </div>
                              <span class="user">${sender}</span>
                              <span class="text">${message}</span>`;
        }
        messageElement.innerHTML = `
            ${messageContent}
            ${timestamp}
        `;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function getCurrentTime() {
        const now = new Date();
        const hours = now.getHours().toString().padStart(2, '0');
        const minutes = now.getMinutes().toString().padStart(2, '0');
        return `${hours}:${minutes}`;
    }

    function displayImageInTextBox(file) {
        // Display the selected image in the text box
        const reader = new FileReader();
        reader.onload = function(e) {
            userInput.style.backgroundImage = `url(${e.target.result})`;
        };
        reader.readAsDataURL(file);
    }
    function sendImageToBot(imageFile, description) {
        // Display the selected image in the chat
        appendMessage('You', '<img src="' + URL.createObjectURL(imageFile) + '" style="max-width: 100px;">', true);
        appendMessage('You', description, true);
    
        // Here you would implement logic to send the image file and its description to the bot
        // For demonstration purposes, we're not sending the image to the bot directly in this example
    }
    
    
    });