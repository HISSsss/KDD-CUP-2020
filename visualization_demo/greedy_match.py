import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import math
import random
from networks import *
from buffers import *
import copy

a = np.random.randint(5, size=(3, 3))
b = np.random.randint(9, size=(3, 3))


def f1(x):
    return 2 * a


def mse_loss(x, target_x):
    return np.square((x - target_x)) / (2 * x.size)


loss = mse_loss(f1(a), b)
print(a.size, 'loss:', loss, 'mean:', loss.mean())



