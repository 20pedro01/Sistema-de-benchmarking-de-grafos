from PIL import Image
import os

def crop_icons():
    # Pack 1 (2x2)
    img1 = Image.open("/Users/pedro/.gemini/antigravity/brain/46f9b3b9-75b5-48d4-a528-005cc18f9e24/icons_pack_1_1777291444168.png")
    w, h = img1.size
    img1.crop((0, 0, w//2, h//2)).save("assets/icons/dice.png")
    img1.crop((w//2, 0, w, h//2)).save("assets/icons/check.png")
    img1.crop((0, h//2, w//2, h)).save("assets/icons/pencil.png")
    img1.crop((w//2, h//2, w, h)).save("assets/icons/rocket.png")

    # Pack 2 (3x3 grid)
    img2 = Image.open("/Users/pedro/.gemini/antigravity/brain/46f9b3b9-75b5-48d4-a528-005cc18f9e24/icons_pack_2_1777291463940.png")
    w, h = img2.size
    dw, dh = w//3, h//3
    img2.crop((0, 0, dw, dh)).save("assets/icons/negative.png")
    img2.crop((dw, 0, 2*dw, dh)).save("assets/icons/loop.png")
    img2.crop((2*dw, 0, w, dh)).save("assets/icons/trash.png")
    img2.crop((2*dw, dh, w, 2*dh)).save("assets/icons/pdf.png")
    img2.crop((2*dw, 2*dh, w, h)).save("assets/icons/refresh.png")

if __name__ == "__main__":
    crop_icons()
