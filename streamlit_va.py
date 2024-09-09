import time
import streamlit as st
import speech_recognition as sr
import pyttsx3
import random
import datetime
import requests
import datetime
from google.generativeai import GenerativeModel, configure

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

reminders = {}
MAX_TOKENS_PER_RESPONSE = 50

class TodoList:
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)
        speak(f"Task '{task}' added to your todo list.")

    def view_tasks(self):
        if self.tasks:
            speak("Here are the tasks in your todo list:")
            for index, task in enumerate(self.tasks, start=1):
                speak(f"Task {index}: {task}")
        else:
            speak("Your todo list is empty. No tasks to display.")

    def remove_task(self, index):
        if 1 <= index <= len(self.tasks):
            removed_task = self.tasks.pop(index - 1)
            speak(f"Task '{removed_task}' removed from your todo list.")
        else:
            speak("Invalid task index. Please provide a valid task number.")

def speak(text):
    text = ' '.join(text.split()[:50])  # Limit spoken text to first 50 words
    engine.say(text)
    engine.runAndWait()

def listen_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        command = recognizer.recognize_google(audio, language='en-in')
        print(f"User said: {command}\n")
        return command.lower()

    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that. Can you please repeat?")
    except sr.RequestError as e:
        speak("Sorry, there was an error processing your request. Please try again later.")
        print(f"Error: {e}")

    return ""

def greet_user():
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        speak("Good morning!")
    elif 12 <= hour < 18:
        speak("Good afternoon!")
    else:
        speak("Good evening!")

    speak("Hi there! How's your day going?")
    speak("What can I assist you with today?")

def respond_to_name_call(query):
    if "Altruisty" in query:
        speak("Yes, how can I help you?")

def handle_friendly_interaction(query):
    if "how are you" in query:
        speak("I'm doing well, thank you for asking!")
    elif "thank you" in query:
        speak("You're welcome! Feel free to ask if you need anything else.")
    elif "good day" in query or "have a great day" in query:
        speak("Thank you! You too have a fantastic day.")
    else:
        speak("I'm here to assist you. What do you need help with?")




def ask_doubt():
    speak("Sure! What's your doubt?")
    user_doubt = listen_command()
    if user_doubt:
        speak("Let me find the answer for you...")
        try:
            # Configure the API key
            configure(api_key="AIzaSyChqASBUL9NVkNOZPJyX0ND030_6c3WilY ")

            # Create a GenerativeModel instance with the desired model
            model = GenerativeModel("models/gemini-pro")

            # Use the model to generate a response
            response = model.generate_content(user_doubt)

            # Access the generated content from the response
            if isinstance(response, list):
                response_text = ""
                for choice in response:
                    ftr=choice.text.replace("*","") #CHANGED
                    response_text += ftr.strip() + " "  # Concatenate response text #CHANGED
                speak(response_text)
            else:
                ftr=response.text.replace("*","") #CHANGED
                speak(ftr.strip()) #CHANGED

        except Exception as e:
            print("Error:", e)
            speak("Sorry, I couldn't find an answer to your doubt.")

def todo_list_handler(todo_list):
    speak("What would you like to do with your todo list?")
    speak("1. Add a task")
    speak("2. View tasks")
    speak("3. Remove a task")
    speak("4. Go back")

    user_input = listen_command()

    if 'add' in user_input:
        speak("What task would you like to add?")
        task = listen_command()
        if task:
            todo_list.add_task(task)
    elif 'view' in user_input :
        todo_list.view_tasks()
    elif 'remove' in user_input or ('delete' in user_input and 'task' in user_input):
        speak("Please specify the task number to remove.")
        task_number = listen_command()
        try:
            task_index = int(task_number)
            todo_list.remove_task(task_index)
        except ValueError:
            speak("Invalid task number. Please try again.")
    elif 'back' in user_input or 'exit' in user_input or 'quit' in user_input:
        speak("Going back to main assistant.")
    else:
        speak("Sorry, I didn't catch that. Please try again.")

    # Allow some delay to prevent immediate repetition of user input processing
    time.sleep(1)

def handle_task_keywords(query, todo_list):
    if 'work task' in query:
        speak("It looks like you're mentioning a work task.")
        speak("Would you like to prepare a todo list?")
        prepare_todo_list = listen_command()
        if 'yes' in prepare_todo_list:
            speak("Let's prepare your todo list.")
            todo_list_handler(TodoList())
        else:
            speak("Let me know if you need assistance with anything else.")
    elif 'to do list' in query or 'todo list' in query:
        speak("Would you like to prepare a todo list?")
        prepare_todo_list = listen_command()
        if 'yes' in prepare_todo_list:
            speak("Let's prepare your todo list.")
            todo_list_handler(TodoList())
        else:
            speak("Let me know if you need assistance with anything else.")

def main():
    greet_user()

    # Initialize TodoList object
    todo_list = TodoList()

    while True:
        query = listen_command()

        if query:
            respond_to_name_call(query)
            handle_friendly_interaction(query)
            handle_task_keywords(query, todo_list)

        
            if any(word in query for word in ['congratulations', 'completed', 'done']):
                speak(random.choice(["Congratulations on completing your task!", "Well done!", "Great job!", "You did it!", "Fantastic work!", "Bravo!"]))
            elif 'doubt' in query:
                ask_doubt()
            elif 'exit' in query or 'quit' in query or 'bye' in query or 'goodbye' in query:
                speak("Goodbye!")
            elif 'todo list' in query or 'task' in query:
                todo_list_handler(todo_list)
                break
if __name__ == "__main__":
    st.title("Altruisty Voice Assistant")
    st.write("Click the button below to start interacting with the assistant.")
    if st.button("Start Assistant"):
        main()