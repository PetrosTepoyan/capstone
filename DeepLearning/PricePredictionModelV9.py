from torch import nn
import timm
import torch
from torch.nn import init

base_neuron_count = 64

class ModifiedInception(nn.Module):
    def __init__(self, output_size):
        super(ModifiedInception, self).__init__()
        # Load and modify the Inception model
        self.inception = timm.create_model('inception_v3', pretrained=True)
        n_features = self.inception.fc.in_features
        self.inception.fc = nn.Linear(n_features, output_size) 

        # Freeze all layers of Inception model except last linear layer
        for param in self.inception.parameters():
            param.requires_grad = False
        for param in self.inception.fc.parameters():
            param.requires_grad = True

    def forward(self, x):
        return self.inception(x)

base_neuron_count = 32

class TabularFFNN(nn.Module):
    def __init__(self, input_size, output_size, dropout_prob=0.18):
        super(TabularFFNN, self).__init__()
        hidden_size = 32
        self.ffnn = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.Dropout(0.05),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size)
        )
        
        for m in self.ffnn:
            if isinstance(m, nn.Linear):
                init.xavier_uniform_(m.weight)
                m.bias.data.fill_(0)

    def forward(self, x):
        x = x.float()
        # print(x)
        x = x.view(x.size(0), -1)
        x = self.ffnn(x)
        return x

class RegressionModel(nn.Module):
    def __init__(self, input_size, dropout_prob = 0.5):
        super(RegressionModel, self).__init__()
        self.regression = nn.Sequential(
            nn.Linear(input_size, base_neuron_count),
            nn.ReLU(),
            nn.Linear(base_neuron_count, base_neuron_count),
            nn.ReLU(),
            nn.Linear(base_neuron_count, 1)  # Output layer for regression, no activation
        )

    def forward(self, x):
        x = self.regression(x)
        return x

class PricePredictionModelV9(nn.Module):
    def __init__(self, tabular_data_size, params):
        super(PricePredictionModelV9, self).__init__()
        # Inception
        inception_model_output_size = params["inception_model_output_size"]
        self.modified_inception = ModifiedInception(inception_model_output_size)
        
        # Tabular
        tabular_ffnn_output_size = params["tabular_ffnn_output_size"]
        self.tabular_ffnn = TabularFFNN(
            input_size = tabular_data_size,
            output_size = tabular_ffnn_output_size
        )
        
        self.regression_model = RegressionModel(
            input_size = inception_model_output_size + tabular_ffnn_output_size
        )

        print("Inception output size", inception_model_output_size)
        print("Tabular output size", tabular_ffnn_output_size)
        print("Regression input size", inception_model_output_size + tabular_ffnn_output_size)
        
    def forward(self, image_tensor, tabular_data):
        image_output = self.modified_inception(image_tensor)
        tabular_output = self.tabular_ffnn(tabular_data)
        combined_output = torch.cat((image_output, tabular_output), dim=1)
        price = self.regression_model(combined_output)
        return price
