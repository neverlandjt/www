from kafka import KafkaProducer
from json import dumps, loads
import requests


def publish_message(producer_instance, topic_name, value):
    try:
        producer_instance.send(topic_name, value=value)
        producer_instance.flush()
        print('Message published successfully.')
    except Exception as ex:
        print('Exception in publishing message')
        print(str(ex))


def connect_kafka_producer(addr=['172.31.87.124:9092']):
    producer = None
    try:
        producer = KafkaProducer(bootstrap_servers=addr,
                                 value_serializer=lambda x:
                                 dumps(x).encode('utf-8'))
    except Exception as ex:
        print('Exception while connecting Kafka')
        print(str(ex))
    finally:
        return producer


if __name__ == '__main__':
    topic = 'wiki'
    kafka_producer = connect_kafka_producer()
    print('Producer connected...')
    stream_link = 'https://stream.wikimedia.org/v2/stream/page-create'
    print('Load data...')
    try:
        r = requests.get(stream_link, stream=True)

        if r.encoding is None:
            r.encoding = 'utf-8'

        for line in r.iter_lines(decode_unicode=True):
            if line:
                split = line.split()
                if split[0] == 'data:':
                    publish_message(kafka_producer, topic, loads(" ".join(split[1:])))

    except KeyboardInterrupt:
        print("Close connection...")
        if kafka_producer is not None:
            kafka_producer.close()
