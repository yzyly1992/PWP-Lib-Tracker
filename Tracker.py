import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import datetime, re, time, os
from PIL import Image
import math
import json

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    paths = ["/mnt/jarvis/Library/PWP-LIBRARY/CUTOUTS/PLANTS/ALL PLANTS Collection/", "/mnt/jarvis/Library/PWP-LIBRARY/CUTOUTS/PEOPLE/PHOTO PEOPLE/"]
    observers = []
    event_handler = PatternMatchingEventHandler(patterns=["*.png"], ignore_patterns = "", ignore_directories=True, case_sensitive=True)
    publicPath = "/home/dyang/PWP-Lib-Search/build"
    buildPath = "/home/dyang/PWP-Lib-Search/public"

    def convert_size(size_bytes):
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s %s" % (s, size_name[i])

    def on_created(event):
        filePath = event.src_path
        folderName = filePath.splite("/")[5]
        
        if folderName == "PLANTS":
            if filePath[-3:] == "png":
                try:
                    im = Image.open(filePath)
                except IOError:
                    print("failed to identify", path)
                name = filePath.splite("/")[-1][:-4]
                if re.match(r'.*?tree.*?', name, flags=re.IGNORECASE):
                    category = "Tree"
                    name = name.replace('Tree', '')
                elif re.match(r'.*?shrub.*?', name, flags=re.IGNORECASE):
                    category = "Shrub"
                    name = name.replace('Shrub', '')
                elif re.match(r'.*?flower.*?', name, flags=re.IGNORECASE):
                    category = "Flower"
                    name = name.replace('Flower', '')
                elif re.match(r'.*?grass.*?', name, flags=re.IGNORECASE):
                    category = "Grass"
                    name = name.replace('Grass', '')
                elif re.match(r'.*?groundcover.*?', name, flags=re.IGNORECASE):
                    category = "Groundcover"
                    name = name.replace('Groundcover', '')
                elif re.match(r'.*?aquatic.*?', name, flags=re.IGNORECASE):
                    category = "Aquatic"
                    name = name.replace('Aquatic', '')
                elif re.match(r'.*?succulent.*?', name, flags=re.IGNORECASE):
                    category = "Succulent"
                    name = name.replace('Succulent', '')
                else:
                    category = "Other"

                with open('/home/dyang/PWP-Lib-Search/public/plants.json', 'r') as plantJson:
                    plantData = json.load(plantJson)

                thumbDir = "/Thumbnails/"
                idNum = plantData[-1]["id"] + 1
                imageSize = im.size
                name = name.replace('-', ' ').replace('_', ' ').replace('+', ' ')
                fullName = " ".join([i for i in name.split() if not i.isdigit()])
                dataType = "2D Cutout"
                fileSize = convert_size(os.path.getsize(filePath))
                createTime = time.ctime(os.path.getmtime(filePath))
                thumbName150 = fullName + " " + str(idNum) + " 150p.jpg"
                thumbName300 = fullName + " " + str(idNum) + " 300p.jpg"
                thumb150path = os.path.join(thumbDir, thumbName150)
                thumb300path = os.path.join(thumbDir, thumbName300)
                thumbName150Png = fullName + " " + str(idNum) + " 150p.png"
                thumbName300Png = fullName + " " + str(idNum) + " 300p.png"
                thumb150pathPng = os.path.join(thumbDir, thumbName150Png)
                thumb300pathPng = os.path.join(thumbDir, thumbName300Png)

                if im.mode == "RGBA":
                    bg = Image.new("RGB", im.size, (255, 255, 255))
                    bg.paste(im, mask=im)
                    im.save(os.path.join(publicPath, thumb300path))
                    im.save(os.path.join(buildPath, thumb300path))
                    bg.save(thumb300path)
                    im.save(os.path.join(publicPath, thumb150path))
                    im.save(os.path.join(buildPath, thumb150path))
                    bg.save(thumb150path)
                    return plantData.append({
                        "id": idNum,
                        "name": fullName,
                        "category": category,
                        "path": filePath, 
                        "dataType": dataType, 
                        "fileSize": fileSize,
                        "createTime": createTime,
                        "imageSize": imageSize,
                        "thumb150path": thumb150path,
                        "thumb300path": thumb300path})
                else:
                    im.thumbnail((300,300), Image.ANTIALIAS)
                    im.save(os.path.join(publicPath, thumb300pathPng), "PNG")
                    im.save(os.path.join(buildPath, thumb300pathPng), "PNG")
                    im.thumbnail((150,150),  Image.ANTIALIAS)
                    im.save(os.path.join(publicPath, thumb150pathPng), "PNG")
                    im.save(os.path.join(buildPath, thumb150pathPng), "PNG")
                    return plantData.append({
                        "id": idNum,
                        "name": fullName,
                        "category": category,
                        "path": filePath, 
                        "dataType": dataType, 
                        "fileSize": fileSize,
                        "createTime": createTime,
                        "imageSize": imageSize,
                        "thumb150path": thumb150pathPng,
                        "thumb300path": thumb300pathPng})
                
                print(plantData[-1])
                

    def on_deleted(event):
        filePath = event.src_path
        folderName = filePath.splite("/")[5]
        
        if folderName == "PLANTS":
            if filePath[-3:] == "png":
                with open('/home/dyang/PWP-Lib-Search/public/plants.json', 'r') as plantJson:
                    plantData = json.load(plantJson)
                for item in plantData:
                    if item["path"] == filePath:
                        os.remove(os.path.join(publicPath, item["thumb150path"]))
                        os.remove(os.path.join(publicPath, item["thumb300path"]))
                        os.remove(os.path.join(buildPath, item["thumb150path"]))
                        os.remove(os.path.join(buildPath, item["thumb300path"]))
                        plantData = plantData.remove(item)
                print(plantData[-1])



    event_handler.on_created = on_created
    event_handler.on_deleted = on_deleted

    observer = Observer()
    for path in paths:
        observer.schedule(event_handler, path, recursive=False)
        observers.append(observer)
    observer.start()

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        for observer in observers:
            observer.unschedule_all()
            observer.stop()

    for observer in observers:
        observer.join()