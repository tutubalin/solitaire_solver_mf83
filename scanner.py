from PIL import Image
import numpy as np
from model import CardDetector
from torch import tensor
import torch
import sys

filename = sys.argv[1]

screenshot = Image.open(filename).convert('F')

# screenshot = Image.open('screenshot.png').convert('F')

NUM_WIDTH = 72
NUM_X_OFFSET = 371
NUM_HEIGHT = 72
NUM_Y_OFFSET = 72
START_X = 1080
START_Y = 74

card_images = list()

for i in range(4):
    x = NUM_X_OFFSET*i + START_X
    for j in range(13):
        y = NUM_Y_OFFSET*j + START_Y
        num = screenshot.crop((x,y,x+NUM_WIDTH,y+NUM_HEIGHT)).resize((16,16))
        num_arr = np.array(num)/255

        card_images.append([num_arr])

device = "cuda"

input = tensor(np.array(card_images)).to(device)

model = torch.load('model.cpkt')

with torch.no_grad():
    model.eval()
    output = (torch.argmax(model(input), dim=1)+tensor(1)).cpu().view((4,13))
    print(output)


# print(input[0])


