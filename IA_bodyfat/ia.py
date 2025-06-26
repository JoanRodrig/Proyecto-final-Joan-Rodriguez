import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense
import cv2
import mediapipe as mp
import joblib
import os
import math

def entrenar_modelo():
    df = pd.read_csv("IA_bodyfat/data/bodyfat.csv")
    df["Height"] = df["Height"] * 2.54
    df["Weight"] = (df["Weight"] * 0.453592).round(2)
    np.random.seed(42)
    df["Gender"] = np.random.randint(0, 2, df.shape[0])

    features_usadas = ["Neck", "Abdomen", "Hip", "Height", "Weight", "Gender", "BodyFat"]
    df = df[features_usadas]

    X = df.drop("BodyFat", axis=1)
    y = df["BodyFat"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    cols_to_scale = ["Neck", "Abdomen", "Hip", "Height", "Weight"]
    X_train[cols_to_scale] = scaler.fit_transform(X_train[cols_to_scale])
    X_test[cols_to_scale] = scaler.transform(X_test[cols_to_scale])

    model = Sequential([
        Dense(64, activation="relu", input_shape=(X_train.shape[1],)),
        Dense(32, activation="relu"),
        Dense(1),
    ])

    model.compile(optimizer="adam", loss="mean_squared_error")
    model.fit(X_train, y_train, epochs=100, batch_size=32, verbose=1)

    os.makedirs("IA_bodyfat/ia1", exist_ok=True)
    model.save("IA_bodyfat/ia1/model.keras", save_format='tf')
    joblib.dump(scaler, "IA_bodyfat/ia1/scaler.pkl")
    print("Modelo entrenado y guardado correctamente.")

def calcular_distancia_3d(punto1, punto2):
    """Calcula la distancia euclidiana entre dos puntos 3D"""
    return math.sqrt(
        (punto1.x - punto2.x)**2 + 
        (punto1.y - punto2.y)**2 + 
        (punto1.z - punto2.z)**2
    )

def calcular_factor_escala(landmarks, altura_real_cm):
    """
    Calcula el factor de escala basado en la altura real de la persona
    usando la distancia entre la cabeza y los pies en la imagen
    """
    try:
        # Puntos para calcular la altura en la imagen
        cabeza = landmarks[mp.solutions.pose.PoseLandmark.NOSE]
        pie_izq = landmarks[mp.solutions.pose.PoseLandmark.LEFT_ANKLE]
        pie_der = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_ANKLE]
        
        # Usar el pie más bajo (más cerca al suelo)
        pie = pie_izq if pie_izq.y > pie_der.y else pie_der
        
        # Calcular altura en coordenadas normalizadas
        altura_imagen = abs(pie.y - cabeza.y)
        
        # Factor de escala: cm reales / unidades de imagen
        if altura_imagen > 0:
            factor_escala = altura_real_cm / altura_imagen
        else:
            # Factor de escala por defecto si no se puede calcular
            factor_escala = 400  # Aproximado para personas de altura promedio
            
        return factor_escala
        
    except Exception as e:
        print(f"Error calculando factor de escala: {e}")
        return 400  # Factor por defecto

def calcular_medida_cuello(landmarks, factor_escala):
    """
    Calcula la circunferencia del cuello de manera más precisa
    """
    try:
        # Puntos del cuello y hombros
        hombro_izq = landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER]
        hombro_der = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER]
        
        # Calcular ancho de hombros como referencia
        ancho_hombros = calcular_distancia_3d(hombro_izq, hombro_der) * factor_escala
        
        # El cuello típicamente es 60-70% del ancho de hombros
        # Aplicamos una fórmula antropométrica más realista
        cuello_estimado = ancho_hombros * 0.65
        
        # Rangos realistas para cuello: 28-45 cm
        cuello_estimado = max(28, min(45, cuello_estimado))
        
        return cuello_estimado
        
    except Exception as e:
        print(f"Error calculando cuello: {e}")
        return 35  # Valor promedio por defecto

