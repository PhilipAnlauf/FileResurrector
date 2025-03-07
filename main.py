import os
import time
from string import ascii_uppercase

#The get drives method finds all drives within the computer
def GetDrives():
    drives = []
    for letter in ascii_uppercase:
        #"\\\\.\\" = r"\\.\", this is used for finding the drives and being able to access bit level data
        if os.path.exists("\\\\.\\" + letter + ":"):
            drives.append("\\\\.\\" + letter + ":")
    return drives

#Read sector data takes a drive and a sector and reads/saves data from the bit level of the sector in that drive
def ReadSectorData(drivePath, sector, sectorSize=512):
    try:
        #'rb' is for reading at bit level
        with open(drivePath, 'rb') as sectorFile:
            sectorFile.seek(sector * sectorSize)
            sectorFileData = sectorFile.read(sectorSize)
            #'02X' is for printing hex, space is added for readability
            dataString = ''.join(format(byte, '02X') + " " for byte in sectorFileData)
            return dataString
    except Exception as e:
        print("Could not open sector " + str(sector) + " of drive " + str(drivePath))
        print(e)

if __name__ == "__main__":
    computerDrives = GetDrives()

    hold = 0

    while True:
        readSectorData = ReadSectorData(computerDrives[0], hold)
        print(readSectorData)
        print()
        hold += 1
        time.sleep(0)

#TODO:
#1. Create method for grabbing key pieces of data, if file is existent 4E 54 46 53, title if possible, pointers to next
#   sector of file, etc.
#2. Create method for recording info of file if it is deleted