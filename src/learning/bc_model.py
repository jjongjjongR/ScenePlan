# src/learning/bc_model.py

# 2026-05-02 신규: State를 입력받아 Action을 예측하는 Behavior Cloning 신경망 구조
import torch
import torch.nn as nn

class BCModel(nn.Module):
    def __init__(self, input_dim, output_dim, hidden_dim=256):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )
        
    def forward(self, x):
        return self.net(x)
