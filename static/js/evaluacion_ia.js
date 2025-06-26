document.addEventListener('DOMContentLoaded', function () {
    console.log('Iniciando aplicación de evaluación IA...');

    // Elementos del DOM
    const step1 = document.getElementById('step1');
    const step2 = document.getElementById('step2');
    const step3 = document.getElementById('step3');
    const btnPrev = document.getElementById('btnPrev');
    const btnNext = document.getElementById('btnNext');
    const btnCalculate = document.getElementById('btnCalculate');
    const video = document.getElementById('videoFeed');
    const imagePreview = document.getElementById('imagePreview');
    const btnCamera = document.getElementById('btnCamera');
    const btnUpload = document.getElementById('btnUpload');
    const btnCapture = document.getElementById('btnCapture');
    const heightInput = document.getElementById('heightInput');
    const weightInput = document.getElementById('weightInput');
    const fatPercentage = document.getElementById('fatPercentage');
    const classification = document.getElementById('classification');
    const btnProgress = document.getElementById('btnProgress');

    // Verificar que todos los elementos existen
    const elements = {
        step1, step2, step3, btnPrev, btnNext, btnCalculate,
        video, imagePreview, btnCamera, btnUpload, btnCapture,
        heightInput, weightInput, fatPercentage, classification, btnProgress
    };

    let missingElements = [];
    for (let [name, element] of Object.entries(elements)) {
        if (!element) {
            missingElements.push(name);
        }
    }

    if (missingElements.length > 0) {
        console.error('Elementos faltantes:', missingElements);
        console.warn('Continuando con elementos disponibles...');
    } else {
        console.log('Todos los elementos encontrados correctamente');
    }

    let currentStep = 1;
    let stream = null;
    let capturedImage = null;

    // Función para verificar permisos de cámara
    async function checkCameraPermissions() {
        try {
            if (navigator.permissions) {
                const permission = await navigator.permissions.query({ name: 'camera' });
                console.log('Estado inicial del permiso de cámara:', permission.state);

                permission.addEventListener('change', () => {
                    console.log('Permiso de cámara cambió a:', permission.state);
                    updateCameraButtonState();
                });

                return permission.state;
            }
        } catch (error) {
            console.log('No se pudo verificar permisos:', error);
        }
        return 'unknown';
    }

    // Actualizar estado del botón de cámara
    function updateCameraButtonState() {
        if (btnCamera) {
            navigator.mediaDevices.enumerateDevices()
                .then(devices => {
                    const hasCamera = devices.some(device => device.kind === 'videoinput');
                    if (!hasCamera) {
                        btnCamera.disabled = true;
                        btnCamera.innerHTML = '<i class="fas fa-video-slash"></i> Sin Cámara';
                        btnCamera.title = 'No se detectó ninguna cámara';
                    }
                })
                .catch(error => console.log('Error al verificar dispositivos:', error));
        }
    }

    // Función para ajustar la imagen al contenedor manteniendo proporción
    function adjustImageToContainer(img, container) {
        const containerWidth = container.offsetWidth;
        const containerHeight = container.offsetHeight;
        const imgAspectRatio = img.naturalWidth / img.naturalHeight;
        const containerAspectRatio = containerWidth / containerHeight;

        // Resetear estilos
        img.style.width = '';
        img.style.height = '';
        img.style.objectFit = 'contain';
        img.style.objectPosition = 'center';
        img.style.position = 'absolute';
        img.style.top = '0';
        img.style.left = '0';
        img.style.right = '0';
        img.style.bottom = '0';
        img.style.margin = 'auto';
        img.style.backgroundColor = '#000';

        // Ajustar según la proporción
        if (imgAspectRatio > containerAspectRatio) {
            // Imagen más ancha que el contenedor - ajustar por ancho
            img.style.width = '100%';
            img.style.height = 'auto';
        } else {
            // Imagen más alta que el contenedor - ajustar por altura
            img.style.width = 'auto';
            img.style.height = '100%';
        }
    }

    // Función para ajustar el video al contenedor
    function adjustVideoToContainer(video, container) {
        if (!video || !container) return;

        const containerWidth = container.offsetWidth;
        const containerHeight = container.offsetHeight;

        // Esperar a que el video tenga metadatos
        const adjustVideo = () => {
            if (video.videoWidth && video.videoHeight) {
                const videoAspectRatio = video.videoWidth / video.videoHeight;
                const containerAspectRatio = containerWidth / containerHeight;

                video.style.position = 'absolute';
                video.style.top = '0';
                video.style.left = '0';
                video.style.right = '0';
                video.style.bottom = '0';
                video.style.margin = 'auto';
                video.style.objectFit = 'contain';
                video.style.objectPosition = 'center';
                video.style.backgroundColor = '#000';

                if (videoAspectRatio > containerAspectRatio) {
                    video.style.width = '100%';
                    video.style.height = 'auto';
                } else {
                    video.style.width = 'auto';
                    video.style.height = '100%';
                }

                console.log(`Video ajustado: ${video.videoWidth}x${video.videoHeight}`);
            }
        };

        if (video.videoWidth && video.videoHeight) {
            adjustVideo();
        } else {
            video.addEventListener('loadedmetadata', adjustVideo);
        }
    }

    // Inicializar la aplicación
    function init() {
        console.log('Inicializando aplicación...');
        showStep(1);
        checkCameraPermissions();
        updateCameraButtonState();

        if (heightInput) {
            heightInput.addEventListener('input', updateCalculateButton);
        }
        if (weightInput) {
            weightInput.addEventListener('input', updateCalculateButton);
        }

        // Ajustar contenedor de preview al cargar
        if (imagePreview) {
            // Asegurar que el contenedor tenga dimensiones fijas
            imagePreview.style.position = 'relative';
            imagePreview.style.overflow = 'hidden';
        }

        // Event listener para el botón de progreso
        if (btnProgress) {
            btnProgress.addEventListener('click', function () {
                console.log('Botón ver progreso presionado');
                btnProgress.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Redirigiendo...';

                // Cambia '/progreso' por la URL correcta de tu apartado de progreso
                window.location.href = '/progreso';
            });
        }
    }

    // Navegación entre pasos
    function showStep(step) {
        console.log(`Mostrando paso ${step}`);

        document.querySelectorAll('.step').forEach(s => {
            s.classList.remove('active');
            s.style.display = 'none';
        });

        const currentStepElement = document.getElementById(`step${step}`);
        if (currentStepElement) {
            currentStepElement.classList.add('active');
            currentStepElement.style.display = 'block';
        }

        currentStep = step;

        // Actualizar botones de navegación
        if (btnPrev) {
            btnPrev.disabled = step === 1;
            btnPrev.style.display = step === 3 ? 'none' : 'flex'; // Ocultar en paso 3 (resultados)
        }

        if (btnNext && btnCalculate) {
            if (step === 2) {
                btnNext.style.display = 'none';
                btnCalculate.style.display = 'flex';
                updateCalculateButton();
            } else if (step === 3) {
                btnNext.style.display = 'none';
                btnCalculate.style.display = 'none';
            } else {
                btnNext.style.display = 'flex';
                btnCalculate.style.display = 'none';
            }
        }

        if (step === 1 && btnNext) {
            btnNext.disabled = !capturedImage;
        } else if (btnNext) {
            btnNext.disabled = false;
        }
    }

    // Actualizar estado del botón calcular
    function updateCalculateButton() {
        if (btnCalculate && heightInput && weightInput) {
            const height = heightInput.value.trim();
            const weight = weightInput.value.trim();
            btnCalculate.disabled = !height || !weight || !capturedImage;
        }
    }

    // Event listeners para navegación
    if (btnNext) {
        btnNext.addEventListener('click', function () {
            console.log('Botón siguiente presionado');
            if (validateStep(currentStep)) {
                showStep(currentStep + 1);
            }
        });
    }

    if (btnPrev) {
        btnPrev.addEventListener('click', function () {
            console.log('Botón anterior presionado');
            showStep(currentStep - 1);
        });
    }

    if (btnCalculate) {
        btnCalculate.addEventListener('click', function () {
            console.log('Botón calcular presionado');
            if (validateStep(2)) {
                calculateBodyFat();
            }
        });
    }

    // Validación de pasos
    function validateStep(step) {
        console.log(`Validando paso ${step}`);

        if (step === 1) {
            if (!capturedImage) {
                alert('Por favor, captura o sube una imagen primero');
                return false;
            }
            return true;
        }

        if (step === 2) {
            if (!heightInput || !weightInput) {
                console.error('Inputs de altura o peso no encontrados');
                return false;
            }

            const height = heightInput.value.trim();
            const weight = weightInput.value.trim();

            if (!height || !weight) {
                alert('Por favor, completa todos los campos');
                return false;
            }

            if (parseFloat(height) < 100 || parseFloat(height) > 250) {
                alert('Por favor, ingresa una altura válida (100-250 cm)');
                return false;
            }

            if (parseFloat(weight) < 30 || parseFloat(weight) > 300) {
                alert('Por favor, ingresa un peso válido (30-300 kg)');
                return false;
            }

            return true;
        }

        return true;
    }

    // Detener stream de cámara
    function stopCameraStream() {
        if (stream) {
            stream.getTracks().forEach(track => {
                track.stop();
                console.log('Track detenido:', track.kind);
            });
            stream = null;
        }
    }

    // Manejo de cámara mejorado
    if (btnCamera) {
        btnCamera.addEventListener('click', async function () {
            console.log('Activando cámara...');

            btnCamera.disabled = true;
            const originalText = btnCamera.innerHTML;
            btnCamera.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Activando...';

            try {
                if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                    throw new Error('Tu navegador no soporta acceso a la cámara');
                }

                let permissionState = 'unknown';
                try {
                    const permission = await navigator.permissions.query({ name: 'camera' });
                    permissionState = permission.state;
                    console.log('Estado del permiso de cámara:', permissionState);
                } catch (permError) {
                    console.log('No se pudo verificar permisos específicos:', permError);
                }

                if (permissionState === 'denied') {
                    throw new Error('PERMISSION_DENIED');
                }

                stopCameraStream();

                stream = await navigator.mediaDevices.getUserMedia({
                    video: {
                        width: { ideal: 640, max: 1280 },
                        height: { ideal: 640, max: 1280 }, // Formato más cuadrado
                        facingMode: 'user'
                    }
                });

                if (video) {
                    video.srcObject = stream;
                    video.style.display = 'block';

                    video.addEventListener('loadedmetadata', () => {
                        console.log(`Video listo: ${video.videoWidth}x${video.videoHeight}`);
                        adjustVideoToContainer(video, imagePreview);
                    });

                    // Ajustar cuando cambie el tamaño
                    video.addEventListener('resize', () => {
                        adjustVideoToContainer(video, imagePreview);
                    });
                }

                // Ocultar placeholder
                if (imagePreview) {
                    const placeholder = imagePreview.querySelector('.preview-placeholder');
                    if (placeholder) {
                        placeholder.style.display = 'none';
                    }
                }

                if (btnCapture) btnCapture.style.display = 'flex';
                if (btnUpload) btnUpload.disabled = true;

                console.log('Cámara activada correctamente');

            } catch (err) {
                console.error("Error al acceder a la cámara:", err);

                let errorMessage = "No se pudo acceder a la cámara.\n\n";

                if (err.message === 'PERMISSION_DENIED' || err.name === 'NotAllowedError') {
                    errorMessage += "❌ Permisos denegados.\n\n" +
                        "✅ Para solucionarlo:\n" +
                        "1. Busca el ícono 🔒 o 📷 en la barra de direcciones\n" +
                        "2. Haz clic y selecciona 'Permitir' para la cámara\n" +
                        "3. Recarga la página (F5)\n\n" +
                        "💡 Si no aparece el ícono, ve a Configuración del navegador > Privacidad > Cámara";
                } else if (err.name === 'NotFoundError') {
                    errorMessage += "❌ No se encontró ninguna cámara conectada.\n\n" +
                        "✅ Verifica que tu cámara esté conectada y funcionando.";
                } else if (err.name === 'NotReadableError') {
                    errorMessage += "❌ La cámara está siendo utilizada por otra aplicación.\n\n" +
                        "✅ Cierra otras aplicaciones que puedan estar usando la cámara\n" +
                        "(Zoom, Teams, Skype, etc.)";
                } else if (err.name === 'SecurityError') {
                    errorMessage += "❌ Acceso denegado por razones de seguridad.\n\n" +
                        "✅ Asegúrate de estar usando HTTPS o localhost.";
                } else if (err.name === 'OverconstrainedError') {
                    errorMessage += "❌ La configuración de cámara solicitada no es compatible.\n\n" +
                        "✅ Tu cámara no soporta la resolución solicitada.";
                } else {
                    errorMessage += "❌ Error técnico: " + err.message + "\n\n" +
                        "✅ Intenta usar la opción 'Subir Imagen' como alternativa.";
                }

                alert(errorMessage);

                if (btnUpload) {
                    btnUpload.disabled = false;
                    btnUpload.style.backgroundColor = '#ff6b35';
                    btnUpload.innerHTML = '<i class="fas fa-upload"></i> Usar esta opción';
                    setTimeout(() => {
                        btnUpload.style.backgroundColor = '';
                        btnUpload.innerHTML = '<i class="fas fa-upload"></i> Subir Imagen';
                    }, 3000);
                }

            } finally {
                btnCamera.disabled = false;
                btnCamera.innerHTML = originalText;
            }
        });
    }

    // Capturar imagen mejorado
    if (btnCapture) {
        btnCapture.addEventListener('click', function () {
            console.log('Capturando imagen...');

            if (!stream || !video || !video.videoWidth || !video.videoHeight) {
                console.error('Video no disponible para captura');
                alert('Error: El video no está listo. Intenta activar la cámara nuevamente.');
                return;
            }

            try {
                const canvas = document.createElement('canvas');
                const containerWidth = imagePreview.offsetWidth;
                const containerHeight = imagePreview.offsetHeight;

                // Configurar canvas con las dimensiones del contenedor
                canvas.width = containerWidth;
                canvas.height = containerHeight;
                const ctx = canvas.getContext('2d');

                // Fondo negro
                ctx.fillStyle = '#000000';
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                // Calcular dimensiones para centrar el video
                const videoAspectRatio = video.videoWidth / video.videoHeight;
                const canvasAspectRatio = canvas.width / canvas.height;

                let drawWidth, drawHeight, drawX, drawY;

                if (videoAspectRatio > canvasAspectRatio) {
                    // Video más ancho - ajustar por ancho
                    drawWidth = canvas.width;
                    drawHeight = canvas.width / videoAspectRatio;
                    drawX = 0;
                    drawY = (canvas.height - drawHeight) / 2;
                } else {
                    // Video más alto - ajustar por altura
                    drawHeight = canvas.height;
                    drawWidth = canvas.height * videoAspectRatio;
                    drawX = (canvas.width - drawWidth) / 2;
                    drawY = 0;
                }

                // Dibujar el video centrado
                ctx.drawImage(video, drawX, drawY, drawWidth, drawHeight);

                capturedImage = canvas.toDataURL('image/jpeg', 0.8);
                displayPreviewImage(capturedImage);

                stopCameraStream();
                if (video) video.style.display = 'none';
                btnCapture.style.display = 'none';
                if (btnUpload) btnUpload.disabled = false;
                if (btnCamera) btnCamera.disabled = false;

                showStep(currentStep);

                btnCapture.style.backgroundColor = '#28a745';
                btnCapture.innerHTML = '<i class="fas fa-check"></i> ¡Capturada!';

                console.log('Imagen capturada correctamente');

            } catch (error) {
                console.error('Error al capturar imagen:', error);
                alert('Error al capturar la imagen. Por favor intenta nuevamente.');
            }
        });
    }

    // Subir imagen mejorado
    if (btnUpload) {
        btnUpload.addEventListener('click', function () {
            console.log('Iniciando subida de imagen...');

            const fileInput = document.createElement('input');
            fileInput.type = 'file';
            fileInput.accept = 'image/*';
            fileInput.style.display = 'none';

            fileInput.onchange = function (e) {
                const file = e.target.files[0];
                if (!file) {
                    console.log('No se seleccionó archivo');
                    return;
                }

                console.log('Archivo seleccionado:', file.name, file.size, file.type);

                if (!file.type.startsWith('image/')) {
                    alert('Por favor selecciona un archivo de imagen válido.');
                    return;
                }

                if (file.size > 10 * 1024 * 1024) {
                    alert('El archivo es demasiado grande. Por favor selecciona una imagen menor a 10MB.');
                    return;
                }

                const reader = new FileReader();
                reader.onload = function (event) {
                    capturedImage = event.target.result;
                    displayPreviewImage(capturedImage);

                    if (stream) {
                        stopCameraStream();
                        if (video) video.style.display = 'none';
                        if (btnCapture) btnCapture.style.display = 'none';
                        if (btnCamera) btnCamera.disabled = false;
                    }

                    showStep(currentStep);

                    btnUpload.style.backgroundColor = '#28a745';
                    btnUpload.innerHTML = '<i class="fas fa-check"></i> ¡Subida!';
                    setTimeout(() => {
                        btnUpload.style.backgroundColor = '';
                        btnUpload.innerHTML = '<i class="fas fa-upload"></i> Subir Imagen';
                    }, 2000);

                    console.log('Imagen subida correctamente');
                };

                reader.onerror = function () {
                    console.error('Error al leer el archivo');
                    alert('Error al leer el archivo. Por favor intenta con otra imagen.');
                };

                reader.readAsDataURL(file);
            };

            document.body.appendChild(fileInput);
            fileInput.click();
            document.body.removeChild(fileInput);
        });
    }

    // Mostrar imagen de preview mejorado
    function displayPreviewImage(imageSrc) {
        console.log('Mostrando imagen de preview...');

        if (!imagePreview) {
            console.error('Contenedor de preview no encontrado');
            return;
        }

        // Limpiar el contenido actual
        imagePreview.innerHTML = '';

        // Crear elemento de imagen
        const img = document.createElement('img');
        img.src = imageSrc;
        img.style.display = 'block';

        // Manejar carga de imagen
        img.onload = function () {
            console.log('Imagen cargada correctamente en preview');
            adjustImageToContainer(img, imagePreview);
        };

        img.onerror = function () {
            console.error('Error al cargar imagen en preview');
            imagePreview.innerHTML = '<div class="preview-placeholder"><i class="fas fa-exclamation-triangle"></i><p>Error al cargar imagen</p></div>';
        };

        imagePreview.appendChild(img);
        console.log('Imagen mostrada correctamente');
    }

    // Calcular porcentaje de grasa
    async function calculateBodyFat() {
        console.log('Calculando porcentaje de grasa...');

        if (!heightInput || !weightInput) {
            alert('Inputs no disponibles');
            return;
        }

        const altura = parseFloat(heightInput.value);
        const peso = parseFloat(weightInput.value);

        if (!altura || !peso) {
            alert('Por favor ingresa tu altura y peso');
            return;
        }

        if (!capturedImage) {
            alert('Por favor, captura o sube una imagen primero');
            showStep(1);
            return;
        }

        if (btnCalculate) {
            btnCalculate.disabled = true;
            btnCalculate.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analizando imagen...';
        }

        try {
            // Mostrar animación de procesamiento
            const steps = [
                'Analizando composición corporal...',
                'Procesando con IA...',
                'Calculando porcentajes...',
                'Generando resultados...'
            ];

            for (let i = 0; i < steps.length; i++) {
                if (btnCalculate) btnCalculate.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${steps[i]}`;
                await new Promise(resolve => setTimeout(resolve, 1000));
            }

            // Enviar datos al servidor
            const formData = new FormData();
            formData.append('imagen_base64', capturedImage);
            formData.append('altura', altura);
            formData.append('peso', peso);

            const response = await fetch(window.location.href, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken'),
                }
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Error en el servidor');
            }

            // Mostrar resultados (manteniendo el estilo visual original)
            document.getElementById('resultGenero').textContent = data.genero;
            document.getElementById('resultAltura').textContent = `${data.altura} cm`;
            document.getElementById('resultPeso').textContent = `${data.peso} kg`;
            document.getElementById('resultCuello').textContent = `${data.medidas.Neck.toFixed(2)} cm`;
            document.getElementById('resultAbdomen').textContent = `${data.medidas.Abdomen.toFixed(2)} cm`;
            document.getElementById('resultCadera').textContent = `${data.medidas.Hip.toFixed(2)} cm`;
            document.getElementById('resultGrasa').textContent = `${data.porcentaje_grasa}%`;
            document.getElementById('resultClasificacion').textContent = data.clasificacion;
            document.getElementById('resultClasificacion').style.color = getClassificationColor(data.clasificacion);
            document.getElementById('resultRecomendacion').textContent = data.recomendacion;

            showStep(3);

            console.log('Cálculo completado:', data);

        } catch (error) {
            console.error("Error al calcular:", error);
            alert(`Ocurrió un error al procesar la imagen: ${error.message}`);
        } finally {
            if (btnCalculate) {
                btnCalculate.disabled = false;
                btnCalculate.innerHTML = '<i class="fas fa-calculator"></i> Calcular';
            }
        }
    }

    // Función auxiliar para obtener el color de clasificación (manteniendo tu estilo)
    function getClassificationColor(clasificacion) {
        switch (clasificacion.toLowerCase()) {
            case 'grasa esencial': return '#4CAF50';
            case 'atleta/fitness': return '#2196F3';
            case 'aceptable': return '#FFC107';
            case 'obesidad': return '#F44336';
            default: return '#FFFFFF';
        }
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

    // Función para obtener color de clasificación
    function getClassificationColor(classification) {
        switch (classification) {
            case 'Bajo peso': return '#ffc107';
            case 'Peso normal': return '#28a745';
            case 'Sobrepeso': return '#fd7e14';
            case 'Obesidad': return '#dc3545';
            default: return '#ffffff';
        }
    }

    // Botones de acción en resultados
    const btnWorkout = document.getElementById('btnWorkout');
    const btnDiet = document.getElementById('btnDiet');

    if (btnWorkout) {
        btnWorkout.addEventListener('click', function () {
            console.log('Botón rutina de ejercicios presionado');
            btnWorkout.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Cargando...';
            setTimeout(() => {
                alert('Funcionalidad de rutinas próximamente disponible.\n\nSe generará una rutina personalizada basada en tus resultados.');
                btnWorkout.innerHTML = '<i class="fas fa-dumbbell"></i> Ver Rutina';
            }, 1000);
        });
    }

    if (btnDiet) {
        btnDiet.addEventListener('click', function () {
            console.log('Botón plan alimenticio presionado');
            btnDiet.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Cargando...';
            setTimeout(() => {
                alert('Funcionalidad de planes alimenticios próximamente disponible.\n\nSe generará un plan nutricional personalizado basado en tus resultados.');
                btnDiet.innerHTML = '<i class="fas fa-utensils"></i> Plan Alimenticio';
            }, 1000);
        });
    }

    // Cleanup functions
    function cleanup() {
        console.log('Limpiando recursos...');
        stopCameraStream();
    }

    // Event listeners para cleanup
    window.addEventListener('beforeunload', cleanup);
    window.addEventListener('unload', cleanup);

    // Manejar errores globales
    window.addEventListener('error', function (e) {
        console.error('Error global:', e.error);
    });

    // Manejar cambios de visibilidad de página
    document.addEventListener('visibilitychange', function () {
        if (document.hidden && stream) {
            console.log('Página oculta, pausando cámara...');
            if (video) video.pause();
        } else if (!document.hidden && stream && video) {
            console.log('Página visible, reanudando cámara...');
            video.play();
        }
    });

    // Manejar redimensionamiento de ventana
    window.addEventListener('resize', function () {
        if (video && video.style.display === 'block') {
            adjustVideoToContainer(video, imagePreview);
        }

        // Reajustar imagen si está visible
        const img = imagePreview.querySelector('img');
        if (img && img.style.display !== 'none') {
            adjustImageToContainer(img, imagePreview);
        }
    });

    // Inicializar la aplicación
    init();

    console.log('Aplicación de evaluación IA inicializada correctamente');
});