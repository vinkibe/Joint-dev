// script.js

function deleteDocument(documentId) {
    if (confirm('Are you sure you want to delete this document?')) {
        fetch(`/delete_document/${documentId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => {
                if (response.ok) {
                    location.reload();
                } else {
                    alert('Error deleting document');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error deleting document');
            });
    }
}


// script.js

function addDocument() {
    const form = document.createElement('form');
    form.enctype = 'multipart/form-data';

    const titleInput = document.createElement('input');
    titleInput.type = 'text';
    titleInput.name = 'title';
    titleInput.placeholder = 'Enter document title';

    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.name = 'file';

    const submitButton = document.createElement('button');
    submitButton.type = 'button';
    submitButton.textContent = 'Upload Document';
    submitButton.addEventListener('click', () => {
        const formData = new FormData(form);

        fetch('/add_document/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: formData
            })
            .then(response => {
                if (response.ok) {
                    location.reload();
                } else {
                    alert('Error adding document');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error adding document');
            });
    });

    form.appendChild(titleInput);
    form.appendChild(fileInput);
    form.appendChild(submitButton);

    // Display the form in a modal or as part of your page layout
    // Example: Show it as a prompt
    const promptResult = prompt('Enter document details:');
    if (promptResult !== null) {
        document.body.appendChild(form);
    }
}

function openDocument(url) {
    window.open(url, '_blank');
}
// document.addEventListener('DOMContentLoaded', function() {
//     const documentTitles = document.querySelectorAll('.document-title');
//     documentTitles.forEach(title => {
//         title.addEventListener('click', function() {
//             const documentUrl = title.dataset.documentUrl;
//             window.open(documentUrl, '_blank');
//         });
//     });
// });

// Function to get CSRF token for AJAX requests
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}