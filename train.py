from torch.optim import Adam
import numpy as np
from model import CardDetector
from torch.utils.data import random_split
from torch import nn
from torch.utils.data import DataLoader
from sklearn.metrics import classification_report
import torch
import time

INIT_LR = 1e-3
BATCH_SIZE = 256
EPOCHS = 30
TRAIN_SPLIT = 0.70

device = "cuda"

inputs_train = torch.tensor(np.fromfile("data/train/inputs.np", dtype=np.float32).reshape((-1,1,16,16)))
outputs_train = torch.tensor(np.fromfile("data/train/outputs.np", dtype=np.int64))

inputs_test = torch.tensor(np.fromfile("data/test/inputs.np", dtype=np.float32).reshape((-1,1,16,16)))
outputs_test = torch.tensor(np.fromfile("data/test/outputs.np", dtype=np.int64))

train_val_data = list(zip(inputs_train, outputs_train))
test_data = list(zip(inputs_test, outputs_test))

print("[INFO] generating the train/validation split...")
num_train_samples = int(len(train_val_data) * TRAIN_SPLIT)
num_val_samples = len(train_val_data) - num_train_samples

(train_data, val_data) = random_split(train_val_data,
	[num_train_samples, num_val_samples],
	generator=torch.Generator().manual_seed(42))

# initialize the train, validation, and test data loaders
train_data_loader = DataLoader(train_data, shuffle=True, batch_size=BATCH_SIZE)
val_data_loader = DataLoader(val_data, batch_size=BATCH_SIZE)
test_data_loader = DataLoader(test_data, batch_size=BATCH_SIZE)

# calculate steps per epoch for training and validation set
train_steps = len(train_data_loader.dataset) // BATCH_SIZE
val_steps = len(val_data_loader.dataset) // BATCH_SIZE

# initialize the LeNet model
print("[INFO] initializing the LeNet model...")
# model = torch.load("model/model.cpkt").to(device)
model = CardDetector().to(device)

# initialize our optimizer and loss function
opt = Adam(model.parameters(), lr=INIT_LR)
lossFn = nn.NLLLoss()

# initialize a dictionary to store training history
H = {
	"train_loss": [],
	"train_acc": [],
	"val_loss": [],
	"val_acc": []
}

# measure how long training is going to take
print("[INFO] training the network...")
startTime = time.time()

# loop over our epochs
for e in range(0, EPOCHS):
    # set the model in training mode
    model.train()
    # initialize the total training and validation loss
    totalTrainLoss = 0
    totalValLoss = 0
    # initialize the number of correct predictions in the training
    # and validation step
    trainCorrect = 0
    valCorrect = 0
    # loop over the training set
    for (x, y) in train_data_loader:
        # send the input to the device
        (x, y) = (x.to(device), y.to(device))
        # perform a forward pass and calculate the training loss
        pred = model(x)

        # print(pred.shape, y.shape)
        loss = lossFn(pred, y)
        # zero out the gradients, perform the backpropagation step,
        # and update the weights
        opt.zero_grad()
        loss.backward()
        opt.step()
        # add the loss to the total training loss so far and
        # calculate the number of correct predictions
        totalTrainLoss += loss
        trainCorrect += (pred.argmax(1) == y).type(torch.float).sum().item()
		
    # switch off autograd for evaluation
    with torch.no_grad():
        # set the model in evaluation mode
        model.eval()
        # loop over the validation set
        for (x, y) in val_data_loader:
            # send the input to the device
            (x, y) = (x.to(device), y.to(device))
            # make the predictions and calculate the validation loss
            pred = model(x)
            totalValLoss += lossFn(pred, y)
            # calculate the number of correct predictions
            valCorrect += (pred.argmax(1) == y).type(torch.float).sum().item()

    # calculate the average training and validation loss
    avgTrainLoss = totalTrainLoss / train_steps
    avgValLoss = totalValLoss / val_steps
    # calculate the training and validation accuracy
    trainCorrect = trainCorrect / len(train_data_loader.dataset)
    valCorrect = valCorrect / len(val_data_loader.dataset)
    # update our training history
    H["train_loss"].append(avgTrainLoss.cpu().detach().numpy())
    H["train_acc"].append(trainCorrect)
    H["val_loss"].append(avgValLoss.cpu().detach().numpy())
    H["val_acc"].append(valCorrect)
    # print the model training and validation information
    print("[INFO] EPOCH: {}/{}".format(e + 1, EPOCHS))
    print("Train loss: {:.6f}, Train accuracy: {:.4f}".format(
        avgTrainLoss, trainCorrect))
    print("Val loss: {:.6f}, Val accuracy: {:.4f}\n".format(
        avgValLoss, valCorrect))

# finish measuring how long training took
endTime = time.time()
print("[INFO] total time taken to train the model: {:.2f}s".format(endTime - startTime))
# we can now evaluate the network on the test set
print("[INFO] evaluating network...")
# turn off autograd for testing evaluation
with torch.no_grad():
    # set the model in evaluation mode
    model.eval()
	
    # initialize a list to store our predictions
    preds = []
    total = len(test_data_loader.dataset)
    errors = 0
    # loop over the test set
    for (x, y) in test_data_loader:
        # send the input to the device
        x = x.to(device)
		# make the predictions and add them to the list
        pred = model(x)
        pred = pred.argmax(axis=1).cpu()
        preds.extend(pred.numpy())
        if not torch.all(torch.eq(pred,y)):
            print(f"{pred} != {y}")
            errors += sum(pred != y)

    print(f"Errors: {errors}/{total}")


# generate a classification report
# print(classification_report(inputs,
# 	np.array(preds), target_names=['A','2','3','4','5','6','7','8','9','10','J','Q','K']))


torch.save(model, "model/model.cpkt")