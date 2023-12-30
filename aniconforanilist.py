from PIL import Image, ImageOps
import requests
import os
import json
import aniparse

def alsearch(name: str):
    url="https://graphql.anilist.co"
    query = '''
            query($name:String)      {
                Page{
                    media(search:$name,format_not_in:[MANGA,ONE_SHOT,NOVEL,MUSIC]) {
                        id
                        type
                        title {
                            romaji
                            english
                        }
                        coverImage {
                            extraLarge
                        }
                    }
                }
            }
        '''
    variables = {
        'name':name
    }
    print(name)
    results = requests.post(url,json={'query':query,'variables':variables})
    jsonobj = json.loads(results.content)
    return(jsonobj)

def getartwork(name: str) -> tuple:
    jsonobj = alsearch(name)
    if automode:
        return(jsonobj['data']['Page']['media'][0]['coverImage']['extraLarge'],jsonobj['data']['Page']['media'][0]['type'])
    else:  
        if len(jsonobj['data']['Page']['media']) == 0:
            print('No results found.')
            custom = True if input('Try with custom name? Y/N : ').upper() == 'Y' else False
            if custom:
                custom = input('Enter custom name : ')
                jsonobj = alsearch(custom)
            else:
                return(None,None)
        counter = 1  
        for id in jsonobj['data']['Page']['media']:
            print(str(counter)+' - '+id['title']['romaji'])
            counter = counter + 1
        ch = input('\n>')
        if ch == '':
            ch = 1
        return(jsonobj['data']['Page']['media'][int(ch)-1]['coverImage']['extraLarge'] , jsonobj['data']['Page']['media'][int(ch)-1]['type'])
 

def createicon(folder: str, link: str):
    art = requests.get(link)
    open(jpgfile, 'wb').write(art.content)

    img = Image.open(jpgfile)
    img = ImageOps.expand(img, (69, 0, 69, 0), fill=0)
    img = ImageOps.fit(img, (500,500)).convert("RGBA")
    
    datas = img.getdata()
    newData = []
    for item in datas:
        if item[0] == 0 and item[1] == 0 and item[2] == 0:
            newData.append((0, 0, 0, 0))
        else:
            newData.append(item)

    img.putdata(newData)
    os.remove(jpgfile)
    img.save(icofile)
    img.close()
    return(icofile)

if __name__ == '__main__':
    print('''Run this in your anime folder
    For help and info, check out
    https://github.com/EnArvy/anicon
    ''')

    folderlist = next(os.walk('.'))[1]

    if folderlist is None or len(folderlist) == 0:
        # In case the file is placed inside an inner most directory which contains only files and no other folders, this list will be empty.
        # Thus adding the current directory path as an element of the list.
        folderlist = [str(os.getcwd())]
    automode = True if input('Use AutoMode? Y/N : ').upper() == 'Y' else False

    for folder in folderlist:
        parsed = aniparse.parse(folder,options={'allowed_delimiters':' .+','season_part_as_unique':True})
        name = parsed['anime_title']
        if 'anime_season' in parsed:
            name+=' '+str(parsed['anime_season'])

        # Extracting the name of the folder without the path and then performing search for the same. This will be the name of the anime
        # episode, thus instead of performing a search for the directory path, now performing a search for the directory name.

        iconname = name.replace(' ', '_')
        jpgfile = folder + '\\' + iconname + '.jpg'
        icofile = folder + '\\' + iconname + '.ico'
        
        if os.path.isfile(icofile):
            print('An icon is already present. Delete the older icon and `desktop.ini` file before applying a new icon')
            continue
        try:
            link, Type = getartwork(name)
            icon = createicon(folder, link)
        except:
            print('Ran into an error. Try manual mode with custom input.')
            continue

        f = open(folder + "\\desktop.ini","w+")
        f.write("[.ShellClassInfo]\nConfirmFileOp=0\n")
        f.write(f"IconResource={os.getcwd()}\\{folder}\\{iconname}.ico,0")
        f.write(f"\nIconFile={iconname}.ico\nIconIndex=0")
        f.write("\n[ViewState]\nMode=\nVid=\nFolderType=Videos")
        
        if Type is not None and len(Type) > 0:
            # If the result has a type, then using this as the infotip for the desktop icon.
            f.write(f"\nInfoTip={Type}")
        f.close()

        # Marking icon and `desktop.ini` file as a system file.
        # Marking folder as read only and system as this is needed to show icons
        os.system(f'attrib +r +s \"{os.getcwd()}\\{folder}\"')
        os.system(f'attrib +h +s \"{os.getcwd()}\\{folder}\\desktop.ini\"')
        os.system(f'attrib +h +s \"{os.getcwd()}\\{icon}\"')

