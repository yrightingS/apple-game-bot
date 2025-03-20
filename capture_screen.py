import pyautogui
import numpy as np
import cv2

def capture_screen():
    """현재 화면을 캡처하여 이미지를 반환"""
    print("📸\t화면 캡처 중...")
    
    screen_width, screen_height = pyautogui.size()
    screenshot = pyautogui.screenshot(region=(0,0, screen_width, screen_height))
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    return screenshot

def preprocess_image(image):
    """이미지 전처리: 대비 증가 + 노이즈 제거 + 선명한 이진화"""
    print("🖼️\t이미지 전처리 중...")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, otsu_thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)

    # 🔍 전처리된 이미지 확인
    # cv2.imshow("Preprocessed Image", otsu_thresh)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return otsu_thresh