from PIL import Image
import numpy as np

screenshot = Image.open('screenshot.png').convert('F')

cards = [[10, 9, 8, 2, 2, 7, 5, 1, 7, 4,13, 2,11],
         [ 6, 6, 1, 7, 4, 2, 9,11,12,10, 8, 8,10],
         [ 8, 3,10, 6, 3,13, 5,12, 9, 5, 3,13,12],
         [ 7,12, 1, 9, 6, 1, 4, 3, 4,11,11, 5,13]]

NUM_WIDTH = 73
NUM_X_OFFSET = 370
NUM_HEIGHT = 73
NUM_Y_OFFSET = 73

counter = [0]*14

inputs = np.zeros((0,16,16), dtype=np.float32)
outputs = np.zeros((0,1), dtype=np.int64)

card_output = []

# for i in range(13):
#     card_arr = np.zeros(13, dtype=np.float32)
#     card_arr[i] = 1
#     card_output.append(card_arr)

for i in range(4):
    x = NUM_X_OFFSET*i
    for j in range(13):
        y = NUM_Y_OFFSET*j
        card = cards[i][j]
        for dx in range(-10,10):
            for dy in range(-10,10):
                num = screenshot.crop((x+dx,y+dy,x+dx+NUM_WIDTH,y+dy+NUM_HEIGHT)).resize((16,16))
                num_arr = np.array(num)/255
                
                inputs = np.append(inputs, [num_arr], axis=0)
                outputs = np.append(outputs, [card-1])

                # num.save(f'images\\{card:02}_{counter[card]:04}.png')
                # counter[card] += 1
        print(f"{(i*13+j)*100/52:.2f}%")

inputs.tofile("inputs.np")
outputs.tofile("outputs.np")