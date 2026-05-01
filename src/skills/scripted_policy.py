# src/skills/scripted_policy.py

# 2026-05-02 신규: robosuite PickPlace 태스크를 완수하기 위한 기초적인 룰 기반 컨트롤러.
import numpy as np

class ScriptedPickPlacePolicy:
    """
    간단한 State Machine 기반의 하드코딩 정책입니다.
    데이터 수집용으로 동작하며, 대략적인 조작(Grasp -> Lift)을 수행합니다.
    """
    def __init__(self, env):
        self.env = env
        self.state = "APPROACH"
        self.step_count = 0
        
    def get_action(self, obs):
        # OSC_POSE 액션: [dx, dy, dz, dax, day, daz, gripper]
        action = np.zeros(7)
        self.step_count += 1
        
        # 임시 타이머 기반 스테이트 전환 (실제로는 거리 기반으로 정교화 필요)
        if self.step_count < 15:
            self.state = "APPROACH"
            action[2] = -0.05       # 아래로 이동
            action[6] = -1.0        # 그리퍼 열림 유지
        elif self.step_count < 20:
            self.state = "GRASP"
            action[2] = 0.0         # 대기
            action[6] = 1.0         # 그리퍼 닫음
        elif self.step_count < 35:
            self.state = "LIFT"
            action[2] = 0.05        # 위로 들기
            action[6] = 1.0
        elif self.step_count < 45:
            self.state = "MOVE"
            action[0] = 0.05        # 앞으로 이동
            action[6] = 1.0
        else:
            self.state = "PLACE"
            action[6] = -1.0        # 그리퍼 열기
            
        return action
