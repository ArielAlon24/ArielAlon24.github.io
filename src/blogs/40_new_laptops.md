---
name: "40 New Laptops"
date: 2024-02-18
---

## Surprise

In my programming class at school, each student has the option to bring their own laptop or utilize one of the numerous laptops and PCs provided in class. Recently, my class received a shipment of about 40 new laptops.

![Many Laptops](/assets/images/many-laptops.webp)

Each of these devices required a comprehensive setup process - installation of various software, programming languages with their related modules, and more. Traditionally, this time consuming task fell upon a handful of dedicated students willing to invest hours into the process, often to discover at the very end that Python was still not properly configured in the system's path.

## Idea

Not sure why, but I felt like there was something that could be done to simplify this process. With a motivation to learn about Windows automation, I started a new Git repository named Winstaller with a fellow classmate. A script designed to automatically download and install software, programming languages, and more.

## Batch? PowerShell?

The Git repository was successfully initialized, but what next? As a first instinct, I created a [batch file](https://en.wikipedia.org/wiki/Batch_file), the Windows scripting file counterpart to Unix's bash. However, after consulting ChatGPT and conducting some Google searches, I encountered several limitations, especially regarding web requests. While technically possible by using a wrapper around PowerShell commands, this approach closely resembles the use of an `exec()` call inside a Python script resulting in less than elegant code.

Therefore, I decided to opt for batch's more capable sibling, [PowerShell](https://en.wikipedia.org/wiki/PowerShell), and deleted the previously created batch file. Opening a new file named `installer.ps1`, we were in business. The goal is to create a script that will install Python, in the correct version and then run a python script in the same folder.

## Installing Python

Let's start with a simple print statement:

```ps1
Write-Host "Starting installation script."
```

Next, we need to check if Python is already installed; if it's not, we'll proceed to install it. To determine if Python is installed, we can use the command python -V. If we receive an output in either stdout (indicating a successful operation) or stderr (indicating an error), we can conclude that Python is indeed installed.

```ps1
$pythonVersion = &{python -V} 2>&1
```

Notice variable deceleration is super simple, using a `$<name> = value` syntax. The `2>&1` redirection merges both stderr and stdout into the same variable, `$pythonVersion`, allowing us to handle the output uniformly. Now, to check if `$pythonVersion` variable is empty or not we can use the built-in `string` function `[string]::IsNullOrWhiteSpace()` in the end

```ps1
if ([string]::IsNullOrWhiteSpace($pythonVersion)) {
    Write-Host "Python is not installed, proceeding with installation..."

    # -=- Here we'll install python -=-

} else {
    Write-Host "Python is already installed: $pythonVersion"
}
```

How to install Python you ask? using the built-ins `Invoke-WebRequest` to download the
Python installer, and `Start-Process` to run the installer.

```ps1
# Download Python Installer
$installerUri = "https://www.python.org/ftp/python/3.10.9/python-3.10.9-amd64.exe"
$installerPath = "$env:TEMP\python-3.10.9-amd64.exe"
Invoke-WebRequest -Uri $installerUri -OutFile $installerPath -ErrorAction Stop

# Install Python Installer
Write-Host "Installing Python 3.10.9..."
Start-Process -FilePath $installerPath -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 TargetDir=C:\Python310-64" -Wait -ErrorAction Stop
Write-Host "Python 3.10.9 installation completed."
```

Lastly, we need to run the Python script that we'll discuss later, this is super simple

```ps1
$env:Path += ";C:\Python310-64"

$script = "script.py"
$executable = "C:\Python310-64\python.exe"

# Execute the Python script
Write-Host "Running script."
& $executable $script
```

The only important thing to notice here, is the manual appending of the Python installation to the path, that's because PowerShell won't update automatically the path unless restarted.

## The Python Script

After we got Python installed there is no reason to keep on working in PowerShell, so here come a new file `script.py`, to make things OOP I, with the help of my classmate created a class to represent a program, with an `__init__`, `download`, `install` and `clean` methods.

Let's first look on the `__init__` method

```Python
class Program:

    def __init__(self, name: str, url: str) -> None:
        self.name = name
        self.url = url
        self.installer = url.split("/")[-1]
```

Using the fact that the installer name is the same as the last part of the URL we can make the constructor work with two supplied parameters.

## Download and Install methods

Now for the `download` method, utilizing the `requests` module, wait, we need to install the `requests` module!

## Installing and Using Python Modules inside a Python script

A bit of a complex header for a simple task, and quite similar to the way we handled the existence of Python in the PowerShell script. Firstly, the `import` python keyword calls a the dunder function `__import__` with a `str` type for the name of the module to be imported. So to check if a module can be imported we can use the `__import__` dunder with it's name and check if any exceptions occur, especially `ImportError` which indicates this module isn't downloaded yet.

Using the `subprocess` module which don't be scared, is a built-in, we can use `pip` - Python's package manger. To install any module with the following line:

```Python
import subprocess
import sys

subprocess.run(
    [sys.executable, "-m", "pip", "install", name, "-q"], check=True
)
```

`sys` was imported (Again, a built-in) to retrieve the executable path.

Now we can construct a simple function, one that checks if a certain module exists, if it does it logs to the screen it's existence, otherwise, downloads it.

```Python
import subprocess
import sys
import logging


def install_module(name: str) -> None:
    try:
        __import__(name=name)
    except ImportError:
        logging.info(f"Package '{name}' was not found. Installing...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", name, "-q"], check=True
            )
            logging.info(f"Module {name} was installed successfully.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to install module '{name}': {e}")
            raise e
```

For those who aren't familiar with the `logging`, think of it as a pretty-print statement, I've used it to give better feedback on the script runtime. Logs look something like this:

```
2024-02-19 13:07:09,128 - INFO - Package 'requests' was not found. Installing...
2024-02-19 13:07:11,448 - INFO - Module requests was installed successfully.
```

This exact format can be acheived by changing the global format option for the logging module (It's more correct to create a specifiec logger for each main object in the system, but as of the small size of this script a single main logging entry is sufficient).

```Python
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
```

## Download and Install methods V2 (now we have requests)

### Download

Download was straightforward, by using the `requests` module we obtained access to, and making a get request to the installer URL, with the additional `stream` flag set to `True`. The installer file will be sent and chunk by chunk will be saved.

```Python
def download(self) -> None:
        logging.info(f"Downloading {self.name}.")
        try:
            with requests.get(self.url, stream=True) as r:
                r.raise_for_status()
                total_size_in_bytes = int(r.headers.get("content-length", 0))
                progress_bar = tqdm(
                    total=total_size_in_bytes, unit="iB", unit_scale=True
                )
                with open(self.installer, "wb") as f:
                    for chunk in r.iter_content(chunk_size=self.CHUNK_SIZE):
                        progress_bar.update(len(chunk))
                        f.write(chunk)
                progress_bar.close()
                if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
                    logging.error("ERROR, something went wrong")
            logging.info(f"Downloaded '{self.name}' successfully.")
        except requests.RequestException as e:
            logging.error(f"Error downloading '{self.name}': {e}")
            raise Exception(f"Error downloading '{self.name}': {e}")
```

In order to make the user understand clearly what part of the script is running, also here some log messages were added, and in top of that, a simple progress bar was added using the `tqdm` module.

### Install

Install on the other hand, involved some understanding. Windows installers can vary but they usually come in one of two forms, as an executable or as a `.msi` file which is the standard Windows installer. So, to properly run the installer we need to match the installer suffix to one of the ways, this is done by a simple `if` `else` block.

To run an executable installer, it's possible just to provide it as an argument to the `subprocess.run` function. But in the case of the `.msi` file we need to use the [Window Installer](https://en.wikipedia.org/wiki/Windows_Installer)(`msiexec.exe`) which is the software that runs those installers. Also quite simple to run just, the software name needs to be passed as well. Finnaly we got

```Python
def install(self) -> None:
    logging.info(f"Installing {self.name}.")
    try:
        if self.installer.endswith(".exe"):
            subprocess.run([self.installer, "/S"], check=True)
        elif self.installer.endswith(".msi"):
            subprocess.run(["msiexec", "/i", self.installer, "/qn"], check=True)
        logging.info(f"'{self.name}' installation initiated successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Installation of '{self.name}' failed: {e}")
        raise Exception(f"Installation of '{self.name}' failed: {e}")
```

The `/S` and `/qn` flags are there to make the installation quiet.

## Final Details

The last method that was added to this class is a `clean` method, a short one for deleting the used installer.

```Python
def clean(self) -> None:
    logging.info(f"Cleaning {self.name} installer.")
    os.remove(self.installer)
```

And lastly, the `main` function had to be created, the one repsonisible for creating all `Program` instances, downloading, installing and cleaning them. Additionaly, this method also installs some modules that needed to be avialable system wide, this is done with the `install_module` function discussed earlier.

```Python
def main():
    programs = [
        # -+- Programs -+-
    ]

    for program in programs:
        program.download()
        program.install()
        program.clean()

    modules = [
        # -+- Modules -+-
    ]

    for module in modules:
        install_module(module)


if __name__ == "__main__":
    main()

```

And that's it.

### !!!!

A single day after running this script on **ALL** 40 computers, and even ensuring it ran properly and installed everything that needed to be installed,

A classmate took a computer - "Ariel, you forgot to install PyCharm on this one", and then another one - "Oh Ariel, there's no BlueJ here" and more and more.

Yes, someone forgot to tell me that Disk C clears itself **ENTIRELY** after a restart.

I guess I've learned a lot about PowerShell, and so have you.
