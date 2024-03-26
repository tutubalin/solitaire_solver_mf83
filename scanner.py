from profiler import profile

with profile('Importing built-ins...'):
    import sys
    import os
    import time
with profile('Importing PIL...'):
    from PIL import Image
with profile('Importing numpy...'):    
    import numpy as np
with profile('Importing torch...'):            
    import torch
with profile('Importing model...'):        
    from model import CardDetector

NUM_WIDTH = 72
NUM_X_OFFSET = 371
NUM_HEIGHT = 72
NUM_Y_OFFSET = 72
START_X = 1080
START_Y = 74

filename = "tmp/screenshot.png"
# device = "cuda"
device = "cpu"

with profile('Loading model...'):
    model = torch.load('model/model.cpkt').to(device)

print('\033[1;32mReady\033[0m', file=sys.stderr, flush=True)

while True:

    if os.path.isfile(filename):
        time.sleep(0.1)
        print('\033[1;36mScreenshot found\033[0m', file=sys.stderr, flush=True)

        with profile(f'Opening screenshot...'):
            screenshot = Image.open(filename).convert('F')
            os.remove(filename)

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
        
        print('\033[1;32mReady\033[0m', file=sys.stderr, flush=True)
    else:
        time.sleep(0.5)
