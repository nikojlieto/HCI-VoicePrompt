"""
Author: Nikolai Lieto
Class: CS 474
Assignment: Voice Prompts
Date: 2/8/24
An adventure game played entirely with voice prompts.
"""

import speech_recognition as sr
import pyttsx3
import sys
import time
tts = pyttsx3.init() # pass 'dummy' to this constructor if this call fails due to a lack of voice drivers (but will disable speech)


#nested dictionary of rooms and info
rooms = {
    "greenRoom":{"desc":'this is a greenRoom, full of plants. the exit is to the East.',
                  'puzDesc':'a plant in the middle is sad and wilted',
                  'puzSolved':False,
                  'item':["plant"],
                  'East':'foyer'},
    "foyer":{'desc':'you are in a foyer. a painting is on the East wall. exits stand to the North, West, and South.',
             'puzDesc':'a toad is blocking the North exit',
             'puzSolved':False,
             'item':["painting", "toad"],
             'West':'greenRoom',
             'South':'kitchen'},
    "kitchen":{'desc':'it is a kitchen. a fridge sits on the West side. Exits are to the north and south.',
               'puzDesc':'',
               'puzSolved':True,
               'item':['water', 'yoghurt', 'fridge'],
               'North':'foyer',
               'South':'bedroom'},
    "bedroom":{'desc':'a sparsely decorated bedroom. a bed sits in the SouthWest corner. doors lead to the North and East.',
               'puzDesc':'the wooden door to the East is locked.',
               'puzSolved': False,
               'item':['crowbar', 'bed'],
               'North':'kitchen'},
    "rat room" :{'desc':'a large and comfortable room that a rat lives in. the rat is looking at you.',
                 'puzDesc':'the rat looks hungry.',
                 'puzSolved':False,
                 'item':['rat'],
                 'West':'bedroom'}
}

#item descriptions for look command
itemDesc = {
    "yoghurt": "delicious yoghurt. rats love to eat it.",
    "bed": "a plain wooden bed. oh! a crowbar's underneath!",
    "crowbar": "a metal crowbar that can be used for prying.",
    "plant": "a wilted and dried out plant. how sad.",
    "wooden key": "a wooden key for a wooden door.",
    "painting": "a oil painting with thick strokes. it seems a little loose.",
    "toad": "it is a mafia toad. it wants a bribe.",
    "money": "australian currency. perfect for bribing.",
    "door key": "the key to the exit! almost there.",
    "fridge": "there is water and yoghurt in the fridge.",
    'rat': 'a spotted domestic rat. he can jump through a hoop.'

}

#progress variables
#change to true when puzzles are solved
progress = {
    'plantWatered' : False,
    'ratUnlocked' : False,
    'ratFed' : False,
    'paintingpried' : False,
    'toadBribed' : False,
    'exitFound' : False,
    'winCon' : False

}

#assorted game variables referenced by methods
inventory = ["crowbar"]
currentroom = "bedroom"
moveerr = "you can't go there."
useerr = "you can't do that."

#speak and listen have been copied directly, with print statements removed.
def speak(tts, text):
    tts.say(text)
    tts.runAndWait()

def listen():
    listener = sr.Recognizer()                                                                                   
    with sr.Microphone() as source:
        listener.adjust_for_ambient_noise(source)
        
        time.sleep(1) # used to prevent hearing any spoken text; what else could we do?
        user_input = None
        sys.stdout.write(">")
        #record audio
        listener.pause_threshold = 0.5 # how long, in seconds, to observe silence before processing what was heard
        audio = listener.listen(source, timeout=3) #, timeout = N throws an OSError after N seconds if nothing is heard.  can also call listen_in_background(source, callback) and specify a function callback that accepts the recognizer and the audio when data is heard via a thread
        try:
            #convert audio to text
            #user_input = listener.recognize_sphinx(audio) #requires PocketSphinx installatidison
            user_input = listener.recognize_google(audio, show_all = False) # set show_all to True to get a dictionary of all possible translations
    
            #print(user_input)
            speak(tts, user_input)
        except sr.UnknownValueError:
            speak(tts, "sorry, i couldn't understand that.")
           # print("Could not understand audio")
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))
        except OSError:
            speak("i didn't hear anything.")
            #print("No speech detected")
        return user_input

#loop while not winning
def playGame():
    #the game should start with a description of your room
    doAction("look")
    while not progress['winCon']:
        speak(tts, "Proceed.")
        #receive dialogue
        d = listen()
        cont = check(d)
        if cont:
            doAction(d)


#took out the check function because of how long it made things last
def check(entry):
    return True
    """speak(tts, "i heard")
    speak(tts, entry)
    n = listen()
    if n == "no":
        return False
    else:
        return True"""

