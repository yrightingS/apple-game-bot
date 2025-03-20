import time
from pynput.mouse import Controller, Button

TICK = 0.05

def execute_drag(solution):
    """
    solution 리스트에 저장된 (x1, y1, x2, y2) 좌표를 사용해 자동 드래그 실행
    """
    if not solution:
        print("❌\t드래그할 조합이 없습니다.")
        return

    print("🚀\t자동 드래그 시작!")

    mouse = Controller()
    for (x1, y1, x2, y2) in solution:
        print(f"🖱️\t드래그: ({x1}, {y1}) → ({x2}, {y2})")
        mouse.position = (x1, y1)
        time.sleep(TICK)  # 안정화를 위한 대기
        mouse.press(Button.left)  # 마우스 누르기
        time.sleep(TICK)  # 안정화
        mouse.position = (x2, y2)  # 이동
        time.sleep(TICK)
        mouse.release(Button.left)  # 마우스 떼기
        time.sleep(TICK)

    print("✅\t모든 드래그 작업 완료!")