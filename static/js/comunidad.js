// comunidad.js - Funcionalidad para la página de comunidad

document.addEventListener('DOMContentLoaded', function() {
    // Mostrar/ocultar formulario de creación de posts
    const createPostBtn = document.getElementById('create-post-btn');
    const postFormContainer = document.getElementById('post-form-container');
    const cancelPostBtn = document.getElementById('cancel-post-btn');
    
    if (createPostBtn && postFormContainer) {
        createPostBtn.addEventListener('click', function() {
            postFormContainer.style.display = 'block';
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
        
        cancelPostBtn.addEventListener('click', function() {
            postFormContainer.style.display = 'none';
        });
    }
    
    // Manejar likes
    document.querySelectorAll('.like-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const postId = this.dataset.postId;
            toggleLike(postId, this);
        });
    });
    
    // Manejar comentarios (mostrar/ocultar sección)
    document.querySelectorAll('.comment-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const postId = this.dataset.postId;
            const commentsSection = document.querySelector(`.comments-section[data-post-id="${postId}"]`);
            
            if (commentsSection.style.display === 'none') {
                // Cargar comentarios si no están cargados
                if (commentsSection.querySelector('.comments-list').children.length === 0) {
                    loadComments(postId);
                }
                commentsSection.style.display = 'block';
            } else {
                commentsSection.style.display = 'none';
            }
        });
    });
    
    // Manejar eliminación de posts
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const postId = this.dataset.postId;
            if (confirm('¿Estás seguro de que quieres eliminar esta publicación?')) {
                deletePost(postId);
            }
        });
    });
    
    // Manejar envío de comentarios
    document.querySelectorAll('.add-comment-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const postId = this.dataset.postId;
            const content = this.querySelector('textarea').value.trim();
            
            if (content) {
                addComment(postId, content, this);
            }
        });
    });
});

// Función para alternar like
function toggleLike(postId, button) {
    fetch(`/comunidad/toggle_like/${postId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        if (data.liked) {
            button.classList.add('liked');
        } else {
            button.classList.remove('liked');
        }
        
        // Actualizar contador de likes
        const postCard = button.closest('.post-card');
        if (postCard) {
            const likesCount = postCard.querySelector('.likes-count');
            if (likesCount) {
                likesCount.textContent = `${data.likes_count} likes`;
            }
        }
    })
    .catch(error => console.error('Error:', error));
}

// Función para cargar comentarios
function loadComments(postId) {
    fetch(`/comunidad/obtener_comentarios/${postId}/`)
    .then(response => response.json())
    .then(data => {
        const commentsList = document.querySelector(`.comments-section[data-post-id="${postId}"] .comments-list`);
        commentsList.innerHTML = '';
        
        data.comentarios.forEach(comment => {
            const commentElement = document.createElement('div');
            commentElement.className = 'comment';
            commentElement.innerHTML = `
                <div class="comment-avatar">${comment.usuario.charAt(0).toUpperCase()}</div>
                <div class="comment-content">
                    <div class="comment-user">${comment.usuario}</div>
                    <div class="comment-text">${comment.contenido}</div>
                    <div class="comment-time">${comment.fecha}</div>
                </div>
            `;
            commentsList.appendChild(commentElement);
        });
    })
    .catch(error => console.error('Error:', error));
}

// Función para agregar comentario
function addComment(postId, content, form) {
    fetch(`/comunidad/agregar_comentario/${postId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ contenido: content }),
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Limpiar el textarea
            form.querySelector('textarea').value = '';
            
            // Agregar el nuevo comentario a la lista
            const commentsList = form.previousElementSibling;
            const commentElement = document.createElement('div');
            commentElement.className = 'comment';
            commentElement.innerHTML = `
                <div class="comment-avatar">${data.comentario.usuario.charAt(0).toUpperCase()}</div>
                <div class="comment-content">
                    <div class="comment-user">${data.comentario.usuario}</div>
                    <div class="comment-text">${data.comentario.contenido}</div>
                    <div class="comment-time">${data.comentario.fecha}</div>
                </div>
            `;
            commentsList.appendChild(commentElement);
            
            // Actualizar contador de comentarios
            const postCard = form.closest('.post-card');
            if (postCard) {
                const commentsCount = postCard.querySelector('.comments-count');
                if (commentsCount) {
                    commentsCount.textContent = `${data.comments_count} comentarios`;
                }
            }
        } else {
            console.error('Error al agregar comentario:', data.errors);
        }
    })
    .catch(error => console.error('Error:', error));
}

// Función para eliminar post
function deletePost(postId) {
    fetch(`/comunidad/eliminar_post/${postId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Recargar la página para reflejar los cambios
            window.location.reload();
        }
    })
    .catch(error => console.error('Error:', error));
}

// Función auxiliar para obtener cookies
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