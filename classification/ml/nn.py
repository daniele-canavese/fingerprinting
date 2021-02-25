"""
Neural networks stuff.
"""
from torch import Tensor
from torch.nn import Dropout
from torch.nn import Linear
from torch.nn import Module
from torch.nn import ReLU
from torch.nn import Sequential
from torch.nn import Softmax


class NeuralModule(Module):
    """
    The feed-forward neural network for classifying the traffic.
    """

    def __init__(self, inputs: int, outputs: int, layers: int, neurons_per_layer: int, p: float):
        """
        Creates the module.
        :param inputs: the number of input neurons
        :param outputs: the number of output neurons
        :param layers: the number of layers
        :param neurons_per_layer: the number of neurons in the hidden layers
        :param p: the dropout probability
        """

        super(NeuralModule, self).__init__()

        modules = []
        if layers == 1:
            modules.append(Linear(inputs, outputs))
            modules.append(Softmax(dim=-1))
        else:
            modules.append(Linear(inputs, neurons_per_layer))
            modules.append(ReLU())
            for _ in range(layers - 2):
                modules.append(Linear(neurons_per_layer, neurons_per_layer))
                modules.append(ReLU())
                modules.append(Dropout(p))
            modules.append(Linear(neurons_per_layer, outputs))
            modules.append(Softmax(dim=-1))

        self.__modules = Sequential(*modules)

    def forward(self, x: Tensor) -> Tensor:
        """
        Performs the forward pass.
        :param x: the input tensor to process
        :return: the resulting tensor
        """

        return self.__modules(x)