def calcular_medida_cintura(landmarks, factor_escala, altura_cm):
    """
    Calcula la circunferencia de la cintura de manera más precisa
    """
    try:
        # Puntos de referencia para la cintura
        cadera_izq = landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP]
        cadera_der = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_HIP]
        hombro_izq = landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER]
        hombro_der = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER]
        
        # Calcular ancho de caderas como base
        ancho_caderas = calcular_distancia_3d(cadera_izq, cadera_der) * factor_escala
        
        # Punto medio de la cintura (entre hombros y caderas)
        cintura_y = (hombro_izq.y + hombro_der.y) / 2 + (cadera_izq.y + cadera_der.y) / 2
        cintura_y /= 2
        
        # Estimar ancho de cintura usando proporción corporal
        # La cintura suele ser 70-85% del ancho de caderas
        cintura_estimada = ancho_caderas * 0.78
        
        # Aplicar corrección basada en altura (personas más altas tienden a tener cinturas proporcionalmente más grandes)
        factor_altura = 1 + (altura_cm - 170) * 0.002  # Ajuste basado en altura promedio
        cintura_estimada *= factor_altura
        
        # Convertir ancho a circunferencia aproximada (multiplicador empírico)
        circunferencia_cintura = cintura_estimada * 3.2
        
        # Rangos realistas para cintura: 60-140 cm
        circunferencia_cintura = max(60, min(140, circunferencia_cintura))
        
        return circunferencia_cintura
        
    except Exception as e:
        print(f"Error calculando cintura: {e}")
        return 80  # Valor promedio por defecto

def calcular_medida_cadera(landmarks, factor_escala, altura_cm):
    """
    Calcula la circunferencia de la cadera de manera más precisa
    """
    try:
        # Puntos de las caderas
        cadera_izq = landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP]
        cadera_der = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_HIP]
        
        # Calcular ancho de caderas
        ancho_caderas = calcular_distancia_3d(cadera_izq, cadera_der) * factor_escala
        
        # Aplicar corrección basada en altura
        factor_altura = 1 + (altura_cm - 170) * 0.0015
        ancho_caderas *= factor_altura
        
        # Convertir ancho a circunferencia (la cadera es más redondeada que la cintura)
        circunferencia_cadera = ancho_caderas * 3.4
        
        # Rangos realistas para cadera: 70-150 cm
        circunferencia_cadera = max(70, min(150, circunferencia_cadera))
        
        return circunferencia_cadera
        
    except Exception as e:
        print(f"Error calculando cadera: {e}")
        return 95  # Valor promedio por defecto

def validar_proporciones_corporales(cuello, cintura, cadera):
    """
    Valida que las proporciones corporales sean anatómicamente correctas
    """
    # Reglas anatómicas básicas
    if cuello >= cintura:
        cuello = cintura * 0.4  # El cuello debe ser menor que la cintura
    
    if cintura >= cadera:
        cintura = cadera * 0.85  # La cintura debe ser menor que la cadera
    
    if cuello < 25 or cuello > 50:
        cuello = max(25, min(50, cuello))
    
    if cintura < 50 or cintura > 150:
        cintura = max(50, min(150, cintura))
    
    if cadera < 60 or cadera > 160:
        cadera = max(60, min(160, cadera))
    
    return cuello, cintura, cadera

