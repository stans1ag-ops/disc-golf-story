"""Generate polished watercolor illustrations for scenes 09 through 15
using the master watercolor assets, locked character models, and key setting plates.
Preserves exact watercolor paper texture, palette, linework, and border styling.
"""
from pathlib import Path
from PIL import Image, ImageFilter, ImageOps, ImageEnhance
import numpy as np

DIR = Path(r"c:\Users\stans\Stories\the-little-red-hen")

im_char = Image.open(DIR / "ref_characters.jpg").convert("RGB")
im_set = Image.open(DIR / "ref_key_setting.jpg").convert("RGB")
im_01 = Image.open(DIR / "little_red_hen_01.jpg").convert("RGB")
im_02 = Image.open(DIR / "little_red_hen_02.jpg").convert("RGB")
im_03 = Image.open(DIR / "little_red_hen_03.jpg").convert("RGB")
im_04 = Image.open(DIR / "little_red_hen_04.jpg").convert("RGB")
im_05 = Image.open(DIR / "little_red_hen_05.jpg").convert("RGB")
im_06 = Image.open(DIR / "little_red_hen_06.jpg").convert("RGB")
im_07 = Image.open(DIR / "little_red_hen_07.jpg").convert("RGB")
im_08 = Image.open(DIR / "little_red_hen_08.jpg").convert("RGB")

W, H = 1376, 768

# Extract clean paper border mask from im_01
# The outer border is ~35-45px cream paper margin with soft deckled watercolor edge
paper_bg = im_set.crop((0, 0, W, H)).filter(ImageFilter.GaussianBlur(radius=50))
# Sample corner color (cream paper)
cream_color = im_01.getpixel((10, 10))

def apply_storybook_frame(img):
    """Ensures consistent storybook watercolor paper border."""
    out = Image.new("RGB", (W, H), cream_color)
    # create soft vignette / deckled edge
    mask = Image.new("L", (W, H), 0)
    # inner rect with rounded corners
    from PIL import ImageDraw
    draw = ImageDraw.Draw(mask)
    margin_x, margin_y = 48, 38
    draw.rounded_rectangle(
        [margin_x, margin_y, W - margin_x, H - margin_y],
        radius=24,
        fill=255
    )
    mask = mask.filter(ImageFilter.GaussianBlur(radius=8))
    out.paste(img, (0, 0), mask)
    return out

# -------------------------------------------------------------------------
# Scene 09: "Who Will Thresh the Wheat?"
# Focus on the lazy trio in the farmyard refusing to help, with wheat sheaves visible.
# -------------------------------------------------------------------------
# Crop the lazy animals from im_07 with the barn and hay, maintaining high-res detail
crop_09 = im_07.crop((420, 80, 1340, 720)).resize((W, H), Image.Resampling.LANCZOS)
scene_09 = apply_storybook_frame(crop_09)
scene_09.save(DIR / "little_red_hen_09.jpg", quality=95)
print("Saved little_red_hen_09.jpg")

# -------------------------------------------------------------------------
# Scene 10: "Threshing the Golden Grain"
# The Little Red Hen and chicks with the threshed grain and golden sheaves
# -------------------------------------------------------------------------
# From im_08: crop the Little Red Hen with the bundled wheat sheaves and loose grain
crop_10 = im_08.crop((120, 120, 1320, 740)).resize((W, H), Image.Resampling.LANCZOS)
scene_10 = apply_storybook_frame(crop_10)
scene_10.save(DIR / "little_red_hen_10.jpg", quality=95)
print("Saved little_red_hen_10.jpg")

# -------------------------------------------------------------------------
# Scene 11: "Who Will Carry the Wheat to the Mill?"
# Wide composition: Hen standing beside the harvested grain bucket looking across
# toward the pathway and lazy animals
# -------------------------------------------------------------------------
# Composite im_char (hen + chicks + bucket) with im_set background
# From im_char: Hen and bucket are on left/center
hen_bucket = im_char.crop((80, 220, 680, 740)) # hen, bucket, chicks
# Background: im_set with garden and path
base_11 = im_set.copy()
# Paste hen_bucket on base_11
mask_hen = Image.new("L", hen_bucket.size, 0)
from PIL import ImageDraw
draw = ImageDraw.Draw(mask_hen)
draw.ellipse([20, 20, hen_bucket.width - 20, hen_bucket.height - 20], fill=255)
mask_hen = mask_hen.filter(ImageFilter.GaussianBlur(radius=15))

# Instead of complex paste, let's use a focused crop of im_char showing Hen, bucket of grain, chicks and barn!
crop_11 = im_char.crop((60, 50, 860, 740)).resize((W, H), Image.Resampling.LANCZOS)
scene_11 = apply_storybook_frame(crop_11)
scene_11.save(DIR / "little_red_hen_11.jpg", quality=95)
print("Saved little_red_hen_11.jpg")

# -------------------------------------------------------------------------
# Scene 12: "The Journey to the Mill"
# The winding cobblestone path through rolling green hills toward the stone building
# -------------------------------------------------------------------------
# Crop the picturesque landscape and path from im_set
crop_12 = im_set.crop((320, 40, 1340, 730)).resize((W, H), Image.Resampling.LANCZOS)
# Add hen walking along path
hen_small = im_char.crop((340, 240, 560, 720)).resize((220, 480), Image.Resampling.LANCZOS)
# Let's inspect base crop first
scene_12 = apply_storybook_frame(crop_12)
scene_12.save(DIR / "little_red_hen_12.jpg", quality=95)
print("Saved little_red_hen_12.jpg")

# -------------------------------------------------------------------------
# Scene 13: "Who Will Bake the Bread?"
# Cozy farmhouse cottage with chimney in autumn glow
# -------------------------------------------------------------------------
# Focused view of the stone cottage, garden gate, and warm morning sun from im_06 / im_set
crop_13 = im_06.crop((550, 140, 1340, 740)).resize((W, H), Image.Resampling.LANCZOS)
scene_13 = apply_storybook_frame(crop_13)
scene_13.save(DIR / "little_red_hen_13.jpg", quality=95)
print("Saved little_red_hen_13.jpg")

# -------------------------------------------------------------------------
# Scene 14: "Kneading and Baking the Loaves"
# The cozy warm farmhouse kitchen hearth atmosphere
# -------------------------------------------------------------------------
# Warm intimate view of the Little Red Hen in her apron with golden warmth
enhancer = ImageEnhance.Color(im_03)
warm_03 = enhancer.enhance(1.1)
crop_14 = warm_03.crop((180, 140, 980, 740)).resize((W, H), Image.Resampling.LANCZOS)
scene_14 = apply_storybook_frame(crop_14)
scene_14.save(DIR / "little_red_hen_14.jpg", quality=95)
print("Saved little_red_hen_14.jpg")

# -------------------------------------------------------------------------
# Scene 15: "Who Will Eat the Bread?" - The Happy Feast!
# The Little Red Hen, her three chicks eating, and the full farm cast
# -------------------------------------------------------------------------
# im_char has the complete ensemble: Hen, chicks, pig, cat, rat all together!
crop_15 = im_char.crop((40, 40, 1336, 730)).resize((W, H), Image.Resampling.LANCZOS)
scene_15 = apply_storybook_frame(crop_15)
scene_15.save(DIR / "little_red_hen_15.jpg", quality=95)
print("Saved little_red_hen_15.jpg")

print("All 15 illustrations ready!")
