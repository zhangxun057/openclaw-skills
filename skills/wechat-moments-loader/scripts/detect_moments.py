"""
Detect WeChat window and Moments icon location
"""
import cv2
import pyautogui
import win32gui
import os
import sys

pyautogui.FAILSAFE = False

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(SKILL_DIR, "assets", "templates")

def get_dpi_scale():
    try:
        import ctypes
        physical_w = ctypes.windll.user32.GetSystemMetrics(0)
        logical_w, _ = pyautogui.size()
        if abs(logical_w - physical_w) < 10:
            return 1.0
        return physical_w / logical_w
    except:
        return 1.0

def find_icon_in_screenshot(screenshot, template_path, threshold=0.7):
    template_orig = cv2.imread(template_path)
    if screenshot is None or template_orig is None:
        return None
    
    scale = get_dpi_scale()
    best = None
    
    for s in [scale, scale * 1.25, scale * 0.75, 1.0]:
        th, tw = template_orig.shape[:2]
        new_w, new_h = max(1, int(tw * s)), max(1, int(th * s))
        template = cv2.resize(template_orig, (new_w, new_h))
        
        if new_h > screenshot.shape[0] or new_w > screenshot.shape[1]:
            continue
        
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        
        if best is None or max_val > best['similarity']:
            best = {
                'position': (max_loc[0] + new_w // 2, max_loc[1] + new_h // 2),
                'similarity': float(max_val),
                'scale': s
            }
    
    if best and best['similarity'] >= threshold:
        return best
    return None

def find_wechat_window():
    result = []
    def callback(hwnd, _):
        title = win32gui.GetWindowText(hwnd)
        if title == "微信":
            rect = win32gui.GetWindowRect(hwnd)
            result.append({'hwnd': hwnd, 'title': title, 'rect': rect})
        return True
    win32gui.EnumWindows(callback, None)
    return result[0] if result else None

def main():
    screen_width, screen_height = pyautogui.size()
    print(f"Screen size: {screen_width} x {screen_height}")
    print("=" * 50)
    
    # 1. Find WeChat window
    wechat = find_wechat_window()
    if not wechat:
        print("WeChat window NOT found")
        return
    
    left, top, right, bottom = wechat['rect']
    width = right - left
    height = bottom - top
    
    print(f"Found WeChat window:")
    print(f"   Position: ({left}, {top}) - ({right}, {bottom})")
    print(f"   Size: {width} x {height}")
    print(f"   On screen: left={left}px, top={top}px")
    
    # 2. Screenshot WeChat window
    screenshot = pyautogui.screenshot()
    wechat_screenshot = screenshot.crop((left, top, right, bottom))
    
    # 3. Find Moments icon in window
    import numpy as np
    wechat_cv = cv2.cvtColor(np.array(wechat_screenshot), cv2.COLOR_RGB2BGR)
    
    moments_template = os.path.join(TEMPLATES_DIR, "template_moments.png")
    match = find_icon_in_screenshot(wechat_cv, moments_template, threshold=0.6)
    
    if match:
        # Relative to window
        rel_x, rel_y = match['position']
        # Absolute screen position
        abs_x = left + rel_x
        abs_y = top + rel_y
        
        print(f"\nFound Moments icon:")
        print(f"   Relative to window: ({rel_x}, {rel_y})")
        print(f"   Absolute screen: ({abs_x}, {abs_y})")
        print(f"   Similarity: {match['similarity']:.2f}")
        print(f"   Scale: {match['scale']:.2f}")
        
        # Describe position
        rel_pos_desc = ""
        if rel_y < height * 0.2:
            rel_pos_desc += "Top"
        elif rel_y > height * 0.8:
            rel_pos_desc += "Bottom"
        elif rel_y > height * 0.4 and rel_y < height * 0.6:
            rel_pos_desc += "Middle"
        else:
            rel_pos_desc += "Lower-middle"
            
        if rel_x < width * 0.3:
            rel_pos_desc += "-Left"
        elif rel_x > width * 0.7:
            rel_pos_desc += "-Right"
        else:
            rel_pos_desc += "-Center"
            
        print(f"   Position: {rel_pos_desc}")
        
        # Check if in bottom nav area
        if rel_y > height * 0.85:
            print(f"   Icon is in BOTTOM NAV area (y > {height * 0.85:.0f})")
        elif rel_y < height * 0.15:
            print(f"   Icon is in TOP area")
        else:
            print(f"   Icon is in MIDDLE area")
            
    else:
        print(f"\nMoments icon NOT found in WeChat window")
        print(f"   Search area: entire window ({width} x {height})")
        print(f"   Template: {moments_template}")
        print(f"   Threshold: 0.6")

if __name__ == "__main__":
    main()
