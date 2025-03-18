import os
import struct
import textwrap
import time
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

#The dissect MFT sector will take a drive and given offset and return given details about the MFT sector
def dissectMFTSector(drivePath, offsetIN):
    with open(drivePath, 'rb') as drive:
        drive.seek(offsetIN)
        sectorData = drive.read(512)

        if sectorData[0:4] != b'FILE':
            return

        nameLength = struct.unpack('<B', sectorData[240:241])[0]
        fileNameSpace = struct.unpack('<B', sectorData[241:242])[0]
        rawName = struct.unpack(f'<{nameLength}s', sectorData[242:242 + nameLength])[0]
        name = rawName.decode('utf-16', errors='ignore')
        #print("Name Length: " + str(nameLength) + " Name: " + name)
        if(name!=''):
            print(name)

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

    #print(ReadSectorData(computerDrives[0], 0))
    #dissectMFTSector(computerDrives[0], offset=MFTSectorSize)

    for offset in range(MFTOffset, totalSectors*bytesPerSector, bytesPerSector):
        #print(ReadSectorData(computerDrives[0], offset))
        dissectMFTSector(computerDrives[0], offset)

#TODO
#1. Further complete the MFT sector Dissect to get file name