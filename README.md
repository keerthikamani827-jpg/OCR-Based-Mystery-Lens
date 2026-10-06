# 🔎 THE UNSEEN – OCR-Based Mystery Lens

A fun and interactive mystery challenge built with **Python and Streamlit**.

THE UNSEEN is a visual puzzle game where users carefully examine two mystery-room images, find hidden differences, and earn points for every correct discovery.

## 🚀 Live Demo

👉 https://ocr-based-mystery-lens-syuopytgipmaxnsv9ir8tx.streamlit.app/

## 📌 Project Overview

THE UNSEEN is designed as an interactive image-based mystery challenge.

The application provides:

- 🖼️ Two mystery-room images
- 🔎 Hidden-difference detection
- 🖱️ Click-based interaction
- ⭐ Score and star system
- ⏱️ 1-minute challenge timer
- ⏸️ Pause option
- 🏆 Final score display
- 🎯 Visual marking of discovered differences

The goal is to find all **20 differences** before the timer ends.

## 🎮 How to Play

1. Open the **THE UNSEEN** application.
2. Click **Start Game**.
3. Carefully compare the two images.
4. Click on an area where you think a difference exists.
5. A correct discovery gives:
   - ⭐ 1 Star
   - 🎯 10 Points
6. Continue searching for hidden differences.
7. Find all 20 differences to complete the challenge.
8. If the timer reaches zero, the game ends.

## 🏆 Scoring System

| Action | Result |
|---|---|
| Correct difference | ⭐ +1 Star |
| Correct difference | 🎯 +10 Points |
| 20 differences | 🏆 200 Points |
| Wrong click | ❌ No points |
| Already discovered area | No additional score |

## ⏱️ Game Timer

The game provides a **60-second timer**.

Players must find as many differences as possible before the time runs out.

The application also provides a **Pause** option so the player can temporarily stop the challenge.

## 🛠️ Technologies Used

- **Python**
- **Streamlit**
- **OpenCV**
- **NumPy**
- **Pillow**
- **streamlit-image-coordinates**

## 🔍 How It Works

The application processes the two mystery images using computer vision techniques.

### 1. Image Loading

The application loads the two mystery-room images from the `images` folder.

### 2. Image Processing

OpenCV is used to compare the images and identify areas that are visually different.

### 3. Difference Detection

The application uses image-difference processing and thresholding to identify potential difference regions.

### 4. User Interaction

Users click on the image to select a suspected difference.

### 5. Result Verification

The clicked location is compared with the detected difference regions.

- Correct click → Score increases
- Wrong click → No score
- Previously found difference → No duplicate score

### 6. Visual Feedback

Successfully discovered differences are highlighted with a green mark.

## 📁 Project Structure

```text
OCR-Based-Mystery-Lens/
│
├── app.py
├── requirements.txt
│
└── images/
    ├── mystery_room_1.png
    └── mystery_room_2.png

🎯 Project Objective

The main objective of THE UNSEEN is to create an engaging image-based puzzle application using computer vision and interactive web technologies.

The project demonstrates how image processing can be combined with a game-based user interface to create an interactive application.

🔮 Future Enhancements

Possible future improvements include:

🔐 Multiple mystery levels
🧩 Different difficulty modes
🏅 Leaderboard system
🎵 Background sound effects
🎨 More mystery-room scenes
📊 Player performance analytics
📱 Improved mobile responsiveness
🤖 AI-powered mystery clues
