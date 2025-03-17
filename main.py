import os
import struct
import textwrap
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

if __name__ == "__main__":
    computerDrives = GetDrives()
    specialFolders = ["C:\\$Recycle.Bin"]

    print(ReadSectorData(computerDrives[0], 0))
    MFTOffset = getMFTOffset(computerDrives[0])

    ReadSectorData(computerDrives[0], MFTOffset)

#TODO:
#1. Fully analyze the boot sector to grab proper info on the filesystem, size, sectors quantity, cluster quantity, etc.
#2. Create method for grabbing key pieces of data, if file is existent 4E 54 46 53, title if possible, pointers to next
#   sector of file, etc.
#3. Create method for recording info of file if it is deleted