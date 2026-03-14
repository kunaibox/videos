import cv2
import numpy as np

CAMERA_INDEX = 1

ASCII_CHARS = "@$B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "

cap = cv2.VideoCapture(CAMERA_INDEX)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if not cap.isOpened():
    print("NO BUENO SORRY")
    exit()

font = cv2.FONT_HERSHEY_PLAIN
font_scale = 1
thickness = 1

ascii_width = 220

char_w = 8
char_h = 16

print("Press Q to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    h, w = gray.shape

    ascii_height = int(h / w * ascii_width * 0.5)

    small = cv2.resize(gray, (ascii_width, ascii_height))

    canvas = np.zeros((ascii_height * char_h, ascii_width * char_w, 3), dtype=np.uint8)

    for y in range(ascii_height):
        for x in range(ascii_width):
            pixel = small[y, x]

            char = ASCII_CHARS[int(pixel) * len(ASCII_CHARS) // 256]

            cv2.putText(
                canvas,
                char,
                (x * char_w, y * char_h + char_h),
                font,
                font_scale,
                (255, 255, 255),
                thickness,
                cv2.LINE_AA
            )

    cv2.imshow("ASCII Camera", canvas)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()