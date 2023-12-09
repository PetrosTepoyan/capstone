import pandas as pd
import torch
import torch.nn as nn
import timm
import os
from torch import optim
from torchvision import transforms
from torch.utils.data import Dataset, DataLoader, random_split
from tqdm import tqdm
# from DeepLearning import PricePredictionModel, ApartmentsDatasetPyTorch, DataSubsetter, 
from DeepLearning import *
import argparse
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description="Training arguments")
parser.add_argument('-device', metavar='device', type=str, help='device to search | mps:0')
parser.add_argument('-data', metavar='data', type=str, help='data name')
parser.add_argument('-images', metavar='images', type=str, help='images name')
parser.add_argument('-model', metavar='model', type=str, help='model version')
parser.add_argument('-continue_training', metavar='continue_training', type=str, help='model version')

args = parser.parse_args()
device_to_search = args.device
data_dir = args.data
images_dir = args.images
model_version = args.model
continue_training_model = args.continue_training

if data_dir is None:
    print("Provide data directory: -data")
    exit()
    
if images_dir is None:
    print("Provide images directory: -images")

print("Data directory", data_dir)
print("Images directory", images_dir)
print("Device", device_to_search)

if continue_training_model:
    print("Continuing", continue_training_model)

params = {
    "data_dir" : data_dir,
    "images_dir" : images_dir,
    "img_input_size" : 256,
    "batch_size" : 64,
    "shuffle" : True,
    
    "inception_model_output_size" : 128,
    "tabular_ffnn_output_size" : 128,
    "learning_rate" : 0.5e-3,
    "weight_decay" : 1e-4
}

if device_to_search is None:
    device_to_search = "cpu"
    
device = torch.device(device_to_search)
if not device:
    raise Exception("Device not found")

transform = transforms.Compose([
    transforms.Resize((params["img_input_size"], params["img_input_size"])),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])  # Normalize images
])

subsetter = DataSubsetter(
    data_dir = params["data_dir"]
)

cols_to_remove = ["coordinates", 'latitude', 'longitude']
dataframe = subsetter.without(
    cols = cols_to_remove
)
print("Removing columns", cols_to_remove)

dataset = ApartmentsDatasetPyTorch(
    device = device,
    dataframe = dataframe,
    images_dir = params["images_dir"], 
    transform = transform
)
print("Tabular Size", len(dataset.df))

if model_version == "v1":
    model = PricePredictionModel(
        dataset.tabular_data_size(), 
        params
    )
elif model_version == "v2":
    model = PricePredictionModelV2(
        dataset.tabular_data_size(), 
        params
    )
elif model_version == "v3":
    model = PricePredictionModelV3(
        dataset.tabular_data_size(), 
        params
    )
elif model_version == "v4":
    model = PricePredictionModelV4(
        dataset.tabular_data_size(), 
        params
    )
elif model_version == "v5":
    model = PricePredictionModelV5(
        dataset.tabular_data_size(), 
        params
    )
elif model_version == "v6":
    model = PricePredictionModelV6(
        dataset.tabular_data_size(), 
        params
    )
elif model_version == "v7":
    model = PricePredictionModelV7(
        dataset.tabular_data_size(), 
        params
    )
elif model_version == "v8":
    model = PricePredictionModelV8(
        dataset.tabular_data_size(), 
        params
    )
else:
    print("Supply model version. v1, v2, v3, v4, v5, v6, v7, v8")
    exit()
    
if continue_training_model:
    model.load_state_dict(torch.load(continue_training_model))

model = model.to(device)
print("Model ready")

print("Total length of the dataset", len(dataset))

# Assuming 'dataset' is your full dataset
train_size = int(0.8 * len(dataset))
val_size = int(0.1 * len(dataset))
test_size = len(dataset) - train_size - val_size
num_epochs = 1000
train_dataset, val_dataset, test_dataset = random_split(dataset, [train_size, val_size, test_size])
num_GPU = 1

train_loader = DataLoader(
    train_dataset,
    batch_size=params["batch_size"], 
    shuffle=params["shuffle"]
)
val_loader = DataLoader(
    val_dataset,
    batch_size=params["batch_size"],
    shuffle=False
)
test_loader = DataLoader(
    test_dataset,
    batch_size=params["batch_size"], 
    shuffle=False
)

print("Train size", len(train_loader))
print("Val size", len(val_loader))
print("Test size", len(test_loader))
print()

# Count weights and neurons
total_weights = sum(p.numel() for p in model.parameters() if p.requires_grad)
total_neurons = sum(layer.out_features for layer in model.modules() if isinstance(layer, nn.Linear))

print(f"Total Weights: {total_weights}")
print(f"Total Neurons: {total_neurons}")
print()

# Initialize lists to track losses
train_losses = []
val_losses = []
epochs_suc = [] # to have a reference to it

optimizer = optim.Adam(
    model.parameters(), 
    lr=params["learning_rate"],
    weight_decay = params["weight_decay"]
)
criterion = torch.nn.MSELoss()
criterion_abs = torch.nn.L1Loss()

print("Starting training...")
# Training loop with progress bar
def train():
    for epoch in range(num_epochs):
        # Training
        model.train()  # Set the model to training mode
        running_loss = 0.0
        l1_losses = []
        for data in tqdm(train_loader, desc=f'Epoch {epoch+1}/{num_epochs} - Training'):
            images, datas, prices = data
            optimizer.zero_grad()
            outputs = model(images, datas)
            prices_viewed = prices.view(-1, 1).float()
            loss = criterion(outputs, prices_viewed)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        train_losses.append(running_loss / len(train_loader))  # Average loss for this epoch

        # Validation
        model.eval()  # Set the model to evaluation mode
        val_loss = 0.0
        with torch.no_grad():  # Disable gradient calculation
            for data in tqdm(val_loader, desc=f'Epoch {epoch+1}/{num_epochs} - Validation'):
                images, datas, prices = data
                outputs = model(images, datas)  # Forward pass
                prices_viewed = prices.view(-1, 1).float()
                loss = criterion(outputs, prices_viewed)  # Compute loss
                val_loss += loss.item()  # Accumulate the loss
                l1_losses.append(criterion_abs(outputs, prices_viewed))
            
        val_losses.append(val_loss / len(val_loader))  # Average loss for this epoch
        l1_mean_loss = sum(l1_losses) / len(l1_losses)
        # Print epoch's summary
        epochs_suc.append(epoch)
        print(f'Epoch {epoch+1}, Training Loss: {int(train_losses[-1])}, Validation Loss: {int(val_losses[-1])}, L1: {int(l1_mean_loss)}')

def save_results():
    model_version_directory = f"models/model_{model_version}"

    if not os.path.exists(model_version_directory):
        os.makedirs(model_version_directory)
        
    existing_model_count = int(len(os.listdir(model_version_directory)) / 2)
    this_model_name = f"model_{model_version}_{existing_model_count}"

    # Saving the model
    torch.save(model.state_dict(), f"{model_version_directory}/{this_model_name}.pth")

    plt.title("Model evaluation")
    plt.plot(train_losses, label = 'Training')
    plt.plot(val_losses, label = 'Validation')
    plt.ylabel("MSE")
    plt.xlabel("Epoch")
    plt.yscale('log')
    plt.xticks(range(1, epochs_suc[-1], int(epochs_suc[-1] / 10)))
    plt.legend()
    plt.savefig(f'{model_version_directory}/{this_model_name}_training.png')

try:
    train()
except Exception as e:
    print(e)
    save_results()
    print("Script interrupted. Cleaning up...")

