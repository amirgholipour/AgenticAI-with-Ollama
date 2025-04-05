import cv2
import base64
import json
from kafka import KafkaProducer, KafkaConsumer
import ollama
import threading
import tempfile
import os
import queue
import yaml
from kafka.admin import KafkaAdminClient, NewTopic

# Load configuration from the YAML file
with open('config/config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

# Access configuration parameters
kafka_topic = config['KAFKA_TOPIC']
bootstrap_servers = config['BOOTSTRAP_SERVERS']
frame_interval = config['FRAME_INTERVAL']
batch_size = config['BATCH_SIZE']
resized_width = config['RESIZED_WIDTH']
resized_height = config['RESIZED_HEIGHT']
model = config['MODEL']
prompt = config['PROMPT']

def extract_frames(video_path, frame_interval, width, height):
    cap = cv2.VideoCapture(video_path)
    frames = []
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % frame_interval == 0:
            resized_frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
            _, buffer = cv2.imencode('.jpg', resized_frame)
            encoded_frame = base64.b64encode(buffer).decode('utf-8')
            frames.append(encoded_frame)
            if len(frames) == batch_size:
                yield frames
                frames = []
        frame_count += 1

    cap.release()
    if frames:
        yield frames

def send_frames_to_kafka(video_path, kafka_topic, bootstrap_servers):
    producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
                             value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    for frame_batch in extract_frames(video_path, frame_interval, resized_width, resized_height):
        producer.send(kafka_topic, frame_batch)
    producer.flush()

def analyze_frames_with_llm(frames, model, prompt):
    images = [base64.b64decode(frame) for frame in frames]
    messages = [{"role": "user", "content": prompt, "images": images}]
    response = ollama.chat(model=model, messages=messages)
    return response['message']['content']

def consume_frames_from_kafka(kafka_topic, bootstrap_servers, result_queue):
    consumer = KafkaConsumer(kafka_topic,
                             bootstrap_servers=bootstrap_servers,
                             value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                             auto_offset_reset='earliest',
                             enable_auto_commit=True)
    overall_summary = []

    for message in consumer:
        frame_batch = message.value
        batch_summary = analyze_frames_with_llm(frame_batch, model, prompt)
        overall_summary.append(batch_summary)
        if len(overall_summary) >= 1:  # Optional exit condition for testing/demo
            break

    final_summary = " ".join(overall_summary)
    result_queue.put(final_summary)

def clear_kafka_topic(topic, bootstrap_servers):
    """
    Deletes and re-creates a Kafka topic to clear its history.
    """
    try:
        admin = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
        admin.delete_topics([topic])
        admin.create_topics([NewTopic(name=topic, num_partitions=1, replication_factor=1)])
    except Exception as e:
        print(f"⚠️ Failed to reset Kafka topic: {e}")

def process_video(video_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmpfile:
        tmpfile.write(video_file.read())
        tmpfile_path = tmpfile.name

        clear_kafka_topic(kafka_topic, bootstrap_servers)
    result_queue = queue.Queue()

    consumer_thread = threading.Thread(target=consume_frames_from_kafka, args=(kafka_topic, bootstrap_servers, result_queue))
    consumer_thread.start()

    send_frames_to_kafka(tmpfile_path, kafka_topic, bootstrap_servers)

    consumer_thread.join()

    os.remove(tmpfile_path)

    final_summary = result_queue.get()
    return final_summary
