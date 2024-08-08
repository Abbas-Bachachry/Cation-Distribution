document.addEventListener('DOMContentLoaded', (event) => {
    const socket = io.connect('http://' + document.domain + ':' + location.port);
    
    socket.on('connect', () => {
        console.log('Connected to the server');
    });

    socket.on('task_done', (data) => {
        console.log('Received task_done event');
        displayAlertMessage(data.message, 'info');  // 'info' for task_done event
    });

    socket.on('task_error', (data) => {
        console.log('Received task_error event');
        displayAlertMessage(data.message, 'error');  // 'error' for task_error event
    });

    socket.on('disconnect', () => {
        console.log('Disconnected from the server');
    });
});

function displayAlertMessage(message, type) {
    const alertContainer = document.getElementById('alert-container');
    const alertMessage = document.createElement('div');
    alertMessage.classList.add('alert-message');
    if (type === 'error') {
        alertMessage.classList.add('alert-error');
    } else if (type === 'info') {
        alertMessage.classList.add('alert-info');
    }
    alertMessage.innerText = message;
    alertContainer.appendChild(alertMessage);
    alertContainer.style.display = 'block';

    // Automatically hide the message after 5 seconds
    setTimeout(() => {
        alertMessage.remove();
        if (alertContainer.children.length === 0) {
            alertContainer.style.display = 'none';
        }
    }, 10000);
}
