from kafka import KafkaConsumer
import json
import time
import pickle
import psycopg2
from src.credentials import get_database_credentials
import logging

logging.basicConfig(level=logging.INFO)

# Cargar el modelo (asegúrate de tener un archivo modelo.pkl)
def load_model():
    try:
        with open('consumer.pkl', 'rb') as f:
            model = pickle.load(f)
        logging.info("Modelo cargado exitosamente.")
        return model
    except Exception as e:
        logging.error(f"Error al cargar el modelo: {e}")
        raise

# Guardar la predicción en la base de datos
def save_prediction_to_db(prediction, data):
    credentials = get_database_credentials()
    try:
        # Conectar a la base de datos
        with psycopg2.connect(
            dbname=credentials['dbname'],
            user=credentials['user'],
            password=credentials['password'],
            host=credentials['host'],
            port=credentials['port']
        ) as connection:
            with connection.cursor() as cursor:
                # Insertar la predicción en la base de datos (asegúrate de tener una tabla llamada 'predictions')
                cursor.execute("""
                    INSERT INTO predictions (data, prediction)
                    VALUES (%s, %s)
                """, (json.dumps(data), prediction))

                # Confirmar la transacción
                connection.commit()
                logging.info(f"Predicción guardada: {prediction}")
    except Exception as e:
        logging.error(f"Error al guardar la predicción en la base de datos: {e}")

def start_consumer():
    # Configuración del consumer
    consumer = KafkaConsumer(
        'happiness_data',
        enable_auto_commit=True,
        group_id='my-group-1',
        bootstrap_servers='kafka-stream:9092',
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )

    # Cargar el modelo de predicción
    model = load_model()

    # Recorrer los mensajes recibidos
    for message in consumer:
        data = message.value
        try:
            # Pasarle el row al modelo
            prediction = model.predict([data])  # Asume que 'data' es una fila en el formato adecuado para tu modelo

            # Imprimir la predicción
            logging.info(f"Predicción: {prediction[0]}")

            # Enviar la predicción a la base de datos
            save_prediction_to_db(prediction[0], data)
        except Exception as e:
            logging.error(f"Error al procesar el mensaje: {e}")

if __name__ == "__main__":
    time.sleep(20)
    start_consumer()
    logging.info("Consumer Terminado.")
