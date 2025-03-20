import os
import sys
import cv2
import numpy as np
from collections import Counter
from constant import GRID_ROWS, GRID_COLS, APPLE_SIZE

import os
import cv2

def get_go_reset(image):
    """img 폴더에서 go, reset 템플릿을 찾고 좌표 반환"""
    coords = []
    img_dir = "img"  # 이미지 폴더 경로
    threshold = 0.8  # 매칭 유사도 임계값

    for i in ["go", "reset"]:
        template_path = os.path.join(img_dir, f"{i}.png")
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)

        if template is None:
            print(f"❌ 템플릿 {i}.png을(를) 찾을 수 없습니다.")
            continue  # 해당 템플릿이 없으면 다음으로 넘어감

        # 템플릿 매칭 수행
        result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # 유사도가 낮으면 무시
        if max_val < threshold:
            print(f"⚠️ {i} 버튼을 찾지 못했습니다. (유사도: {max_val:.2f})")
            continue

        # 중심 좌표 계산
        h, w = template.shape[:2]
        center_x, center_y = max_loc[0] + w / 2, max_loc[1] + h / 2
        coords.append((center_x, center_y))

    return coords  # 최종 좌표 반환


def load_templates():
    """img 폴더에서 1.png ~ 9.png 숫자 템플릿 로드"""
    templates = {}
    img_dir = "img"  # 이미지 폴더 경로
    for i in range(1, 10):
        template_path = os.path.join(img_dir, f"{i}.png")
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is not None:
            templates[i] = template
        else:
            print(f"⚠️\t숫자 템플릿 {template_path}을(를) 찾을 수 없음.")
    return templates

def match_digit(roi, templates, threshold=0.8):
    """ROI와 숫자 템플릿을 비교하여 가장 유사한 숫자를 반환"""

    roi = cv2.resize(roi, (templates[1].shape[1], templates[1].shape[0]))  # ROI 크기 맞추기
    best_match = -1
    best_score = -1

    for digit, template in templates.items():
        result = cv2.matchTemplate(roi, template, cv2.TM_CCOEFF_NORMED)
        score = np.max(result)  # 유사도 점수

        if score > best_score:
            best_match = digit
            best_score = score

    return best_match if best_score >= threshold else -1

TEMPLATES = load_templates()

def extract_digits(image):
    """이미지에서 숫자를 감지하고 좌표와 함께 반환"""
    print("🔢\t숫자 추출 중...")
    contours, _ = cv2.findContours(image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    digit_data = []

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if h > APPLE_SIZE and w > APPLE_SIZE:  # 작은 잡음 제거
            roi = image[y:y+h, x:x+w]
            digit = match_digit(roi, TEMPLATES)

            if digit > 0:  # 숫자인 경우만 저장
                digit_data.append((int(digit), x, y))

    if len(digit_data) < 170:
        print(f"⚠️\t숫자 추출 실패 데이터 감지.")

    return digit_data

def check_digit_balance(digit_data):
    """digit_data에서 각 숫자의 빈도를 조사하고 조건을 만족하는지 확인 및 로깅"""
    
    # 🔹 1. digit 빈도수 계산
    digit_counts = Counter(digit for digit, _, _ in digit_data)

    # 🔹 3. 조건 확인
    condition_1 = digit_counts.get(1, 0) >= digit_counts.get(9, 0)
    condition_2 = digit_counts.get(2, 0) >= digit_counts.get(8, 0)
    condition_3 = digit_counts.get(3, 0) >= digit_counts.get(7, 0)
    condition_4 = digit_counts.get(4, 0) >= digit_counts.get(6, 0)

    all_conditions_met = condition_1 and condition_2 and condition_3 and condition_4

    # 🔹 4. 결과 출력
    print("📌\t조건 검증 중...")
    print(f"✅\t1의 개수 ({digit_counts.get(1, 0)}) >= 9의 개수 ({digit_counts.get(9, 0)}) → {'✔️' if condition_1 else '❌'}")
    print(f"✅\t2의 개수 ({digit_counts.get(2, 0)}) >= 8의 개수 ({digit_counts.get(8, 0)}) → {'✔️' if condition_2 else '❌'}")
    print(f"✅\t3의 개수 ({digit_counts.get(3, 0)}) >= 7의 개수 ({digit_counts.get(7, 0)}) → {'✔️' if condition_3 else '❌'}")
    print(f"✅\t4의 개수 ({digit_counts.get(4, 0)}) >= 6의 개수 ({digit_counts.get(6, 0)}) → {'✔️' if condition_4 else '❌'}")

    return all_conditions_met  # 모든 조건을 만족하면 True, 아니면 False
    
def construct_fixed_grid(digit_data):
    """숫자 데이터를 10x17 고정 크기의 2D 배열로 변환"""
    if not digit_data:
        return [[None] * GRID_COLS for _ in range(GRID_ROWS)]  # 빈 배열 반환

    # x, y 좌표의 최소값을 기준으로 상대 위치 계산
    x_min = min(d[1] for d in digit_data)
    y_min = min(d[2] for d in digit_data)

    # x, y 좌표 최대값 계산 (최대 범위)
    x_max = max(d[1] for d in digit_data)
    y_max = max(d[2] for d in digit_data)

    # 열과 행 간격 계산 (평균적인 간격 측정)
    row_spacing = (y_max - y_min) / (GRID_ROWS - 1)
    col_spacing = (x_max - x_min) / (GRID_COLS - 1)

    # 10x17 그리드 초기화
    grid = [[[None] * 3] * GRID_COLS for _ in range(GRID_ROWS)]

    # 숫자를 그리드의 올바른 위치에 배치
    for digit, x, y in digit_data:
        col_index = round((x - x_min) / col_spacing)
        row_index = round((y - y_min) / row_spacing)

        # 인덱스가 범위를 초과하지 않도록 보정
        col_index = min(max(col_index, 0), GRID_COLS - 1)
        row_index = min(max(row_index, 0), GRID_ROWS - 1)

        grid[row_index][col_index] = [digit, x, y]

    return grid