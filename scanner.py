from profiler import profile

with profile('Importing PIL...'):
    from PIL import Image
with profile('Importing numpy...'):    
    import numpy as np
with profile('Importing torch...'):            
    import torch
with profile('Importing model...'):        
    from model import CardDetector
with profile('Importing sys...'):        
    import sys

NUM_WIDTH = 72
NUM_X_OFFSET = 371
NUM_HEIGHT = 72
NUM_Y_OFFSET = 72
START_X = 1080
START_Y = 74

filename = sys.argv[1]
# device = "cuda"
device = "cpu"

with profile('Loading model...'):
    model = torch.load('model/model.cpkt').to(device)

with profile(f'Opening {filename}...'):
    screenshot = Image.open(filename).convert('F')

with profile('Getting images...'):
    card_images = list()
    for i in range(4):
        x = NUM_X_OFFSET*i + START_X
        for j in range(13):
            y = NUM_Y_OFFSET*j + START_Y
            num = screenshot.crop((x,y,x+NUM_WIDTH,y+NUM_HEIGHT)).resize((16,16))
            num_arr = np.array(num)/255

            card_images.append([num_arr])

    input = torch.tensor(np.array(card_images)).to(device)

with profile('Scanning...'), torch.no_grad():
    model.eval()
    layout = (torch.argmax(model(input), dim=1)+torch.tensor(1)).cpu().view((4,13))

for column in layout:
    print(" ".join(str(int(x)) for x in column))