def extraer_medidas(image, altura_cm):
    """
    Extrae medidas corporales de la imagen usando MediaPipe con mayor precisión
    """
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(
        static_image_mode=True,
        model_complexity=2,  # Mayor precisión
        enable_segmentation=False,
        min_detection_confidence=0.5
    )
    
    # Preprocesar imagen para mejor detección
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Mejorar contraste si es necesario
    lab = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    l = clahe.apply(l)
    enhanced = cv2.merge([l, a, b])
    image_rgb = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)
    
    results = pose.process(image_rgb)
    
    if not results.pose_landmarks:
        raise ValueError("No se detectó pose completa en la imagen. Asegúrate de que todo el cuerpo sea visible.")

    landmarks = results.pose_landmarks.landmark
    
    # Verificar que los landmarks críticos estén presentes
    landmarks_criticos = [
        mp_pose.PoseLandmark.LEFT_SHOULDER,
        mp_pose.PoseLandmark.RIGHT_SHOULDER,
        mp_pose.PoseLandmark.LEFT_HIP,
        mp_pose.PoseLandmark.RIGHT_HIP,
        mp_pose.PoseLandmark.NOSE
    ]
    
    for landmark_idx in landmarks_criticos:
        if landmarks[landmark_idx].visibility < 0.5:
            raise ValueError(f"Landmark crítico no visible: {landmark_idx.name}")
    
    # Calcular factor de escala basado en altura real
    factor_escala = calcular_factor_escala(landmarks, altura_cm)
    print(f"Factor de escala calculado: {factor_escala}")
    
    # Calcular medidas usando el factor de escala
    cuello = calcular_medida_cuello(landmarks, factor_escala)
    cintura = calcular_medida_cintura(landmarks, factor_escala, altura_cm)
    cadera = calcular_medida_cadera(landmarks, factor_escala, altura_cm)
    
    # Validar proporciones anatómicas
    cuello, cintura, cadera = validar_proporciones_corporales(cuello, cintura, cadera)
    
    medidas = {
        "Neck": round(cuello, 2),
        "Abdomen": round(cintura, 2),
        "Hip": round(cadera, 2),
    }
    
    print(f"Medidas calculadas: {medidas}")
    return medidas

def predecir_con_imagen(image_path, altura, peso, genero):
    """
    Predice el porcentaje de grasa corporal usando la imagen y datos antropométricos
    """
    try:
        # Cargar modelo y scaler
        model = load_model("IA_bodyfat/ia1/model.keras", compile=False)
        scaler = joblib.load("IA_bodyfat/ia1/scaler.pkl")
        
        # Leer imagen
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("No se pudo leer la imagen desde la ruta proporcionada")
        
        print(f"Imagen cargada: {image.shape}")
        print(f"Datos de entrada - Altura: {altura}cm, Peso: {peso}kg, Género: {genero}")
        
        # Extraer medidas corporales
        medidas = extraer_medidas(image, altura)
        
        # Crear DataFrame para predicción
        X_new = pd.DataFrame([[
            medidas["Neck"],
            medidas["Abdomen"],
            medidas["Hip"],
            altura,
            peso,
            genero
        ]], columns=["Neck", "Abdomen", "Hip", "Height", "Weight", "Gender"])
        
        print(f"Datos antes del escalado: {X_new.iloc[0].to_dict()}")
        
        # Aplicar escalado solo a las columnas numéricas necesarias
        cols_to_scale = ["Neck", "Abdomen", "Hip", "Height", "Weight"]
        X_scaled = X_new.copy()
        X_scaled[cols_to_scale] = scaler.transform(X_new[cols_to_scale])
        
        print(f"Datos después del escalado: {X_scaled.iloc[0].to_dict()}")
        
        # Realizar predicción
        prediccion = model.predict(X_scaled, verbose=0)[0][0]
        
        # Validar que la predicción esté en un rango realista
        prediccion = max(3.0, min(50.0, prediccion))  # Rango típico de grasa corporal
        
        resultado = {
            "medidas": medidas,
            "prediccion": round(float(prediccion), 2)
        }
        
        print(f"Predicción final: {resultado}")
        return resultado
        
    except Exception as e:
        print(f"Error detallado en predecir_con_imagen: {str(e)}")
        raise ValueError(f"Error en la predicción: {str(e)}")

# Función adicional para debug
def debug_landmarks(image_path):
    """
    Función de debug para visualizar los landmarks detectados
    """
    import matplotlib.pyplot as plt
    
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    
    pose = mp_pose.Pose(static_image_mode=True, model_complexity=2)
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    results = pose.process(image_rgb)
    
    if results.pose_landmarks:
        # Dibujar landmarks
        annotated_image = image_rgb.copy()
        mp_drawing.draw_landmarks(
            annotated_image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        plt.figure(figsize=(10, 10))
        plt.imshow(annotated_image)
        plt.axis('off')
        plt.title('Landmarks detectados')
        plt.show()
        
        return results.pose_landmarks
    else:
        print("No se detectaron landmarks")
        return None