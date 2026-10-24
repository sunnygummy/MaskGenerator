import torch
import numpy as np
from PIL import Image
from pathlib import Path
import argparse
import sys
from models.unet import UNet

# Path to the checkpoint produced by training
# ============================================================
# APPLICATION PATH
# ============================================================
if getattr(sys, "frozen", False):
    # Directory containing Predict.exe
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    # Directory containing predict.py
    BASE_DIR = Path(__file__).resolve().parent

# External model checkpoint
CKPT_PATH = (
    BASE_DIR
    / "runs"
    / "unet"
    / "unet_best.pt"
)
# Prediction threshold
THR = 0.5

# Supported image types
IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".tif",
    ".tiff",
    ".bmp",
}


# ============================================================
# LOAD MODEL
# ============================================================

def load_model():

    if not CKPT_PATH.exists():
        raise FileNotFoundError()

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    checkpoint = torch.load(
        CKPT_PATH,
        map_location=device
    )

    # Use the same image size used during training
    img_size = checkpoint.get(
        "img_size",
        256
    )

    # Use the same base channel count used during training
    base_channels = checkpoint.get(
        "base",
        64
    )

    model = UNet(
        in_ch=3,
        out_ch=1,
        base=base_channels
    ).to(device)

    model.load_state_dict(
        checkpoint["model"]
    )

    model.eval()

    print("Model loaded successfully.")

    return model, device, img_size


# ============================================================
# GENERATE ONE MASK
# ============================================================

def generate_mask(
    model,
    device,
    img_size,
    image_path,
    output_path
):

    image_path = Path(image_path)
    output_path = Path(output_path)

    if not image_path.exists():
        raise FileNotFoundError()

    # --------------------------------------------------------
    # Load image using Pillow
    # --------------------------------------------------------

    image = Image.open(
        image_path
    ).convert("RGB")

    original_size = image.size

    image = image.resize(
        (img_size, img_size),
        Image.Resampling.BILINEAR
    )

    # --------------------------------------------------------
    # Convert image to tensor
    # --------------------------------------------------------

    img_arr = (
        np.array(image)
        .astype(np.float32)
        / 255.0
    )

    img_t = (
        torch.from_numpy(img_arr)
        .permute(2, 0, 1)
        .unsqueeze(0)
    )

    # --------------------------------------------------------
    # Generate prediction
    # --------------------------------------------------------

    with torch.no_grad():

        logits = model(
            img_t.to(device)
        )

        probs = torch.sigmoid(
            logits
        )

        mask = probs > THR

    # --------------------------------------------------------
    # Convert mask to image
    # --------------------------------------------------------

    mask_np = (
        mask[0, 0]
        .cpu()
        .numpy()
        .astype(np.uint8)
        * 255
    )

    mask_image = Image.fromarray(
        mask_np,
        mode="L"
    )

    # --------------------------------------------------------
    # Return mask to original image size
    # --------------------------------------------------------

    mask_image = mask_image.resize(
        original_size,
        Image.Resampling.NEAREST
    )

    # --------------------------------------------------------
    # Save mask
    # --------------------------------------------------------

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    mask_image.save(
        output_path,
        format="TIFF"
    )


# ============================================================
# FIND IMAGES
# ============================================================

def find_images(input_path):

    input_path = Path(input_path)

    # --------------------------------------------------------
    # Single image
    # --------------------------------------------------------

    if input_path.is_file():

        if (
            input_path.suffix.lower()
            not in IMAGE_EXTENSIONS
        ):
            raise ValueError()

        return [input_path]

    # --------------------------------------------------------
    # Folder
    # --------------------------------------------------------

    if input_path.is_dir():

        images = sorted(
            [
                p
                for p in input_path.iterdir()
                if (
                    p.is_file()
                    and p.suffix.lower()
                    in IMAGE_EXTENSIONS
                )
            ]
        )

        if not images:

            raise RuntimeError()

        return images

    # --------------------------------------------------------
    # Doesn't exist
    # --------------------------------------------------------

    raise FileNotFoundError()


# ============================================================
# MAIN
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Generate vignetting masks using "
            "a trained U-Net."
        )
    )

    # --------------------------------------------------------
    # INPUT
    # --------------------------------------------------------

    parser.add_argument(
        "input_path",
        help=(
            "Path to an image or folder "
            "containing images."
        )
    )

    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    parser.add_argument(
        "--out",
        required=True,
        help=(
            "Folder where generated masks "
            "will be saved."
        )
    )

    args = parser.parse_args()

    # --------------------------------------------------------
    # Convert paths
    # --------------------------------------------------------

    input_path = Path(
        args.input_path
    )

    output_dir = Path(
        args.out
    )

    # --------------------------------------------------------
    # Find images
    # --------------------------------------------------------

    image_paths = find_images(
        input_path
    )

    # --------------------------------------------------------
    # Load model ONCE
    # --------------------------------------------------------

    model, device, img_size = load_model()

    print()

    # --------------------------------------------------------
    # Generate masks
    # --------------------------------------------------------

    for image_path in image_paths:

        output_path = (
            output_dir
            / f"{image_path.stem}_mvig.tif"
        )

        print(
            f"Processing: {image_path.name}"
        )

        generate_mask(
            model=model,
            device=device,
            img_size=img_size,
            image_path=image_path,
            output_path=output_path
        )

if __name__ == "__main__":
    main()
