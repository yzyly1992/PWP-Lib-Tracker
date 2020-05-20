with open("./test.skp", "encoding="ascii", errors='ignore'") as f:
    skpContent = f.read()

with open("./skpDecoded.txt", "w") as p:
    p.write(skpContent)
    p.close()