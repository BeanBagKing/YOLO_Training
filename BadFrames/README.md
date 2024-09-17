Used for sorting out bad/corrupted frames from legitimate images.

Settings: `yolo task=detect mode=train epochs=100 data=data.yaml model=yolov8s.pt imgsz=640 patience=20 name=badframes save_json=True project=C:\outputfolder`
