<h1><b>Project Goal</b></h1>
Do you ever see those YouTube short videos that have a stimulating background video and word for word captions of someone reading a reddit story? And then shortly after watching that video with millions and millions of views, do you wonder if you could create something like that? Well, you can now with this innovative program!!! 

<h1><b>Generated video using this repository</b></h1>

you can change the voice, text being read, background video, and much more!

https://github.com/johnbuts/TikTok_Generator/assets/66661618/db26e949-c0c6-49ed-92bf-24ac10d40dba

<h1><b>Installation Guide</b></h1>
Start off by making sure your python > 3.10, and then install the requirements.txt.
pip install requirements.txt
After this, you need to install ImageMagick https://imagemagick.org/index.php


<h1><b>Useage</b></h1>
Now that you've installed everything, let me provide a step-by-step guide on how to get started generating those videos.
Before you run the gui.py, you need to add some files. The model that we use takes in an audio file of someone speaking and the text you want to be read. You need to provide both of these things. Once you find the text that you want to have read aloud during the generated video, make it a .txt file and put it into the text_stories directory. The audio is a little bit more complicated. You need to find an audio clip featuring the voice of the person who you want to read your selected text. Meaning if you want a generated Morgan Freeman to read out your text file, you need to get a clean and clear audio file of just him speaking for around 2 minutes. Here's a youtube link that you can convert to a .wav file for great results. https://www.youtube.com/watch?v=-WEgTq8_ei4  Keep in mind, whichever voice you choose, **the audio must be in .wav format.** Once you have the .wav file of your favorite celebrity or politician speaking, drag that into the voices directory. Once you have your story and voice picked out, you are ready to run the gui.py.

**python gui/gui.py**

![Alt text](https://i.imgur.com/0spvV5V.png)

This is the first screen you are greeted with, please select your voice and story and give it a minute to generate the audio.

![Alt text](https://i.imgur.com/srNogcH.png)

Once your audio is generated, please fill in the YouTube link section for the video you would like to be playing in the background. For the start time field, choose the starting point at which you would like the background video to start playing. And also when you would like it to stop. Please try to make sure the difference between the end time and start time is over the duration of the audio otherwise the audio might get cut off. Then give it a second to find and crop the video for you.

![Alt text](https://i.imgur.com/EAiKrPp.png)

Select your caption color, and let the program generate the final product for you!

![Alt text](https://i.imgur.com/lmjY2KY.png)

Then choose if you would like to make another or exit.
