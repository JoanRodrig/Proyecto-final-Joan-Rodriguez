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


# ========== ENTRENAMIENTO DEL MODELO ==========
def entrenar_modelo():
    df = pd.read_csv("bodyfat.csv")
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

    os.makedirs("ia1", exist_ok=True)
    model.save("ia1/bodyfat_model.keras")
    joblib.dump(scaler, "ia1/scaler.pkl")
    print("Modelo entrenado y guardado correctamente.")


# ========== PROCESAMIENTO DE IMAGEN ==========
def extraer_medidas(image):
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=True)
    results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    if not results.pose_landmarks:
        return None

    landmarks = results.pose_landmarks.landmark
    key_landmarks = [
        mp_pose.PoseLandmark.LEFT_SHOULDER,
        mp_pose.PoseLandmark.RIGHT_SHOULDER,
        mp_pose.PoseLandmark.LEFT_HIP,
        mp_pose.PoseLandmark.RIGHT_HIP,
        mp_pose.PoseLandmark.LEFT_KNEE,
        mp_pose.PoseLandmark.RIGHT_KNEE,
        mp_pose.PoseLandmark.LEFT_ANKLE,
        mp_pose.PoseLandmark.RIGHT_ANKLE,
    ]

    for landmark in key_landmarks:
        if landmarks[landmark].visibility < 0.5:
            return None

    h, w = image.shape[:2]
    puntos = {
        "neck": landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER],
        "waist": landmarks[mp_pose.PoseLandmark.LEFT_HIP],
        "hip": landmarks[mp_pose.PoseLandmark.LEFT_KNEE],
    }

    medidas = {
        "Neck": np.linalg.norm([puntos["neck"].x * w, puntos["neck"].y * h]) * 0.0265,
        "Abdomen": np.linalg.norm([puntos["waist"].x * w, puntos["waist"].y * h]) * 0.0265,
        "Hip": np.linalg.norm([puntos["hip"].x * w, puntos["hip"].y * h]) * 0.0265,
        "Height": 175,  # valor temporal
        "Weight": 70,
        "Gender": 0,
    }
    return medidas


# ========== PREDICCIÓN ==========
def predecir_con_imagen(image_path, altura, peso, genero, return_results=False):
    model = load_model("ia1/bodyfat_model.keras")
    scaler = joblib.load("ia1/scaler.pkl")
    image = cv2.imread(image_path)
    medidas = extraer_medidas(image)

    if medidas is None:
        raise ValueError("No se detectó un cuerpo completo en la imagen.")

    medidas["Height"] = altura
    medidas["Weight"] = peso
    medidas["Gender"] = genero

    X_new = pd.DataFrame([[
        medidas["Neck"],
        medidas["Abdomen"],
        medidas["Hip"],
        medidas["Height"],
        medidas["Weight"],
        medidas["Gender"]
    ]], columns=["Neck", "Abdomen", "Hip", "Height", "Weight", "Gender"])

    cols_to_scale = ["Neck", "Abdomen", "Hip", "Height", "Weight"]
    X_new[cols_to_scale] = scaler.transform(X_new[cols_to_scale])
    prediccion = model.predict(X_new)[0][0]
    clasificacion_genero = "Hombre" if genero == 0 else "Mujer"

    if genero == 0:
        clasif_grasa = ("Grasa esencial" if prediccion < 8 else
                        "Atleta/Fitness" if prediccion < 20 else
                        "Aceptable" if prediccion < 25 else
                        "Obesidad")
    else:
        clasif_grasa = ("Grasa esencial" if prediccion < 12 else
                        "Atleta/Fitness" if prediccion < 25 else
                        "Aceptable" if prediccion < 30 else
                        "Obesidad")

    if return_results:
        return prediccion, clasif_grasa

    return {
        "genero": clasificacion_genero,
        "medidas": medidas,
        "altura": altura,
        "peso": peso,
        "prediccion": round(prediccion, 2),
        "clasificacion": clasif_grasa
    }
