# capstone

[Figma Pipelines](https://www.figma.com/file/QyKBl6YhZuI0D9D86thCc3/Pipelines?type=whiteboard&node-id=0%3A1&t=KCB0szRzkneM0i9G-1)


The scraping is not consistent when reproducing - apartments get added and removed from the websites.

To train the model on M1 mac, run this\
`python3 train_model.py -device "mps:0" -data data_tiny -images images_tiny -model v3`

To train the model on a Linux with CUDA, run this\
`python3 train_model.py -device "cuda" -data data -images images -model v2`

Change arguments as needed: