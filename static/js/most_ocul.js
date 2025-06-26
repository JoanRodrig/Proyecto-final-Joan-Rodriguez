/**
 * Funcionalidad para mostrar/ocultar contraseñas
 */

// Función principal para alternar visibilidad
function togglePasswordVisibility(toggleButton, targetInput) {
    const input = targetInput;
    const icon = toggleButton.querySelector('span');
    
    if (input.type === 'password') {
        // Mostrar contraseña
        input.type = 'text';
        icon.className = 'hide-icon';
        toggleButton.setAttribute('aria-label', 'Ocultar contraseña');
        toggleButton.setAttribute('title', 'Ocultar contraseña');
    } else {
        // Ocultar contraseña
        input.type = 'password';
        icon.className = 'show-icon';
        toggleButton.setAttribute('aria-label', 'Mostrar contraseña');
        toggleButton.setAttribute('title', 'Mostrar contraseña');
    }
}

// Función para inicializar un toggle específico
function initializePasswordToggle(toggleButton) {
    const targetId = toggleButton.getAttribute('data-target');
    const targetInput = document.getElementById(targetId);
    
    if (!targetInput) {
        console.warn(`No se encontró el input con ID: ${targetId}`);
        return;
    }
    
    // Configurar atributos iniciales
    toggleButton.setAttribute('aria-label', 'Mostrar contraseña');
    toggleButton.setAttribute('title', 'Mostrar contraseña');
    toggleButton.setAttribute('type', 'button'); // Asegurar que no envíe el form
    
    // Agregar event listener
    toggleButton.addEventListener('click', function(e) {
        e.preventDefault(); // Prevenir envío del formulario
        togglePasswordVisibility(toggleButton, targetInput);
    });
    
    // Agregar soporte para teclado (Enter y Espacio)
    toggleButton.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            togglePasswordVisibility(toggleButton, targetInput);
        }
    });
}

// Función para inicializar todos los toggles
function initializeAllPasswordToggles() {
    const toggleButtons = document.querySelectorAll('.password-toggle');
    
    toggleButtons.forEach(button => {
        initializePasswordToggle(button);
    });
    
    console.log(`Inicializados ${toggleButtons.length} toggles de contraseña`);
}

// Función para crear un toggle dinámicamente
function createPasswordToggle(inputId, iconStyle = 'default') {
    const input = document.getElementById(inputId);
    if (!input || input.type !== 'password') {
        console.error(`Input con ID ${inputId} no encontrado o no es de tipo password`);
        return null;
    }
    
    // Crear el contenedor si no existe
    let container = input.parentElement;
    if (!container.classList.contains('password-field')) {
        const newContainer = document.createElement('div');
        newContainer.className = 'password-field';
        input.parentNode.insertBefore(newContainer, input);
        newContainer.appendChild(input);
        container = newContainer;
    }
    
    // Crear el botón toggle
    const toggleButton = document.createElement('button');
    toggleButton.type = 'button';
    toggleButton.className = `password-toggle ${iconStyle}`;
    toggleButton.setAttribute('data-target', inputId);
    
    const icon = document.createElement('span');
    icon.className = 'show-icon';
    toggleButton.appendChild(icon);
    
    container.appendChild(toggleButton);
    
    // Inicializar el toggle
    initializePasswordToggle(toggleButton);
    
    return toggleButton;
}

// Auto-inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    initializeAllPasswordToggles();
});

// Función para manejar contenido dinámico
function observePasswordFields() {
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === Node.ELEMENT_NODE) {
                    const newToggles = node.querySelectorAll('.password-toggle:not([data-initialized])');
                    newToggles.forEach(toggle => {
                        initializePasswordToggle(toggle);
                        toggle.setAttribute('data-initialized', 'true');
                    });
                }
            });
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}

// Exportar funciones para uso global
window.PasswordToggle = {
    initialize: initializeAllPasswordToggles,
    create: createPasswordToggle,
    toggle: togglePasswordVisibility,
    observe: observePasswordFields
};

// Inicializar observador para contenido dinámico (opcional)
// observePasswordFields();