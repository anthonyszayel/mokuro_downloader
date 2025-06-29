import requests, os, threading
from bs4 import BeautifulSoup       #html parser
from time import sleep              #for thread creation control
from urllib.parse import urljoin
from copy import deepcopy

def write_file(filePath, fileLink):
    try:
        imageRequest = requests.get(fileLink, timeout=10)
        imageRequest.raise_for_status()

        with open(filePath, "wb") as fp:   
            fp.write(imageRequest.content)

    except Exception:
        print(f"An unexpected error occurred: {Exception}")
    
def writer_thread_starter(filePath, fileLink, threadList, cores):

    threadList[:] = [thread for thread in threadList if thread.is_alive()] #removes threads that have already finished their tasks

    while len(threadList) >= cores: #only allow as many threads as there are cores available to run at once
        sleep(0.1)
        threadList[:] = [thread for thread in threadList if thread.is_alive()] #update threadList to see when we can create a new one
    
    thread = threading.Thread(target=write_file, args=(filePath, fileLink))
    thread.start()
    threadList.append(thread)

def remove_extension(fileUrl):
    counter=0
    for character in fileUrl[::-1]:
        if character!=".":
            counter+=1
        else:
            counter+=1
            break
    
    cutoff = len(fileUrl)-counter
    withoutExtension = fileUrl[:cutoff:]

    return withoutExtension

def remove_slash(anyName): #for removing the final slash from folder directories (to use it as a name rather than a directory, for example)
    cutoff = len(anyName)-1
    withoutSlash = anyName[:cutoff:]

    return withoutSlash

def get_extension(fileUrl):
    fileExtension = ""
    for character in fileUrl[::-1]:
        if character!=".":
            fileExtension += character #this will get us the reversed file extension
        else:
            fileExtension += character
            fileExtension = fileExtension[::-1] #this will make it right
            return fileExtension

def get_manga_name(anyName):
    withoutSlash = remove_slash(anyName)

    decimal = [str(i) for i in range(0,10)]
    
    counter = 0
    for letter in withoutSlash[::-1]:
        if letter in decimal or letter==" ": #this gets the name of the manga by deleting the volume number from
                                             #the name of the folder. the result is going to be used as a folder
                                             #name, so it can't have whitespaces as the last character.
            counter+=1
        else:
            cutoff = len(withoutSlash)-counter
            finalName = withoutSlash[:cutoff:]
            break

    return finalName

def menu(nameLinkDictList):

    for idx, pair in enumerate(nameLinkDictList):
        if pair["link"][-6:] == "mokuro": #examining the file extension
            break                         #if the extension is .mokuro, I don't wanna show it (it is automatically
                                          #downloaded with the volume)
        print(f"{idx:4} - {pair["name"]}")
    
    index = int(input("### PLEASE CHOOSE A DIRECTORY (-1 TO EXIT THE PROGRAM) ###\n"))

    if index != -1:
        while index>=len(nameLinkDictList):
            print("ERROR: UNKNOWN INDEX.")
            index = int(input("PLEASE CHOOSE A VALID DIRECTORY: "))
    
    return index

def volume_menu():
    options = [
        "1 - Download full volume",
        "2 - Start downloading from a specific page",
        "3 - Download specific pages",
        "0 - Go back"
    ]

    print("### PLEASE CHOOSE AN OPTION ###\n")

    for option in options:
        print(option)
    
    chosen = int(input())
    while chosen<0 or chosen>len(options)-1:
        print("ERROR: UNKNOWN OPTION.")
        chosen = int(input("PLEASE CHOOSE A VALID OPTION: "))

    return chosen

def download(mangaName, volumeName, dirLink, fileList):
    rootDir = os.path.dirname(os.path.abspath(__file__)) #this program downloads to the .py file's folder

####### CREATING THE MANGA FOLDER #######
    mangaFolderPath = os.path.join(rootDir, mangaName)
    if not os.path.exists(mangaFolderPath):
        os.makedirs(mangaFolderPath)

####### CREATING THE VOLUME FOLDER WITHIN THE MANGA FOLDER PREVIOUSLY CREATED #######
    volumeFolderPath = os.path.join(mangaFolderPath, volumeName)
    if not os.path.exists(volumeFolderPath):
        os.makedirs(volumeFolderPath)
    
    cores = os.process_cpu_count()

    threads = []

