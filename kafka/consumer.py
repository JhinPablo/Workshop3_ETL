from kafka import KafkaConsumer
import json

# Configuración del consumer
consumer = KafkaConsumer(
    'happiness_data',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

# Procesar los mensajes recibidos
for message in consumer:
    data = message.value
    print(f"Recibido: {data}")
    # Aquí puedes realizar el procesamiento que necesites con los datos
