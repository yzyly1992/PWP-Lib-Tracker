import sys
import time
import logging
from watchdog.observers.polling import PollingObserver
from watchdog.events import PatternMatchingEventHandler
import datetime, re, time, os
from PIL import Image
import math
import json

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = "/mnt/jarvis/Library/PWP-LIBRARY/CUTOUTS/PLANTS/ALL PLANTS MASTER"
    event_handler = PatternMatchingEventHandler(patterns="*.png", ignore_patterns = "", ignore_directories=True, case_sensitive=False)
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
        im = Image.open(filePath)
        
        name = filePath.split("/")[-1][:-4]
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
        mac = filePath.replace("/mnt/jarvis", "/Volumes")
        file2Path = filePath.replace("/mnt/jarvis/Library", "Y:").replace("/", "\\")

        if im.mode == "RGBA":
            bg = Image.new("RGB", im.size, (255, 255, 255))
            bg.paste(im, mask=im)
            bg.thumbnail((300,300))
            bg.save(os.path.join(buildPath, thumb300path[1:]))
            bg.save(os.path.join(publicPath, thumb300path[1:]))
            bg.thumbnail((150,150))
            bg.save(os.path.join(buildPath, thumb150path[1:]))
            bg.save(os.path.join(publicPath, thumb150path[1:]))
            plantData.append({
                "id": idNum,
                "name": fullName,
                "category": category,
                "path": file2Path, 
                "dataType": dataType, 
                "fileSize": fileSize,
                "createTime": createTime,
                "imageSize": imageSize,
                "thumb150path": thumb150path,
                "thumb300path": thumb300path,
                "mac": mac})
        else:
            im.thumbnail((300,300), Image.ANTIALIAS)
            im.save(os.path.join(publicPath, thumb300pathPng[1:]), "PNG")
            im.save(os.path.join(buildPath, thumb300pathPng[1:]), "PNG")
            im.thumbnail((150,150),  Image.ANTIALIAS)
            im.save(os.path.join(publicPath, thumb150pathPng[1:]), "PNG")
            im.save(os.path.join(buildPath, thumb150pathPng[1:]), "PNG")
            plantData.append({
                "id": idNum,
                "name": fullName,
                "category": category,
                "path": file2Path, 
                "dataType": dataType, 
                "fileSize": fileSize,
                "createTime": createTime,
                "imageSize": imageSize,
                "thumb150path": thumb150pathPng,
                "thumb300path": thumb300pathPng,
                "mac": mac})

        with open('/home/dyang/PWP-Lib-Search/public/plants.json', 'w') as publicJson:
            json.dump(plantData, publicJson)
        with open('/home/dyang/PWP-Lib-Search/build/plants.json', 'w') as buildJson:
            json.dump(plantData, buildJson)
        print("add file success")

                

    def on_deleted(event):
        filePath = event.src_path

        with open('/home/dyang/PWP-Lib-Search/build/plants.json', 'r') as plantJson:
            plantData = json.load(plantJson)
            for item in plantData:
                if item["path"] == filePath.replace("/mnt/jarvis/Library", "Y:").replace("/", "\\"):
                    os.remove(os.path.join(publicPath, item["thumb150path"][1:]))
                    os.remove(os.path.join(publicPath, item["thumb300path"][1:]))
                    os.remove(os.path.join(buildPath, item["thumb150path"][1:]))
                    os.remove(os.path.join(buildPath, item["thumb300path"][1:]))
                    plantData.remove(item)
                    with open('/home/dyang/PWP-Lib-Search/public/plants.json', 'w') as publicJson:
                        json.dump(plantData, publicJson)
                    with open('/home/dyang/PWP-Lib-Search/build/plants.json', 'w') as buildJson:
                        json.dump(plantData, buildJson)
        print("delete file success")

    def on_moved(event):
        oldName = event.src_path
        newName = event.dest_path

        with open('/home/dyang/PWP-Lib-Search/build/plants.json', 'r') as plantJson:
            plantData = json.load(plantJson)
            for item in plantData:
                if item["path"] == oldName.replace("/mnt/jarvis/Library", "Y:").replace("/", "\\"):
                    name = newName.split("/")[-1][:-4]
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

                    name = name.replace('-', ' ').replace('_', ' ').replace('+', ' ')
                    item["name"] = " ".join([i for i in name.split() if not i.isdigit()])
                    item["mac"] = newName.replace("/mnt/jarvis", "/Volumes")
                    item["category"] = category
                    item["path"] = newName.replace("/mnt/jarvis/Library", "Y:").replace("/", "\\")

        with open('/home/dyang/PWP-Lib-Search/public/plants.json', 'w') as publicJson:
            json.dump(plantData, publicJson)
        with open('/home/dyang/PWP-Lib-Search/build/plants.json', 'w') as buildJson:
            json.dump(plantData, buildJson)
        print("rename file success")

    event_handler.on_created = on_created
    event_handler.on_deleted = on_deleted
    event_handler.on_moved = on_moved

    nWatch = PollingObserver(timeout=60)
    targetPath = str(path)
    nWatch.schedule(event_handler, targetPath, recursive=False)

    nWatch.start()

    try:
        while True:
            time.sleep(1000)
    except KeyboardInterrupt:
        nWatch.stop()
    nWatch.join()
