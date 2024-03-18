import tkinter as tk
from tkinter import ttk
import os
from moviepy.editor import VideoFileClip
import uuid
import torch
from TTS.api import TTS
import wave
import contextlib
import subprocess
import math
import whisper_timestamped as whisper
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip, concatenate_videoclips
import json
from PIL import Image, ImageTk, ImageSequence
import threading
import re
import time


def first_page():

    # Function to remove file extension
    def remove_extension(filename):
        return os.path.splitext(filename)[0]

    def get_tts(voice_path, text_path, callback):
        id = uuid.uuid4()
        device = "cuda" if torch.cuda.is_available() else "cpu"
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

        with open(f"../text_stories/{text_path}.txt", 'r', encoding='utf-8', errors='ignore') as file:
            file_content = file.read()

        tts.tts_to_file(text=file_content,speaker_wav=f"../voices/{voice_path}.wav", language="en", file_path=f"../stories/{id}.wav")

        fname = f"../stories/{id}.wav"
        with contextlib.closing(wave.open(fname,'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
            root.after(0, callback, math.ceil(duration), id)


    def on_audio_complete(result1, result2):
        stop_loading_animation()
        show_second_page(result1 + 1, result2)
        
        print("Result 1:", result1)
        print("Result 2:", result2)
        # Update the GUI with these results if needed

    def on_audio_submit():
        submit_button.config(state="disabled")
        start_loading_animation("Generating Audio")
        selected_story = story_combobox.get()
        selected_voice = voice_combobox.get()
        print("Selected Story:", selected_story)
        print("Selected Voice:", selected_voice)
        threading.Thread(target=get_tts, args=(selected_voice, selected_story, on_audio_complete)).start()

    # List files in ../text_stories and ../voices directories
    for widget in root.winfo_children():
        widget.pack_forget()
    stories_dir = "../text_stories"
    voices_dir = "../voices"

    story_files = [remove_extension(f) for f in os.listdir(stories_dir) if os.path.isfile(os.path.join(stories_dir, f))]
    voice_files = [remove_extension(f) for f in os.listdir(voices_dir) if os.path.isfile(os.path.join(voices_dir, f))]
    
    # Create a label and combobox for story selection
    story_label = tk.Label(root, text="Select a story:", bg='white', font=modern_font)
    story_label.pack(pady=5)

    story_combobox = ttk.Combobox(root, values=story_files, state="readonly", font=modern_font)
    story_combobox.pack()

    # Create a label and combobox for voice selection
    voice_label = tk.Label(root, text="Select a voice:", bg='white', font=modern_font)
    voice_label.pack(pady=5)

    voice_combobox = ttk.Combobox(root, values=voice_files, state="readonly", font=modern_font)
    voice_combobox.pack()

    # Create a submit button
    submit_button = tk.Button(root, text="Generate Audio", command=on_audio_submit, font=modern_font)
    submit_button.pack(pady=10)
    root.mainloop()  # Start the GUI event loop




def show_second_page(duration, id):
    # Hide or destroy old widgets

    def submit_youtube_link(url, start, end): 
        
        def get_best_format():
            try:
                # Run the yt-dlp command with --list-formats
                text = subprocess.run(['yt-dlp', '-F', url], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stdout

                # Regular expression to match ID numbers at the beginning of each line
                pattern = re.compile(r'^(\d+)', re.MULTILINE)

                # Find all matches and convert them to integers
                ids = [int(match.group(1)) for match in pattern.finditer(text)]

                # Get the maximum ID, if any IDs were found
                desired_id = 22
                if 299 in ids:
                    desired_id = 299

                return desired_id

            except subprocess.CalledProcessError as e:
                # Handle errors in the subprocess
                print(f"An error occurred: {e.stderr}")


        """Download and cut the video using ffmpeg."""
        start_loading_animation("Downloading Youtube Video")
        format_id = get_best_format()
        command = ["yt-dlp", "-f", str(format_id), "--get-url", url]
        result = subprocess.run(command, stdout=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise Exception("yt-dlp command failed")
        
        direct_url = result.stdout.strip()
        command = [
            "ffmpeg", "-ss", str(start), "-i", direct_url, "-t", str(float(end) - float(start)),
            "-c:v", "copy", "-c:a", "copy", f"../base_mp4/{id}.mp4"
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise Exception("ffmpeg command failed: " + result.stderr)

        stop_loading_animation()
        show_third_page(id, float(end) - float(start))



    for widget in root.winfo_children():
        widget.pack_forget()  # or widget.destroy()

    # Display new content with the duration
    duration_message = f"The audio that was generated is {duration} seconds long"
    duration_label = tk.Label(root, text=duration_message, bg='white', font=modern_font)
    duration_label.pack(pady=(10, 5))  # Add some padding for better spacing

    # Create a label and entry for YouTube link input
    youtube_label = tk.Label(root, text="Please enter a YouTube link:", bg='white', font=modern_font)
    youtube_label.pack(pady=(5, 2))
    youtube_entry = tk.Entry(root, font=modern_font, width=40)
    youtube_entry.pack(pady=(2, 10))

    # Instructions for cropping the video
    crop_instructions = "Now you're going to crop the video. Please choose a starting time and ending time in the YouTube video. Keep in mind this time must be longer than the duration of the audio."
    instructions_label = tk.Label(root, text=crop_instructions, wraplength=350, justify="left", bg='white', font=modern_font)
    instructions_label.pack(pady=(10, 5))

    # Entry for start time
    start_time_label = tk.Label(root, text="Start Time (Seconds):", bg='white', font=modern_font)
    start_time_label.pack(pady=(5, 2))
    start_time_entry = tk.Entry(root, font=modern_font, width=15)
    start_time_entry.pack(pady=(2, 5))

    # Entry for end time
    end_time_label = tk.Label(root, text="End Time (Seconds):", bg='white', font=modern_font)
    end_time_label.pack(pady=(5, 2))
    end_time_entry = tk.Entry(root, font=modern_font, width=15)
    end_time_entry.pack(pady=(2, 10))

    # Submit button for all details
    submit_button = tk.Button(root, text="Submit All Details", font=modern_font, command=lambda: submit_youtube_link(youtube_entry.get(), start_time_entry.get(), end_time_entry.get()))
    submit_button.pack(pady=(10, 0))
    


def show_third_page(id, final_duration):

    def generate_subtitles():
        audio = whisper.load_audio(f"../stories/{id}.wav")
        model = whisper.load_model("tiny", device="cpu")
        dict = whisper.transcribe(model, audio, language="en")
        word_list = []
        for i in dict["segments"]:
            for words in i["words"]:
                word_list.append([words["text"], words["start"], words["end"]])

        return word_list
    

    def add_words_to_video(video_path, word_objects, output_path, audio_path, final_duration):
        start_loading_animation("Splicing Audio and Youtube Video")
        video = VideoFileClip(video_path)
        clips = [video]  # Start with the original video
        #vid_width, vid_height = video.size
        font_path = r"/mnt/c/Users/autor/Downloads/Koblenz-Serial-Heavy.ttf"
        #print(TextClip.list('color'))

        for i, word_obj in enumerate(word_objects):
            # Adjust the start time for continuous flow
            stroke_width = 7
            if i > 0:
                word_obj[1] = word_objects[i-1][2]

            text_clip_stroke = TextClip(word_obj[0],
                                    fontsize=80,
                                    color=color_combobox.get(),
                                    font=font_path,
                                    stroke_width=stroke_width,
                                    stroke_color="black",
                                    align='center',
                                    method='caption',
                                    ).set_duration(min(.65, word_obj[2] - word_obj[1])
                                    ).set_start(word_obj[1])
            
            text_clip = TextClip( word_obj[0],
                            fontsize=80,
                            color=color_combobox.get(),
                            font=font_path,
                            align='center',
                            method='caption',
                            ).set_duration(min(.65, word_obj[2] - word_obj[1])
                            ).set_start(word_obj[1])
            
            
            stroked_text_clip = CompositeVideoClip([text_clip_stroke, text_clip]).set_position(("center", "center"))
            clips.append(stroked_text_clip)

        final_clip = CompositeVideoClip(clips).subclip(0, final_duration)
        audio_clip = AudioFileClip(audio_path)
        final_clip = final_clip.set_audio(audio_clip)
        final_clip.write_videofile(output_path, codec='libx264', fps = 60)
        stop_loading_animation()
        show_final_page()

    words_obj = generate_subtitles()

    for widget in root.winfo_children():
        widget.pack_forget()

    # Dropdown menu options
    color_options = ["white", "black", "blue", "green"]

    # Create a label for the dropdown
    color_label = tk.Label(root, text="Choose a subtitle color:", bg='white', font=modern_font)
    color_label.pack(pady=(5, 2))

    # Create a combobox for color selection
    color_combobox = ttk.Combobox(root, values=color_options, state="readonly", font=modern_font)
    color_combobox.pack(pady=(2, 10))


    # Create a submit button
    submit_button = tk.Button(root, text="Submit", command=lambda: add_words_to_video(f"../base_mp4/{id}.mp4", words_obj, f"../final_product/{id}.mp4", f"../stories/{id}.wav", final_duration), font=modern_font)
    submit_button.pack(pady=(10, 0))


def show_final_page():
    # Hide or destroy old widgets
    for widget in root.winfo_children():
        widget.pack_forget()

    # Display the question
    question_label = tk.Label(root, text="Would you like to generate another?", bg='white', font=modern_font)
    question_label.pack(pady=(10, 5))

    # Function to restart the process
    def restart_process():
        first_page()

    # Function to exit the application
    def exit_application():
        root.destroy()

    # Create a frame to hold the buttons
    button_frame = tk.Frame(root, bg='white')
    button_frame.pack(pady=10)

    # Create "Yes" button inside the frame
    yes_button = tk.Button(button_frame, text="Yes", command=restart_process, font=modern_font)
    yes_button.pack(side=tk.LEFT, padx=10)

    # Create "No" button inside the frame
    no_button = tk.Button(button_frame, text="No", command=exit_application, font=modern_font)
    no_button.pack(side=tk.RIGHT, padx=10)


def start_loading_animation(text):
    global loading_label
    loading_label = tk.Label(root, text=text, bg='white', font=modern_font)
    loading_label.pack(pady=10)
    update_loading_text()

def update_loading_text():
    if loading_label.winfo_exists():  # Check if the label still exists
        current_text = loading_label.cget("text")
        if current_text.endswith("..."): 
            loading_label.config(text=current_text[:-3])
        else:
            loading_label.config(text=current_text + ".")
        root.after(500, update_loading_text)  # Update every 500 milliseconds

def stop_loading_animation():
    if loading_label.winfo_exists():  # Check if the label still exists
        loading_label.pack_forget()


    
root = tk.Tk()
root.title("Short Form Content Generator")
root.geometry("800x600")
root.configure(bg='white')
modern_font = ("Helvetica", 12)
first_page()  # Initialize the first page

