## Monitoring inventory in retail with Edge Impulse and Renesas RZ/V2L :department_store:

![Cover Image]()

### Quick start :computer:

You can find the public Edge Impulse project here [Inventory tracking in retail with Renesas DRP-AI](https://studio.edgeimpulse.com/public/165074/latest)

Ensure you have a recent version of Python then install the Edge-Impulse Linux Python SDK : 
```
 pip3 install edge_impulse_linux -i https://pypi.python.org/simple
```

Next, install Flask which is required to run the application.
```
pip3 install flask
```

Clone the repository to your target board
```
git clone https://github.com/SolomonGithu/inventory-tracking-with-Edge-Impulse.git
```

Navigate to the repository
```
cd inventory-tracking-with-Edge-Impulse
```
Start the application by running the following command while in the root directory of this repo:
```
python3 app.py
```

Alternatively, this Flask application has also been built as an executable for aarch64 (or amd64) Linux platforms using PyInstaller. This executable is in the ```dist``` folder. Run the commands below to start the executable:
```
cd dist && \ 
chmod u+x app && \
./app
```

### Rebuilding the executable :hammer:

If you want to update the application and rebuild the executable ensure [PyInstaller](https://pyinstaller.org/en/stable/) is installed. 

Since the RZ/V2L is of the AARCH64 platform, we need to ensure this is the target for the built executable. By default, the PyInstaller's bootloaders architecture defaults to the installed machine’s platform. If you want to cross compile on a host computer you can do it by [building the bootloader](https://pyinstaller.org/en/stable/bootloader-building.html) for AARCH64.

Ensure that a terminal is in the parent directory of this repository and build the application with the command:
```
pyinstaller -w -F --add-data "templates:templates" --add-data "static:static" --add-data "modelfile:modelfile" app.py
```

If you see some warnings when looking for dynamic libraries in the build process, first run the command ```sudo ldconfig``` and build the application again.

Lastly start the application with the command :
```
cd dist && ./app
```


