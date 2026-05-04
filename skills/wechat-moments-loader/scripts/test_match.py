"""测试当前屏幕下模板匹配相似度"""
import cv2
import pyautogui
import os
import ctypes

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "templates")

def get_dpi_scale():
    physical_w = ctypes.windll.user32.GetSystemMetrics(0)
    logical_w, _ = pyautogui.size()
    if abs(logical_w - physical_w) < 10:
        return 1.0
    return physical_w / logical_w

def test_template(name, template_path, shot_path):
    screenshot = cv2.imread(shot_path)
    template_orig = cv2.imread(template_path)
    scale = get_dpi_scale()

    print(f"\n[{name}]")
    print(f"  截图尺寸: {screenshot.shape[1]}x{screenshot.shape[0]}")
    print(f"  模板尺寸: {template_orig.shape[1]}x{template_orig.shape[0]}")
    print(f"  DPI scale: {scale:.2f}")

    best = None
    for s in [scale, scale * 1.25, scale * 0.75, 1.0, scale * 1.5, scale * 0.5]:
        th, tw = template_orig.shape[:2]
        new_w, new_h = max(1, int(tw * s)), max(1, int(th * s))
        template = cv2.resize(template_orig, (new_w, new_h))
        if new_h > screenshot.shape[0] or new_w > screenshot.shape[1]:
            continue
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        cx = int((max_loc[0] + new_w // 2) / scale)
        cy = int((max_loc[1] + new_h // 2) / scale)
        if best is None or max_val > best['val']:
            best = {'val': max_val, 'scale': s, 'pos': (cx, cy)}

    print(f"  最佳相似度: {best['val']:.4f}  (scale={best['scale']:.2f}, pos={best['pos']})")
    print(f"  阈值0.7: {'✅ 通过' if best['val'] >= 0.7 else '❌ 未通过'}")
    print(f"  阈值0.6: {'✅ 通过' if best['val'] >= 0.6 else '❌ 未通过'}")
    print(f"  阈值0.5: {'✅ 通过' if best['val'] >= 0.5 else '❌ 未通过'}")

shot_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_fullscreen.png")
print("截图中...")
pyautogui.screenshot(shot_path)
print(f"截图保存: {shot_path}")

for name, fname in [("折叠按钮", "template_arrow.png"), ("微信图标", "template_wechat.png"), ("朋友圈图标", "template_moments.png")]:
    test_template(name, os.path.join(TEMPLATES_DIR, fname), shot_path)