#cases for all accepted dialogue
def doAction(dialogue):
    global currentroom
    match dialogue:
        case "look":
            printRoom()

        case "examine":
            speak(tts, "examine what")
            d = listen()
            items = inventory + rooms[currentroom]['item']
            #if item in inventory or room is listed
            if d in items:
                #print item description
                speak(tts, itemDesc[d])

        case "take":
            speak(tts, "take what?")
            x = listen()
            #if item is in room and unlocked
            if x in rooms[currentroom]['item']:
                speak(tts, "you took the")
                speak(tts, rooms[currentroom]['item'])
                rooms[currentroom]['item'].remove(x)
                inventory.append(x)
                

        case "use":
            speak(tts, "use what?")
            it = listen()
            itright = False
            while not itright:
                speak(tts, it)
                speak("is that right?")
                ans = listen()
                if ans == "yes":
                    itright = True
                else:
                    it = listen()
            #if item is in inventory proceed
            if it in inventory:
                speak(tts, "on what?")
                ob = listen()
                obright = False
                while not obright:
                    speak(tts, "use")
                    speak(tts, it)
                    speak(tts, "on")
                    speak(tts, ob)
                    speak(tts, "is that right?")
                    ans = listen()
                    if ans == "yes":
                        checkPuz(it, ob)
                    else:
                        speak("on what, then?")
                        ob = listen()   
            else:
                speak(tts, "you don't have that.")
            #if puzzle solution is correct then do something lol

        case "inventory":
            speak(tts, inventory)
        
        case "North":
            #moveroom(dialogue, currentroom)
            currentroom = rooms[currentroom][dialogue]
            printRoom()
        
        case "South":
            #moveroom(dialogue, currentroom)
            currentroom = rooms[currentroom][dialogue]
            printRoom()

        case "West":
            #moveroom(dialogue, currentroom)
            currentroom = rooms[currentroom][dialogue]
            printRoom()

        case "East":
            #moveroom(dialogue, currentroom)
            currentroom = rooms[currentroom][dialogue]
            printRoom()

        case "help":
            help()

        case _:
            speak(tts, "that's not an accepted command.")

#introduce which prompts tutorial
def introduce():
    speak(tts, "Welcome to the game.")
    speak(tts, "Say 'Skip' to skip the tutorial.")
    speak(tts, "Say anything else to hear it.")
    #receive input here
    w = listen()
    if w != ("skip"):
        speak(tts, "okay, introduction.")
        help()
    else:
        speak(tts, "okay, skipping.")

#repeatable tutorial. just a lot of talking.
def help():
    speak(tts, "how to play.")
    speak(tts, "say a command to progress the game.")
    speak(tts, "acceptable commands include:")
    speak(tts, "look to hear a description of a room.")
    speak(tts, "examine, followed by an item in a room or your inventory to hear a description of that item")
    speak(tts, "take, followed by an item to take it.")
    speak(tts, "use, followed by the item you would like to use, followed by what you would like to use it on.")
    speak(tts, "please only say one word at a time. you will be prompted to say more.")
    speak(tts, "inventory to hear a list of your items")
    speak(tts, "North, South, East, or West to move in that direction.")
    speak(tts, "say help to hear this guide again.")
    speak(tts, "otherwise, say one of the commands when prompted.")
    speak(tts, "you may speak when you hear 'proceed'.")


#this... was not working either. something about local variables.   
"""def moveroom(direction, currentroom):
    print(currentroom)
    if rooms[currentroom][direction]:
        currentroom = rooms[currentroom][direction]
    else:
        print(moveerr)"""

#it should be speak room instead? will say puzzle components if needed
def printRoom():
    speak(tts, rooms[currentroom]['desc'])
    if not(rooms[currentroom]['puzSolved']):
        speak(tts, rooms[currentroom]['puzDesc'])

#when an item used, checks if progress is made.
def checkPuz(it, ob):
    match it:
        case "crowbar":
            if ob == "painting" and currentroom == "foyer":
                progress['paintingpried'] = True
                inventory.append("money")
                speak(tts, "there was money behind the painting! got money.")
        case "yoghurt":
            if ob == "rat" and currentroom == "ratroom":
                progress['ratFed'] = True
                inventory.append("door key")
                speak(tts, "the rat loved the yoghurt! he gave you a door key out of gratitude.")
        case "water":
            if ob == "plant" and currentroom == "greenroom":
                progress['plantWatered'] = True
                inventory.append("wooden key")
                speak(tts, "the plant perked up. you see a key under its leaves. got a wooden key.")
        case "money":
            if ob == 'toad' and currentroom == 'foyer':
                progress['toadBribed'] = True
                speak(tts, "the toad accepted your bribe. he's out of your way.")
        case "wooden key":
            if ob == 'door' and currentroom == 'bedroom':
                progress['ratUnlocked'] = True
                rooms['bedroom']['East'] = 'ratroom'
                speak(tts, "the door unlocked! now you can go this way.")
        case "door key":
            if ob == 'door' and currentroom == 'foyer':
                progress['winCon'] = True
                speak(tts, "oh boy! you won!")


def main():
    introduce()
    playGame()


if __name__ == "__main__":
    main()
    
#how to game
    """
    take crowbar from bed, water/yoghurt from fridge
    use water on plant for rat key
    use key on rat door
    use yoghurt on rat for door key
    use crowbar on painting for money
    use money on toad
    use key on exit
    win!!
    """
