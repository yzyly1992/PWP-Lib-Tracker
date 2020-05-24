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
    paths = ["/mnt/jarvis/Library/PWP-LIBRARY/CUTOUTS/PLANTS/ALL PLANTS Collection", "/mnt/jarvis/Library/PWP-LIBRARY/CUTOUTS/PEOPLE/PHOTO PEOPLE"]
    event_handler = PatternMatchingEventHandler(patterns=["*.png"], ignore_patterns = None, ignore_directories=True, case_sensitive=False)
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
        print(folderName)

        if folderName == "PLANTS":
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
            mac = filePath.replace("/mnt/jarvis", "/Volumes")
            filePath = filePath.replace("/mnt/jarvis/Library", "Y:").replace("/", "\\")

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
                    "thumb300path": thumb300path,
                    "mac": mac})
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
                    "thumb300path": thumb300pathPng,
                    "mac": mac})
                
            print(plantData[-1])

            with open('/home/dyang/PWP-Lib-Search/public/plants.json', 'w') as publicJson:
                json.dump(plantData, publicJson)
            with open('/home/dyang/PWP-Lib-Search/build/plants.json', 'w') as buildJson:
                json.dump(plantData, buildJson)

                

    def on_deleted(event):
        filePath = event.src_path
        folderName = filePath.splite("/")[5]
        print(filePath)

        if folderName == "PLANTS":
            with open('/home/dyang/PWP-Lib-Search/public/plants.json', 'r') as plantJson:
                plantData = json.load(plantJson)
            for item in plantData:
                if item["path"] == filePath.replace("/mnt/jarvis/Library", "Y:").replace("/", "\\"):
                    os.remove(os.path.join(publicPath, item["thumb150path"]))
                    os.remove(os.path.join(publicPath, item["thumb300path"]))
                    os.remove(os.path.join(buildPath, item["thumb150path"]))
                    os.remove(os.path.join(buildPath, item["thumb300path"]))
                    plantData = plantData.remove(item)
            
            print(plantData[-1])
            with open('/home/dyang/PWP-Lib-Search/public/plants.json', 'w') as publicJson:
                json.dump(plantData, publicJson)
            with open('/home/dyang/PWP-Lib-Search/build/plants.json', 'w') as buildJson:
                json.dump(plantData, buildJson)



    event_handler.on_created = on_created
    event_handler.on_deleted = on_deleted
    threads = []

    nWatch = Observer()
    for path in paths:
        targetPath = str(path)
        nWatch.schedule(event_handler, targetPath, recursive=False)
        threads.append(nWatch)

    nWatch.start()

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        for o in observers:
            nWatch.stop()
    nWatch.join()
