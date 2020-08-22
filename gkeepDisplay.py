import credential
import gkeepapi


keep = gkeepapi.Keep()
keep.login(credential.mail, credential.password)
gnote = keep.get(credential.noteUUID)


print(gnote.title)
print("------")


for item in gnote.items:
    notePrint = ""
    if(item.indented):
        notePrint += "\t"
    if(item.checked):
        notePrint += 'x '
    else:
        notePrint += 'o '
        
    if "http" in item.text:
        notePrint += "_website url_"
    
    else:        
        notePrint += item.text
    
    print(notePrint)


keep.sync()