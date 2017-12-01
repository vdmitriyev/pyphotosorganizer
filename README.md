### About

A small Python script that helps to organize your photos/media backups properly. In this case "properly" means using EXIF metadata to copy and sort "RAW" copies of photos from a media devices like mobile phones into destination folder with "year-month" structure.

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
