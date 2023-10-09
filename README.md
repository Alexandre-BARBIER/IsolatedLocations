# Find isolated properties in France

## Goal of this project

Using cadastre databases' data, find all habitations that are further than 300 meters from their closest neightbor.
Only keep locations that are less than a certain T driving time away from a point V.

## How to run

Clone the repository and open a terminal in the folder

Run the following commands


```console
python3 -m venv venv
source venv/bin/activate   
pip install -r requirements.txt
```

If you have a HERE API key with access to Isoline routing
- Add the key on line 15 of `PrototypeLoiret.py`

If you do not have a HERE API key
- Change the value of USE_HERE to False on line 20 of `PrototypeLoiret.py`
- This will disable the driving time test, but this is the only solution with no API key.

Run the following command

```console
python3 PrototypeLoiret.py
```

## Create an executable

On windows with PyInstaller:

```console
pyinstaller -F --hidden-import="sklearn.utils._typedefs" --hidden-import="sklearn.neighbors._partition_nodes" --onefile PrototypeLoiret.py
```