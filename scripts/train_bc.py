# scripts/train_bc.py

# 2026-05-02 신규: 모은 데이터를 바탕으로 신경망을 Behavior Cloning(지도학습) 방식으로 학습시킵니다.
import sys
from pathlib import Path
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import os

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.learning.dataset import DemoDataset
from src.learning.bc_model import BCModel

def train():
    dataset_path = "data/datasets/demo_dataset.hdf5"
    if not os.path.exists(dataset_path):
        print(f"Dataset not found at {dataset_path}. Please run collect_demonstrations.py first.")
        return
        
    dataset = DemoDataset(dataset_path)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
    
    input_dim = dataset.states.shape[1]
    output_dim = dataset.actions.shape[1]
    
    model = BCModel(input_dim, output_dim)
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.MSELoss()
    
    print(f"Starting BC training. Input dim: {input_dim}, Output dim: {output_dim}")
    print(f"Total dataset size: {len(dataset)} steps")
    
    num_epochs = 100
    for epoch in range(num_epochs):
        total_loss = 0
        for states, actions in dataloader:
            optimizer.zero_grad()
            preds = model(states)
            loss = criterion(preds, actions)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            
        avg_loss = total_loss / len(dataloader)
        if (epoch + 1) % 5 == 0 or epoch == 0:
            print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {avg_loss:.6f}")
            
    os.makedirs("data/models", exist_ok=True)
    torch.save(model.state_dict(), "data/models/bc_model.pt")
    print("✅ Training complete. Model saved to data/models/bc_model.pt")

if __name__ == "__main__":
    train()
