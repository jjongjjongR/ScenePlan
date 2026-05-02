# scripts/collect_demonstrations.py

# 2026-05-02 신규: Scripted Policy를 실행하여 Behavior Cloning에 쓸 데이터를 수집합니다.
import sys
from pathlib import Path
import h5py
import numpy as np
import os

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.sim.env_setup import create_env
from src.skills.scripted_policy import ScriptedPickPlacePolicy

def collect_data(num_episodes=200, max_steps=300):
    env = create_env(has_renderer=False, has_offscreen_renderer=False)
    
    os.makedirs("data/datasets", exist_ok=True)
    dataset_path = "data/datasets/demo_dataset.hdf5"
    
    print(f"Starting data collection: {num_episodes} episodes...")
    with h5py.File(dataset_path, "w") as f:
        data_grp = f.create_group("data")
        
        for ep in range(num_episodes):
            ep_grp = data_grp.create_group(f"demo_{ep}")
            obs = env.reset()
            policy = ScriptedPickPlacePolicy(env)
            
            states = []
            actions = []
            
            for step in range(max_steps):
                # 딕셔너리 형태의 observation 중 1차원 벡터들만 모아서 state로 사용
                state_vec = np.concatenate([v for k, v in obs.items() if isinstance(v, np.ndarray) and v.ndim == 1])
                
                action = policy.get_action(obs)
                
                states.append(state_vec)
                actions.append(action)
                
                obs, reward, done, info = env.step(action)
                
            ep_grp.create_dataset("states", data=np.array(states))
            ep_grp.create_dataset("actions", data=np.array(actions))
            print(f"  - Collected episode {ep+1}/{num_episodes} (Steps: {max_steps})")
            
    env.close()
    print(f"✅ Data collection complete. Saved to {dataset_path}")

if __name__ == "__main__":
    collect_data()
