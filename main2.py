from transformers import pipeline

pipe = pipeline(task="depth-estimation", model="Intel/dpt-large")
image="./front1/frame_0001.ply"
result = pipe(image)
result["depth"]
