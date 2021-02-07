### About

A small Python script that helps to properly organize your photos/media backups. "Properly" means - by using EXIF metadata. It is used to copy and sort "RAW"/"original" copies of photos from a media devices (e.g. mobile phones, cameras) into a destination folder. The "year->month" structure is used to sort files.

### Dependencies

```
pip install -r requirements.txt
```

### Usage

* Getting help
```
python pyphotosorganizer.py --help
```
* Process photos in source directory
```
python pyphotosorganizer.py --source i:\Photos\from-iPhone\ --dest F:\iphone\ --mode PROCESS
```
* Check whether all photos/videos were copied
```
python pyphotosorganizer.py --source i:\Photos\from-iPhone\ --dest F:\iphone\ --mode CHECK
```
* Or check provided "bat" files
