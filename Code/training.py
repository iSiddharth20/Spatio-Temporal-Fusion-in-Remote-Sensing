'''
Module for Training Models
Separate Functions for Training AutoEncoder and LSTM Models
Saves the Model with the Lowest Validation Loss
--------------------------------------------------------------------------------
Forward Pass: Compute Output from Model from the given Input
Backward Pass: Compute the Gradient of the Loss with respect to Model Parameters
Initialize Best Validation Loss to Infinity as we will save model with lowest validation loss
'''

# Import Necessary Libraries
import torch

# Define Training Class
class Trainer():
    def __init__(self, model, loss_function, model_save_path):
        # Define the device
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        # Define the model and move it to the device
        self.model = model.to(self.device)
        # Define the loss function
        self.loss_function = loss_function
        # Define the optimizer
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        # Define the path to save the model
        self.model_save_path = model_save_path

    def save_model(self):
        # Save the model
        torch.save(self.model.state_dict(), self.model_save_path)

    def train_autoencoder(self, epochs, train_loader, val_loader):
        best_val_loss = float('inf')  
        for epoch in range(epochs):
            self.model.train()  # Set the Model to Training Mode
            # Training Loop
            for input, target in train_loader:  # Input - Grayscale Image, Target - RGB Image
                input, target = input.to(self.device), target.to(self.device)
                output = self.model(input)  # Forward Pass
                loss = self.loss_function(output, target)  # Compute Training Loss
                self.optimizer.zero_grad()  # Zero gradients to prepare for Backward Pass
                loss.backward()  # Backward Pass
                self.optimizer.step()  # Update Model Parameters
            # Validation Loss Calculation
            self.model.eval()  # Set the Model to Evaluation Mode
            with torch.no_grad():  # Disable gradient computation
                val_loss = 0.0
                val_loss = sum(self.loss_function(self.model(input.to(self.device)), target.to(self.device)).item() for input, target in val_loader)  # Compute Total Validation Loss
                val_loss /= len(val_loader)  # Compute Average Validation Loss
            # Print the epoch number and the validation loss
            print(f'Epoch : {epoch}, Validation Loss : {val_loss}')
            # If the current validation loss is lower than the best validation loss, save the model
            if val_loss < best_val_loss:
                best_val_loss = val_loss  # Update the best validation loss
                self.save_model()  # Save the model
        # Return the Trained Model
        return self.model

    def train_lstm(self, epochs, n_interpolate_frames, train_data, val_data):
        min_val_loss = float('inf')  # Initialize the minimum validation loss to infinity
        # Loop over the number of epochs
        for epoch in range(epochs):
            self.model.train() # Set the model to training mode
            # Training Loop
            for sequence, target in train_data:
                self.optimizer.zero_grad() # Reset the gradients accumulated from the previous iteration
                sequence, target = sequence.to(self.device), target.to(self.device)  # Moved both to the device
                output = self.model(sequence, n_interpolate_frames)
                loss = self.loss_function(output, target) # Compute Training Loss
                loss.backward() # Backward Pass
                self.optimizer.step() # Update Model Parameters
            # Validation Loss Calculation
            self.model.eval() # Set the Model to Evaluation Mode
            with torch.no_grad():
                val_loss = 0.0
                for sequence, target in val_data:
                    sequence = sequence.to(self.device)
                    target = target.to(self.device)
                    output = self.model(sequence, n_interpolate_frames)
                    val_loss += self.loss_function(output, target).item()  # Calculate loss only on interpolated frames
                val_loss /= len(val_data)
            # Print the epoch number and the validation loss
            print(f'Epoch : {epoch}, Validation Loss : {val_loss}')
            # If the current validation loss is lower than the best validation loss, save the model
            if val_loss < min_val_loss:
                min_val_loss = val_loss # Update the best validation loss
                self.save_model() # Save the model
        # Return the Trained Model
        return self.model