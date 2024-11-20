import csv
import json
import time
from kafka import KafkaProducer

def start_producer():
    # Configuración del producer
    producer = KafkaProducer(
        bootstrap_servers='kafka-stream:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    return producer

# Función para enviar datos desde un archivo CSV
def send_csv_data(file_path, producer):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            producer.send('happiness_data', row)
            print(f"Enviado: {row}")
            time.sleep(1)  # Pausa entre envíos de filas para simular un flujo continuo

if __name__ == "__main__":
    time.sleep(20)
    producer = start_producer()

    # Enviar datos de los archivos CSV
    csv_files = ['data/combined_df.csv']
    for csv_file in csv_files:
        send_csv_data(csv_file, producer)
        print(f"Datos de {csv_file} enviados a Kafka.")
    producer.flush()

