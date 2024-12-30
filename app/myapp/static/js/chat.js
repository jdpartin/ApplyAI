// Chat Bubble and Chat Container Logic
document.addEventListener('DOMContentLoaded', () => {
    const chatBubble = document.getElementById('chatBubble');
    const chatContainer = document.getElementById('chatContainer');
    const fullscreenToggle = document.getElementById('fullscreenToggle');

    // Toggle Chat Visibility
    chatBubble.addEventListener('click', () => {
        chatContainer.style.transform = 'translateY(0)';
    });

    // Toggle Fullscreen Mode
    fullscreenToggle.addEventListener('click', () => {
        chatContainer.classList.toggle('fullscreen');
    });

    // Close Chat when clicking outside (optional enhancement)
    document.addEventListener('click', (event) => {
        if (!chatContainer.contains(event.target) && !chatBubble.contains(event.target)) {
            chatContainer.style.transform = 'translateY(100%)';
            chatContainer.classList.remove('fullscreen');
        }
    });
});
