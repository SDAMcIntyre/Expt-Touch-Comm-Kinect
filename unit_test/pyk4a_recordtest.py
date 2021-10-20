from pyk4a import PyK4A

# Load camera with the default config
k4a = PyK4A()
k4a.start()

# Get the next capture (blocking function)
capture = k4a.get_capture()
img_color = capture.color

# Display with pyplot
from matplotlib import pyplot as plt
plt.imshow(img_color[:, :, 2::-1]) # BGRA to RGB
plt.show()
