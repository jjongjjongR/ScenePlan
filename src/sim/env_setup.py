# src/sim/env_setup.py

# 2026-05-02 신규: robosuite 기반 PickPlace 시뮬레이션 환경 구축
import robosuite as suite

def create_env(has_renderer=True, has_offscreen_renderer=False):
    """
    robosuite의 기본 PickPlace 환경을 Franka Panda 로봇으로 생성합니다.
    
    Args:
        has_renderer (bool): 화면에 GUI 창을 띄울지 여부 (로컬 디버깅용)
        has_offscreen_renderer (bool): 카메라 관측값(이미지)을 렌더링할지 여부
    """
    env = suite.make(
        env_name="PickPlace",
        robots="Panda",             # Franka Emika Panda 로봇 사용
        has_renderer=has_renderer,
        has_offscreen_renderer=has_offscreen_renderer,
        render_camera="frontview",
        ignore_done=True,           # 태스크가 끝나도 에피소드를 강제로 종료하지 않음
        use_camera_obs=False,       # State-based 정책 실험을 위해 초기에는 False
        control_freq=20,            # 제어 주기 (20Hz)
    )
    
    return env
