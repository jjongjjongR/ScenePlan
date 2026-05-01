# src/learning/dataset.py

# 2026-05-02 신규: 수집된 HDF5 데모 데이터를 PyTorch에서 사용할 수 있도록 Dataset 형태로 로드합니다.
import h5py
import torch
from torch.utils.data import Dataset
import numpy as np

class DemoDataset(Dataset):
    def __init__(self, hdf5_path):
        self.states = []
        self.actions = []
        
        with h5py.File(hdf5_path, "r") as f:
            data_grp = f["data"]
            for ep_name in data_grp.keys():
                ep_grp = data_grp[ep_name]
                self.states.append(np.array(ep_grp["states"]))
                self.actions.append(np.array(ep_grp["actions"]))
                
        # 여러 에피소드의 데이터를 하나의 큰 배열로 합침
        self.states = np.concatenate(self.states, axis=0)
        self.actions = np.concatenate(self.actions, axis=0)
        
    def __len__(self):
        return len(self.states)
        
    def __getitem__(self, idx):
        return (
            torch.FloatTensor(self.states[idx]),
            torch.FloatTensor(self.actions[idx])
        )
