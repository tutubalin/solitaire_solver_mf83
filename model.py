import math
import inspect
from dataclasses import dataclass

from torch.nn import Module
from torch.nn import Conv2d
from torch.nn import Linear
from torch.nn import MaxPool2d
from torch.nn import ReLU
from torch.nn import LogSoftmax
from torch import flatten

import torch
import torch.nn as nn
from torch.nn import functional as F

class CardDetector(nn.Module):

    def __init__(self, numChannels = 1, classes = 13):
        super().__init__()

        self.conv1 = Conv2d(in_channels=numChannels, out_channels=20, kernel_size=(5, 5), padding=2)
        self.relu1 = ReLU()
        self.maxpool1 = MaxPool2d(kernel_size=(2, 2), stride=(2, 2))

        self.conv2 = Conv2d(in_channels=20, out_channels=50, kernel_size=(5, 5), padding=2)
        self.relu2 = ReLU()
        self.maxpool2 = MaxPool2d(kernel_size=(2, 2), stride=(2, 2))

        self.fc1 = Linear(in_features=800, out_features=500)
        self.relu3 = ReLU()

        self.fc2 = Linear(in_features=500, out_features=classes)
        self.logSoftmax = LogSoftmax(dim=1)

    def forward(self, x):

        # print(1, x.shape)

        x = self.conv1(x)

        # print(2, x.shape)

        x = self.relu1(x)

        # print(3, x.shape)

        x = self.maxpool1(x)

        # print(4, x.shape)

        x = self.conv2(x)

        # print(5, x.shape)

        x = self.relu2(x)

        # print(6, x.shape)

        x = self.maxpool2(x)

        # print(7, x.shape)

        x = flatten(x, 1)

        # print(8, x.shape)

        x = self.fc1(x)

        # print(9, x.shape)

        x = self.relu3(x)

        # print(10, x.shape)

        x = self.fc2(x)

        # print(11, x.shape)

        output = self.logSoftmax(x)

        # print(12, x.shape)

        return output
    
    


