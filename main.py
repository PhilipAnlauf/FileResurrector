import os
import struct
import textwrap
import time
import threading
from string import ascii_uppercase

from PIL.ImageChops import offset


#The get drives method finds all drives within the computer
def GetDrives():
    drives = []
    for letter in ascii_uppercase:
        #"\\\\.\\" = r"\\.\", this is used for finding the drives and being able to access bit level data
        if os.path.exists("\\\\.\\" + letter + ":"):
            drives.append("\\\\.\\" + letter + ":")
    return drives

#Read sector data takes a drive and a sector and reads/saves data from the bit level of the sector in that drive
def ReadSectorData(drivePath,offset, sectorSize=512):
    with open(drivePath, "rb") as drive:
        drive.seek(offset)
        sectorData = drive.read(sectorSize)
        rawHex = sectorData.hex()
        formattedHex = ' '.join(textwrap.wrap(rawHex, 2))
        #lines = textwrap.wrap(formattedHex, 48)

        #for line in lines:
        #    print(line)
        return formattedHex

#The get MFT offset takes a drive in and looks at the boot sector to and sees what offset the MFT table is at
def getMFTOffset(drive):
    with open(drive, 'rb') as sectorFile:
        bootSectorData = sectorFile.read(512)
        MFTStartCluster = struct.unpack('<Q', bootSectorData[0x30:0x38])[0]
        offset = MFTStartCluster * 4096
        return offset

#The get boot sector details analyzes the boot sector and returns certain info about the system to be used later
def getBootSectorDetails(drive):
    with open(drive, 'rb') as sectorFile:
        bootSectorData = sectorFile.read(512)
        bytesPerSectorOut = struct.unpack('<H', bootSectorData[0x0B:0x0D])[0]
        sectorsPerClusterOut = struct.unpack('<B', bootSectorData[0x0D:0x0E])[0]
        MFTSectorSizeOut = sectorsPerClusterOut * bytesPerSectorOut
        MFTOffsetOut = getMFTOffset(drive)
        totalSectorsOut = struct.unpack('<Q', bootSectorData[0x28:0x30])[0]
        totalClustersOut = totalSectorsOut/8
        return bytesPerSectorOut, sectorsPerClusterOut, totalSectorsOut, totalClustersOut, MFTSectorSizeOut, MFTOffsetOut

def getFileName(sectorDataIN):
    try:
        fileNameLength = int.from_bytes(struct.unpack('<I', sectorDataIN[168:172]), 'little')
        rawFileName = sectorDataIN[176 + 0x42:176 + fileNameLength]
        name = rawFileName.decode('utf-16-le', errors='replace')

        return name
    except:
        return ""

#The dissect MFT sector will take a drive and given offset and return given details about the MFT sector
def dissectMFTSector(drivePath, offsetIN):
    name = ""
    isDeleted = False

    with open(drivePath, 'rb') as drive:
        drive.seek(offsetIN)
        sectorData = drive.read(1024)

        if sectorData[0:4] != b'FILE':
            return

        name = getFileName(sectorData)

        isDeleted = int.from_bytes(struct.unpack('<B', sectorData[0x16:0x17]), 'little') == 0

        if(name!='' and name!='.'):
            if(isDeleted):
                print("Name: " + name + ", DELETED")
            #else:
                #print("Name: " + name + ", NOT DELETED")

if __name__ == "__main__":
    computerDrives = GetDrives()
    specialFolders = ["C:\\$Recycle.Bin"]

    #Get the details of the boot sector for possible later use
    bytesPerSector, sectorsPerCluster, totalSectors, totalClusters, MFTSectorSize, MFTOffset = getBootSectorDetails(computerDrives[0])

    #Program start output
    print("Drive details:\nBytes per sector: %d\nSectors per cluster: %d\nTotal sectors: %d\nTotal clusters: %d\nMFT Offset: %d"
          % (bytesPerSector, sectorsPerCluster, totalSectors,totalClusters,MFTOffset))
    print("Starting in 3 seconds...")
    time.sleep(3)


    import sys
    print("MFT Offset: " + str(MFTOffset) + ", Size: " + str(totalSectors*512))
    for offset in range(MFTOffset, totalSectors*bytesPerSector, 1024):
        sys.stdout.write(f"\rOffset: {offset} " + str((offset/(totalSectors*512))*100) + "% ")  # Overwrite the line
        sys.stdout.flush()  # Force immediate output
        dissectMFTSector(computerDrives[0], offset)

#TODO
#1. Optimize search pattern to speed up physical searching