####### DOWNLOADING THE IMAGE FILES #######
    for file in fileList:
        if file["name"] == "../":
            continue

        fileLink = urljoin(dirLink, file["link"])
        fileExtension = get_extension(fileLink)
        fileName = remove_extension(file["name"])
        filePath = os.path.join(volumeFolderPath, fileName+fileExtension) #this sequence of removing the extension and then adding it again
                                                                          #might seem confusing, but it is actually necessary. the extension
                                                                          #from the original file["name"] is not recognized as a file
                                                                          #extension, but rather as just a part of the name. if that isn't
                                                                          #done, we'll end up with files like "00001.webp.webp" when attaching
                                                                          #the actual file extension.
        if not os.path.isfile(filePath):
            writer_thread_starter(filePath, fileLink, threads, cores)
        else:
            continue

    for thread in threads:
        thread.join()     #wait for all threads to finish before moving on

def download_mokuro_file(previousDirLink, previousNameLinkPairs, mangaName, volumeInfo): #see download() for explanations. same logic.
    rootDir = os.path.dirname(os.path.abspath(__file__))
    mangaFolderPath = os.path.join(rootDir, mangaName) #will always already exist. download() is executed before this and creates it.
    volumeLink = remove_slash(volumeInfo["link"])
    volumeName = remove_slash(volumeInfo["name"])

    extension = ".mokuro"
    file = volumeLink + extension       #need to use volumeLink instead of volumeName here because of japanese characters.
    fileName = volumeName + extension

    filePath = os.path.join(mangaFolderPath, fileName)

    for pair in previousNameLinkPairs:
        if pair["link"] == file:
            if not os.path.isfile(filePath):
                fileLink = os.path.join(previousDirLink, file)
                write_file(filePath, fileLink)
            break

indexLink = "https://mokuro.moe/manga/"
currentDirLink = indexLink
previousDirLink = currentDirLink

listIndex = 1
previousNameLinkPairs = []  #we're going to use this to get the names of the manga and the volume

while listIndex != -1:

    r = requests.get(currentDirLink, timeout=10)
    r.raise_for_status()

    currentPage = BeautifulSoup(r.content, 'html.parser')

######## Extracting all names and links from the html document #########

    extractedAElements = currentPage.find_all('a')

    nameLinkPairs = []
    isItAVolumeFolder = 1

    for idx, element in enumerate(extractedAElements):
        link = element.get('href')

        nameLinkPairs.append(
            {
                "name": element.contents[0], #gets the name without the surrounding tags
                "link": link
            }
        )

        if link[-1] == "/" and idx != 0: #idx=0 will always be "../". volume folders don't have directories,
                                        #only images. since directories always end with a /, if there are no
                                        #links ending with a / other than "../", it is a volume folder.
            isItAVolumeFolder = 0

    if isItAVolumeFolder:   #it is impossible for this to be executed in the first folder. jump to the "else" part first to better understand the flow of the program.
        alternative = volume_menu()
        volumeInfo = previousNameLinkPairs[listIndex]
        volumeName = remove_slash(volumeInfo["name"])
        mangaName = get_manga_name(volumeInfo["name"])

        match alternative:
            case 1: #download full
                download(mangaName, volumeName, currentDirLink, nameLinkPairs)
                download_mokuro_file(previousDirLink, previousNameLinkPairs, mangaName, volumeInfo)

            case 2: #download starting from a specific page
                start = int(input("Starting page: "))
                while start<0 or start>=len(nameLinkPairs):
                    print("Invalid page number.")
                    start = int(input("Please enter a valid page value: "))
                nameLinkPairs = nameLinkPairs[start::]
                download(mangaName, volumeName, currentDirLink, nameLinkPairs)
                download_mokuro_file(previousDirLink, previousNameLinkPairs, mangaName, volumeInfo)

            case 3: #download only certain specific pages
                pages = []
                temp = 0
                while temp!=-1:
                    temp = int(input("Please enter a page number (-1 to stop): "))
                    if temp==-1:
                        break
                    elif temp<=0 or temp>=len(nameLinkPairs):
                        print("Page number out of range.")
                    else:
                        pages.append(temp)
                nameLinkPairs[:] = [nameLinkPairs[i] for i in pages]
                download(mangaName, volumeName, currentDirLink, nameLinkPairs)
                download_mokuro_file(previousDirLink, previousNameLinkPairs, mangaName, volumeInfo)

        currentDirLink = previousDirLink
        previousDirLink += "../"
            
    else:
        listIndex = menu(nameLinkPairs)
        previousNameLinkPairs = []

        previousNameLinkPairs = deepcopy(nameLinkPairs)  #we will use this to get the manga name for creating
                                                         #the manga folder on the user pc and to download the .mokuro file
        previousDirLink = currentDirLink
        currentDirLink += nameLinkPairs[listIndex]["link"] #also works if you want to go back, since
                                                           #currentDir + "../" == previousDir