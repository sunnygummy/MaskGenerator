Structure of the code should be as follows:
MaskGenerator/

├── Dashboard.py

├── /Vignetting

│   ├── Vignetting.exe

│   ├── _internal

│   └── runs/unet

│       └── unet_best.pt

├── /Vessels? eventually

_internal is a folder of all the library requirements from the .venv
runs/unet/unet_best.pt is the training weights. Eventually I need to replace this with a better trained model

To create a .exe file based on predict.py use the following command. Make sure you are in the right .venv first.
When you use this to create an exe, the whole Vignetting folder is generated with the _internal and runs/unet included.

pyinstaller --clean --noconfirm --onedir --noconsole --name Vignetting --add-data "runs/unet;runs/unet" predict.py
