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
                        datefmt='%Y-%m-%d %H:%M:%S', filename='tracker.log')
    path = "/Users/davidyang/Downloads/TestTest"
    event_handler = PatternMatchingEventHandler(patterns="*.png", ignore_patterns = "", ignore_directories=True, case_sensitive=False)
    # buildPath = "/home/dyang/PWP-Lib-Search/build"
    publicPath = "/Users/davidyang/Documents/PWP-Lib-Search/public"

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
        # try:
        #     im = Image.open(filePath)
        # except IOError:
        #     print("failed to identify", path)
        
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

        with open('/Users/davidyang/Documents/PWP-Lib-Search/public/plants.json', 'r') as plantJson:
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
        # file2Path = filePath.replace("/mnt/jarvis/Library", "Y:").replace("/", "\\")
        file2Path = filePath

        if im.mode == "RGBA":
            bg = Image.new("RGB", im.size, (255, 255, 255))
            bg.paste(im, mask=im)
            bg.thumbnail((300,300))
            # im.save(os.path.join(publicPath, thumb300path[1:]))
            # im.save(os.path.join(buildPath, thumb300path))
            bg.save(os.path.join(publicPath, thumb300path[1:]))
            # im.save(os.path.join(publicPath, thumb150path[1:]))
            # im.save(os.path.join(buildPath, thumb150path))
            bg.thumbnail((150,150))
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
            # im.save(os.path.join(buildPath, thumb300pathPng), "PNG")
            im.thumbnail((150,150),  Image.ANTIALIAS)
            im.save(os.path.join(publicPath, thumb150pathPng[1:]), "PNG")
            # im.save(os.path.join(buildPath, thumb150pathPng), "PNG")
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

        with open('/Users/davidyang/Documents/PWP-Lib-Search/public/plants.json', 'w') as publicJson:
            json.dump(plantData, publicJson)
        # with open('/home/dyang/PWP-Lib-Search/build/plants.json', 'w') as buildJson:
        #     json.dump(plantData, buildJson)
        logging.info("add file success: " + filePath)
        # print(plantData[-1])

                

    def on_deleted(event):
        filePath = event.src_path

        with open('/Users/davidyang/Documents/PWP-Lib-Search/public/plants.json', 'r') as plantJson:
            plantData = json.load(plantJson)
            for item in plantData:
                # if item["path"] == filePath.replace("/mnt/jarvis/Library", "Y:").replace("/", "\\"):
                if item["path"] == filePath:
                    os.remove(os.path.join(publicPath, item["thumb150path"][1:]))
                    os.remove(os.path.join(publicPath, item["thumb300path"][1:]))
                    # os.remove(os.path.join(buildPath, item["thumb150path"]))
                    # os.remove(os.path.join(buildPath, item["thumb300path"]))
                    plantData.remove(item)

        with open('/Users/davidyang/Documents/PWP-Lib-Search/public/plants.json', 'w') as publicJson:
            json.dump(plantData, publicJson)
        # with open('/home/dyang/PWP-Lib-Search/build/plants.json', 'w') as buildJson:
        #     json.dump(plantData, buildJson)
        logging.info("delete file success: " + filePath)

    def on_moved(event):
        oldName = event.src_path
        newName = event.dest_path

        with open('/Users/davidyang/Documents/PWP-Lib-Search/public/plants.json', 'r') as plantJson:
            plantData = json.load(plantJson)
            for item in plantData:
                # if item["path"] == filePath.replace("/mnt/jarvis/Library", "Y:").replace("/", "\\"):
                if item["path"] == oldName:
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
                    item["path"] = newName

        with open('/Users/davidyang/Documents/PWP-Lib-Search/public/plants.json', 'w') as publicJson:
            json.dump(plantData, publicJson)
        logging.info("rename file success: " + newName)

    event_handler.on_created = on_created
    event_handler.on_deleted = on_deleted
    event_handler.on_moved = on_moved

    nWatch = Observer()
    targetPath = str(path)
    nWatch.schedule(event_handler, targetPath, recursive=False)

    nWatch.start()

    try:
        while True:
            time.sleep(1000)
    except KeyboardInterrupt:
        nWatch.stop()
    nWatch.join()