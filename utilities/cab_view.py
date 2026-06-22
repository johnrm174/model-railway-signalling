import cv2

stream_url = "http://192.168.1.149:8080"

print("Connecting to ESPHome Cab View stream...")
cap = cv2.VideoCapture(stream_url)

if not cap.isOpened():
    print("Error: Could not open the ESPHome stream.")
    exit()

window_name = "OO Gauge Cab View (ESPHome)"
# Create the window explicitly before the loop so X11 registers it properly
cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

print("Connected! Press 'q' or click 'X' to close.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Dropped frame...")
        continue

    cv2.imshow(window_name, frame)

    # Under X11, cv2.waitKey handles the event queue processing.
    # Increasing this briefly gives the display thread time to flush clicks.
    key = cv2.waitKey(1) & 0xFF

    # CATCH WINDOW CLOSURE UNDER X11/X:
    # If the user clicks 'X', querying ANY property on a destroyed X window 
    # returns -1 or throws an internal error state.
    try:
        prop = cv2.getWindowProperty(window_name, cv2.WND_PROP_AUTOSIZE)
        if prop < 0:
            print("Window closed via GUI. Exiting.")
            break
    except:
        # If X completely dropped the window handle, the query throws an exception
        print("Window handle lost. Exiting.")
        break
        
    # KEYBOARD CHECK
    if key == ord('q'):
        print("'q' pressed. Exiting.")
        break

cap.release()
cv2.destroyAllWindows()
print("Cleaned up successfully.")