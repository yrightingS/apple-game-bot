import time
from capture_screen import capture_screen, preprocess_image
from constant import APPLE_SIZE
from digit_recognition import extract_digits, construct_fixed_grid, check_digit_balance, get_go_reset
from solver import find_solution
from automation import execute_drag
from pynput.mouse import Controller, Button

def validate() :
    print("📝\t검증 중...")
    image = capture_screen()
    processed_image = preprocess_image(image)
    digit_data = extract_digits(processed_image)
    grid = construct_fixed_grid(digit_data)

    solution = find_solution(grid)
    if len(solution) == 0 :
        print("☑️\t가능한 조합이 존재하지 않습니다!")
    else :
        print("🆘\t가능한 조합이 존재합니다!")
        execute_drag(solution)

def main():
    time.sleep(2) # 사용자가 화면을 준비할 시간 제공
    _image = capture_screen()
    _processed_image = preprocess_image(_image)
    (go_x, go_y), (reset_x, reset_y) = get_go_reset(_processed_image)

    while True:
        # 리셋 누르기
        print("🔄\t리셋 후 재시작...")
        mouse = Controller()
        mouse.position = (reset_x, reset_y)
        time.sleep(0.1)
        mouse.click(Button.left)
        time.sleep(0.1)
        mouse.position = (go_x, go_y)
        time.sleep(0.1)
        mouse.click(Button.left)
        time.sleep(0.5)
        image = capture_screen()
        processed_image = preprocess_image(image)
        digit_data = extract_digits(processed_image)
        if check_digit_balance(digit_data):
            break

    grid = construct_fixed_grid(digit_data)

    solution = find_solution(grid)
    execute_drag(solution)

if __name__ == "__main__":
    main()