from ia import entrenar_modelo
import tensorflow as tf

# Verifica versión de TensorFlow
print("Versión de TensorFlow:", tf.__version__)

# Limpia sesión de Keras previa (importante si vas a reentrenar múltiples veces)
tf.keras.backend.clear_session()

# Entrena el modelo
print("\nIniciando entrenamiento...")
entrenar_modelo()
print("\nEntrenamiento completado exitosamente!")