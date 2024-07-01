import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import requests
import openai
from openai.error import InvalidRequestError, AuthenticationError, APIError
from auth import auth_token
from tkinter import messagebox
from pathlib import Path

openai.api_key = auth_token

# Verify API key before running the app
print(f"Using OpenAI API Key: {openai.api_key}")

class HomeScreen(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.configure(bg="#1E1E1E")  # Set background color
        self.create_widgets()

    def create_widgets(self):
        # Title label
        self.title_label = ctk.CTkLabel(self, text="Welcome to AI Generator", font=("Arial", 24))
        self.title_label.configure(text_color="white")  # Set text color
        self.title_label.pack(pady=(100, 20))  # Add vertical padding

        # Instruction label
        self.instruction_label = ctk.CTkLabel(self, text="Click the button below to generate images or speech from text.", font=("Arial", 16))
        self.instruction_label.configure(text_color="white")  # Set text color
        self.instruction_label.pack(pady=20)

        # Generate Image button
        self.generate_image_button = ctk.CTkButton(self, text="Generate Images", font=("Arial", 20), command=self.go_to_image_generator)
        self.generate_image_button.configure(text_color="white")  # Set text color
        self.generate_image_button.pack(pady=20)

        # Text to Speech button
        self.text_to_speech_button = ctk.CTkButton(self, text="Text to Speech", font=("Arial", 20), command=self.go_to_text_to_speech)
        self.text_to_speech_button.configure(text_color="white")  # Set text color
        self.text_to_speech_button.pack(pady=20)

    def go_to_image_generator(self):
        self.master.switch_to_image_generator()

    def go_to_text_to_speech(self):
        self.master.switch_to_text_to_speech()




from gtts import gTTS
import os
from datetime import datetime

class TextToSpeechScreen(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.configure(bg="#1E1E1E")  # Set background color
        self.create_widgets()

    def create_widgets(self):
        # Text input
        self.text_input = ctk.CTkEntry(self, font=("Arial", 16), placeholder_text="Enter text to convert to speech")
        self.text_input.pack(pady=20, padx=10, fill="x")

        # Generate Speech button
        self.generate_speech_button = ctk.CTkButton(self, text="Generate Speech", font=("Arial", 20), command=self.generate_speech)
        self.generate_speech_button.configure(text_color="white")  # Set text color
        self.generate_speech_button.pack(pady=20)

        # Back button
        self.back_button = ctk.CTkButton(self, text="Back", font=("Arial", 20), command=self.go_back)
        self.back_button.configure(text_color="white")  # Set text color
        self.back_button.pack(pady=20)

        # Status label
        self.status_label = ctk.CTkLabel(self, text="", font=("Arial", 16))
        self.status_label.configure(text_color="white")
        self.status_label.pack(pady=5)

    def generate_speech(self):
        input_text = self.text_input.get()
        if not input_text:
            # Handle empty input
            messagebox.showerror("Error", "Please enter text.")
            return

        try:
            # Generate spoken audio from input text using gTTS
            tts = gTTS(text=input_text, lang='en')
            
            # Create speech folder if it doesn't exist
            os.makedirs("speech", exist_ok=True)
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            speech_file_path = f"speech/speech_{timestamp}.mp3"
            tts.save(speech_file_path)

            # Show success message
            messagebox.showinfo("Success", f"Speech generated successfully!")
            self.status_label.configure(text=f"Speech generated successfully! File saved as '{speech_file_path}'")
        except Exception as e:
            # Handle errors
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            self.status_label.configure(text=f"Error: {e}")

    def go_back(self):
        self.master.switch_to_home()







class TextToImageGenerator(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.create_widgets()

    def create_widgets(self):
        # Create a frame for the main content
        main_frame = ctk.CTkFrame(self, width=620, height=700)
        main_frame.pack(pady=10, padx=10)

        # Entry for the prompt
        prompt_label = ctk.CTkLabel(main_frame, text="Enter your prompt:", font=("Arial", 18))
        prompt_label.pack(pady=10)

        self.prompt_input = ctk.CTkEntry(main_frame, 
                                    height=40, 
                                    width=520, 
                                    font=("Arial", 20), 
                                    text_color="black", 
                                    fg_color="white", 
                                    placeholder_text="Enter prompt here...")
        self.prompt_input.pack(pady=10)

        # Image Canvas
        self.main_image = tk.Canvas(main_frame, width=480, height=512, bg='gray')
        self.main_image.pack(pady=20)

        # Status label
        self.status_label = ctk.CTkLabel(main_frame, text="", font=("Arial", 16))
        self.status_label.pack(pady=5)

        # Function to generate image
        def apply_magic():
            global tk_img
            global img

            prompt = self.prompt_input.get()
            print(f"Prompt received: {prompt}")

            self.status_label.configure(text="Generating image...")

            try:
                response = openai.Image.create(prompt=prompt, n=1, size="512x512")
                image_url = response["data"][0]["url"]
                img = Image.open(requests.get(image_url, stream=True).raw)
                tk_img = ImageTk.PhotoImage(img)
                self.main_image.create_image(0, 0, anchor=tk.NW, image=tk_img)
                print("Image created for prompt:", prompt)
                self.status_label.configure(text="Image generated successfully!")
            except InvalidRequestError as e:
                print("InvalidRequestError:", e)
                messagebox.showerror("Error", "Billing limit reached or other request error.")
                self.status_label.configure(text="Error: Billing limit reached or other request error.")
            except AuthenticationError as e:
                print("AuthenticationError:", e)
                messagebox.showerror("Error", "Authentication failed. Check your API key.")
                self.status_label.configure(text="Error: Authentication failed.")
            except Exception as e:
                print("Error:", e)
                messagebox.showerror("Error", f"An unexpected error occurred: {e}")
                self.status_label.configure(text="Error: An unexpected error occurred.")

        # Function to save image
        def save_image():
            if img:
                prompt = self.prompt_input.get().replace(" ", "_")
                img.save(f"img/{prompt}.png")
                self.status_label.configure(text="Image saved successfully!")

        # Function to go back to the home screen
        def go_back():
            self.master.switch_to_home()

        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(pady=20)

        back_button = ctk.CTkButton(button_frame, 
                                    height=40, 
                                    width=150, 
                                    font=("Arial", 20), 
                                    text_color="white", 
                                    fg_color=("white", "gray38"), 
                                    command=go_back)
        back_button.configure(text="Back")
        back_button.grid(row=0, column=0, padx=10)

        magic_button = ctk.CTkButton(button_frame, 
                                     height=40, 
                                     width=150, 
                                     font=("Arial", 20), 
                                     text_color="white", 
                                     fg_color=("white", "gray38"), 
                                     command=apply_magic)
        magic_button.configure(text="Generate Image")
        magic_button.grid(row=0, column=1, padx=10)

        save_button = ctk.CTkButton(button_frame, 
                                    height=40, 
                                    width=150, 
                                    font=("Arial", 20), 
                                    text_color="white", 
                                    fg_color=("white", "gray38"), 
                                    command=save_image)
        save_button.configure(text="Save Image")
        save_button.grid(row=0, column=2, padx=10)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("650x850")
        self.title("AI Generator")
        ctk.set_appearance_mode("dark")

        self.home_screen = HomeScreen(self)
        self.image_generator_screen = TextToImageGenerator(self)
        self.text_to_speech_screen = TextToSpeechScreen(self)

        self.current_screen = None
        self.switch_to_home()

    def switch_to_home(self):
        if self.current_screen is not None:
            self.current_screen.pack_forget()
        self.current_screen = self.home_screen
        self.current_screen.pack(fill="both", expand=True)

    def switch_to_image_generator(self):
        if self.current_screen is not None:
            self.current_screen.pack_forget()
        self.current_screen = self.image_generator_screen
        self.current_screen.pack(fill="both", expand=True)

    def switch_to_text_to_speech(self):
        if self.current_screen is not None:
            self.current_screen.pack_forget()
        self.current_screen = self.text_to_speech_screen
        self.current_screen.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()
