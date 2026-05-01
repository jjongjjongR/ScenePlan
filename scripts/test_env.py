# scripts/test_env.py

# 2026-05-02 신규: 구축된 robosuite 환경이 정상 작동하는지 무작위 행동으로 테스트합니다.
import sys
from pathlib import Path
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.sim.env_setup import create_env

def test_environment():
    print("Initializing robosuite environment...")
    
    # GUI 렌더러를 켜고, 무작위 행동을 50스텝 동안 실행합니다.
    env = create_env(has_renderer=True, has_offscreen_renderer=False)
    
    obs = env.reset()
    print("Environment reset successful.")
    
    print("Running random actions for 50 steps...")
    for i in range(50):
        # 컨트롤러 스페이스에 맞는 랜덤 액션 샘플링
        action = np.random.uniform(-1, 1, env.robots[0].dof)
        obs, reward, done, info = env.step(action)
        env.render()
        
    print("Simulation test completed successfully.")
    env.close()

if __name__ == "__main__":
    test_environment()
