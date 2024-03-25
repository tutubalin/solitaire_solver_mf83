from PIL import Image
import numpy as np
import glob
from sys import argv

for metadataFilename in glob.glob(argv[1]+"/*.txt"):
    with open(metadataFilename) as f:
        screenshotFile = argv[1] + "/" + f.readline().strip()
        NUM_START_X, NUM_START_Y = map(int, f.readline().split())
        NUM_WIDTH, NUM_HEIGHT = map(int, f.readline().split())
        NUM_X_OFFSET, NUM_Y_OFFSET = map(int, f.readline().split())
        NUM_DX_FROM, NUM_DX_TO, NUM_DX_STEP = map(int, f.readline().split())
        NUM_DY_FROM, NUM_DY_TO, NUM_DY_STEP = map(int, f.readline().split())

        cards = [[int(card)for card in f.readline().split()] for _ in range(4)]    

    screenshot = Image.open(screenshotFile).convert('F')    

    counter = [0]*14

    inputs_list = []
    outputs_list = []

    card_output = []

    print(screenshotFile)

    for i in range(4):
        x = NUM_START_X + NUM_X_OFFSET*i
        for j in range(13):
            y = NUM_START_Y +  NUM_Y_OFFSET*j
            card = cards[i][j]
            for dx in range(NUM_DX_FROM, NUM_DX_TO, NUM_DX_STEP):
                for dy in range(NUM_DY_FROM, NUM_DY_TO, NUM_DY_STEP):
                    num = screenshot.crop((x+dx,y+dy,x+dx+NUM_WIDTH,y+dy+NUM_HEIGHT)).resize((16,16))
                    num_arr = np.array(num)/255
                    
                    inputs_list.append(num_arr)
                    outputs_list.append(card-1)

                    # num.convert('L').save(f'img\\{card:02}_{counter[card]:04}.png')
                    counter[card] += 1
            print(f"\b\b\b\b\b\b\b{(i*13+j)*100/52:.2f}%")

inputs = np.array(inputs_list, dtype=np.float32)
outputs = np.array(outputs_list, dtype=np.int64)

inputs.tofile(argv[1]+"/inputs.np")
outputs.tofile(argv[1]+"/outputs.np")