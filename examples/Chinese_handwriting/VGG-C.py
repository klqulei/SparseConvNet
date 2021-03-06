# Copyright 2016-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import torch
import torch.nn as nn
import sparseconvnet as scn
from data import get_iterators

# two-dimensional SparseConvNet
class Model(nn.Module):
    def __init__(self):
        nn.Module.__init__(self)
        self.sparseModel = scn.SparseVggNet(2, 3, [
            ['C', 16], ['C', 16], 'MP',
            ['C', 32], ['C', 32], 'MP',
            ['C', 48], ['C', 48], 'MP',
            ['C', 64], ['C', 64], 'MP',
            ['C', 96], ['C', 96]]
        ).add(scn.Convolution(2, 96, 128, 3, 2, False)
        ).add(scn.BatchNormReLU(128)
        ).add(scn.SparseToDense(2, 128))
        self.linear = nn.Linear(128, 3755)

    def forward(self, x):
        x = self.sparseModel(x)
        x = x.view(-1, 128)
        x = self.linear(x)
        return x

model = Model()
spatial_size = model.sparseModel.input_spatial_size(torch.LongTensor([1, 1]))
print('Input spatial size:', spatial_size)
dataset = get_iterators(spatial_size, 63, 3)
scn.ClassificationTrainValidate(
    model, dataset,
    {'n_epochs': 100,
     'initial_lr': 0.1,
     'lr_decay': 0.05,
     'weight_decay': 1e-4,
     'use_gpu': torch.cuda.is_available(),
     'check_point': True, })
