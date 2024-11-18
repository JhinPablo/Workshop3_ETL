import csv
import json
from kafka import KafkaProducer

# Configuración del producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Tópico de Kafka
topic = 'happiness_data'

# Función para enviar datos desde un archivo CSV
def send_csv_data(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            producer.send(topic, row)
            print(f"Enviado: {row}")

# Enviar datos de los archivos CSV
csv_files = ['data/2015.csv', 'data/2016.csv', 'data/2017.csv', 'data/2018.csv', 'data/2019.csv']
for csv_file in csv_files:
    send_csv_data(csv_file)

# Cerrar el producer
producer.flush()
producer.close()
