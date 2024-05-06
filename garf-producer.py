import cv2
from ultralytics import YOLO
import supervision as sv
import numpy as np

from confluent_kafka import Producer, Consumer

def read_config():
  # reads the client configuration from client.properties
  # and returns it as a key-value map
  config = {}
  with open("client.properties") as fh:
    for line in fh:
      line = line.strip()
      if len(line) != 0 and line[0] != "#":
        parameter, value = line.strip().split('=', 1)
        config[parameter] = value.strip()
  return config

def produce(key,value,config):
  # creates a new producer instance
  producer = Producer(config)

  producer.produce("GarfDetections", key=key[0], value=value)
  print(f"Produced message to topic GarfDetections: key = {key} value = {value}")

  # send any outstanding or buffered messages to the Kafka broker
  producer.poll(10000)
  producer.flush()


def main():
    config = read_config()
    selectedClasses = [15,0] #person, gato
    cap = cv2.VideoCapture(0)
    model = YOLO()

    boxAnnotater = sv.BoundingBoxAnnotator(
        thickness=2
    )

    labelAnnotater = sv.LabelAnnotator(
        text_position=sv.Position.TOP_CENTER,
        text_scale=1,
        text_thickness=2
    )
    
    while True:
        ret, frame = cap.read()
        result = model(frame)[0]

        detections = sv.Detections.from_ultralytics(result)
        detections = detections[np.isin(detections.class_id, selectedClasses)]

        boxedFrame = boxAnnotater.annotate(scene=frame.copy(),detections=detections)
        labeledFrame = labelAnnotater.annotate(scene=boxedFrame.copy(),detections=detections)

        detectedClasses = detections.data.get('class_name')
        print(f"Detected Objects: {detectedClasses}")

        success, encoded_image = cv2.imencode('.jpg', labeledFrame)
        if success:
            produce(detectedClasses,encoded_image, config)
        cv2.imshow('GarfDetector', labeledFrame)

        if cv2.waitKey(30) == 27:
            print("Exiting...")
            break


if __name__ == "__main__":
    main()