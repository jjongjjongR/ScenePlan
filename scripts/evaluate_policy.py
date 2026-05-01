# scripts/evaluate_policy.py

# 2026-05-02 신규: 학습된 BC 모델을 로드하여 시뮬레이터 환경에서 직접 테스트합니다.
import sys
from pathlib import Path
import torch
import numpy as np
import os

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.sim.env_setup import create_env
from src.learning.bc_model import BCModel

def evaluate():
    model_path = "data/models/bc_model.pt"
    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}. Please run train_bc.py first.")
        return
        
    print("Initializing environment for evaluation...")
    env = create_env(has_renderer=False, has_offscreen_renderer=False)
    
    # 저장된 모델 가중치로부터 input_dim, output_dim 유추
    state_dict = torch.load(model_path)
    input_dim = state_dict['net.0.weight'].shape[1]
    output_dim = state_dict['net.4.bias'].shape[0]
    
    model = BCModel(input_dim, output_dim)
    model.load_state_dict(state_dict)
    model.eval()
    
    print("Starting evaluation (5 episodes)...")
    num_episodes = 5
    for ep in range(num_episodes):
        obs = env.reset()
        print(f"  - Episode {ep+1} started.")
        
        for step in range(50):
            state_vec = np.concatenate([v for k, v in obs.items() if isinstance(v, np.ndarray) and v.ndim == 1])
            state_tensor = torch.FloatTensor(state_vec).unsqueeze(0)
            
            with torch.no_grad():
                action = model(state_tensor).squeeze(0).numpy()
                
            obs, reward, done, info = env.step(action)
            # env.render()
            
    env.close()
    print("✅ Evaluation complete.")

if __name__ == "__main__":
    evaluate()
