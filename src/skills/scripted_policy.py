# src/skills/scripted_policy.py

# 2026-05-02 신규: robosuite PickPlace 태스크를 완수하기 위한 기초적인 룰 기반 컨트롤러.
import numpy as np

class ScriptedPickPlacePolicy:
    """
    P-Control 기반의 State Machine 하드코딩 정책입니다.
    실제로 물체(Milk)의 위치를 관측하고 동적으로 로봇 팔을 움직여서 집어올립니다.
    """
    def __init__(self, env):
        self.env = env
        self.state = "APPROACH_HOVER"
        self.grasp_timer = 0
        
    def get_action(self, obs):
        action = np.zeros(7)
        # 기본적으로 OSC_POSE는 위치 제어이므로, 현재 위치와 목표 위치의 차이를 action(속도/이동량)으로 줍니다.
        # 물체 위치 (여기서는 캔 'Can'을 타겟으로 함)
        target_pos = obs.get("Can_pos", np.zeros(3))
        eef_pos = obs.get("robot0_eef_pos", np.zeros(3))
        
        Kp = 5.0  # P-control Gain
        
        if self.state == "APPROACH_HOVER":
            # 물체 위 15cm 상단으로 이동
            hover_pos = target_pos + np.array([0, 0, 0.15])
            action[:3] = (hover_pos - eef_pos) * Kp
            action[6] = -1.0  # 그리퍼 열기
            
            # 목표에 충분히 가까워지면 다음 단계로
            if np.linalg.norm(hover_pos - eef_pos) < 0.02:
                self.state = "APPROACH_DOWN"
                
        elif self.state == "APPROACH_DOWN":
            # 물체 위치로 하강
            grasp_pos = target_pos + np.array([0, 0, -0.01])  # 살짝 더 아래로
            action[:3] = (grasp_pos - eef_pos) * Kp
            action[6] = -1.0  # 그리퍼 열기
            
            if np.linalg.norm(grasp_pos - eef_pos) < 0.02:
                self.state = "GRASP"
                self.grasp_timer = 0
                
        elif self.state == "GRASP":
            # 제자리에서 그리퍼 닫기 대기
            action[:3] = 0.0
            action[6] = 1.0  # 그리퍼 닫기
            self.grasp_timer += 1
            if self.grasp_timer > 30:  # 15 -> 30스텝 동안 꽉 잡기 (학습 데이터 보강)
                self.state = "LIFT"
                
        elif self.state == "LIFT":
            # 꽉 잡은 채로 위로 들기
            lift_pos = target_pos + np.array([0, 0, 0.25])
            action[:3] = (lift_pos - eef_pos) * Kp
            action[6] = 1.0  # 그리퍼 닫음 유지
            
        return action
