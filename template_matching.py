import cv2

# Provide absolute paths for images
template_path = '/Users/prathameshsutone/Code/pythonpoc/reference/reference.png'
image_path = '/Users/prathameshsutone/Code/pythonpoc/screenshot.png'

# Load images
template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

# Check if images are loaded
if template is None:
    raise FileNotFoundError(f"Error: Template image not found at {template_path}")
if image is None:
    raise FileNotFoundError(f"Error: Target image not found at {image_path}")

# Proceed with feature matching
orb = cv2.ORB_create()
keypoints1, descriptors1 = orb.detectAndCompute(template, None)
keypoints2, descriptors2 = orb.detectAndCompute(image, None)

bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
matches = bf.match(descriptors1, descriptors2)
matches = sorted(matches, key=lambda x: x.distance)

output_image = cv2.drawMatches(template, keypoints1, image, keypoints2, matches[:10], None, flags=2)
cv2.imwrite('/Users/prathameshsutone/Code/pythonpoc/output/matches.jpg', output_image)
cv2.imshow('Matches', output_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
