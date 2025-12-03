import pyautogui
import time

# Wait for window to be visible
time.sleep(8)

# Take screenshot
screenshot = pyautogui.screenshot()
screenshot.save("test_screenshot.png")
print("Screenshot saved to test_screenshot.png")
