from PIL import Image
import numpy as np
import glob
from sys import argv
import torch

device = "cpu"

model = torch.load('model/model.cpkt').to(device)

for metadataFilename in glob.glob(argv[1]+"/*.txt"):
    with open(metadataFilename) as f:
        screenshotFile = argv[1] + "/" + f.readline().strip()
        NUM_START_X, NUM_START_Y = map(int, f.readline().split())
        NUM_WIDTH, NUM_HEIGHT = map(int, f.readline().split())
        NUM_X_OFFSET, NUM_Y_OFFSET = map(int, f.readline().split())
        NUM_DX_FROM, NUM_DX_TO, NUM_DX_STEP = map(int, f.readline().split())
        NUM_DY_FROM, NUM_DY_TO, NUM_DY_STEP = map(int, f.readline().split())

        cards = torch.tensor([[int(card)for card in f.readline().split()] for _ in range(4)])

    screenshot = Image.open(screenshotFile).convert('F')

    card_images = list()
    for i in range(4):
        x = NUM_X_OFFSET*i + NUM_START_X
        for j in range(13):
            y = NUM_Y_OFFSET*j + NUM_START_Y
            num = screenshot.crop((x,y,x+NUM_WIDTH,y+NUM_HEIGHT)).resize((16,16))
            num_arr = np.array(num)/255

            card_images.append([num_arr])

    input = torch.tensor(np.array(card_images)).to(device)
    
    print(screenshotFile)

    model.eval()
    layout = (torch.argmax(model(input), dim=1)+torch.tensor(1)).cpu().view((4,13))

    if not torch.all(torch.eq(cards, layout)):
        print('error!')

