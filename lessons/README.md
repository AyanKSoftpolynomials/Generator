# Lessons

Each lesson is one folder under `lessons/`:

```
lessons/
├── whole_numbers/
├── voice_demo/          (4 voice changes in one scene; test lesson)
├── integers/            (next)
└── ...
```

## Lesson folder

```
lesson_name/
├── animation.py         ← the only file you write: visuals + narrate() calls
├── source_script.txt    (optional) the original teaching script, for reference
├── assets/              images/SVGs used only by this lesson
├── README.md            notes
│
│   everything below is created by scripts/generate_video.py
├── generated/           script.json, timing.json, timeline.json, metadata.json, logs/
├── audio/               <narration_id>.wav clips + narration_track.wav
├── alignment/           alignment.json (word/sentence timestamps)
├── subtitles/           <lesson>.srt / <lesson>.vtt
└── output/              <lesson>.mp4 / <lesson>_preview.mp4
```

Never edit files in `generated/`: they are rebuilt from `animation.py` on
every run.

## Creating a new lesson

1. Make the folder: `New-Item -ItemType Directory lessons/whole_numbers/assets`
2. Write `lessons/whole_numbers/animation.py` (or have the AI write it from the
   teaching script):

   ```python
   from manim import *
   from src.animation import LMSScene

   class WholeNumbersVideo(LMSScene):
       lesson_title = "Whole Numbers"
       default_voice = "teacher_b"          # this lesson's main voice

       def construct(self):
           self.scene_start("hook")
           title = Text("WHOLE NUMBERS")
           n = self.narrate("hook_01", "Welcome back, everyone!")
           self.play_with(n, Write(title))
   ```

   The folder name is the lesson id and names the output files. Use
   `snake_case` for folders and narration ids, `PascalCase` for the class.
3. Preview: `python scripts/generate_video.py lessons/whole_numbers`
4. Final: `python scripts/generate_video.py lessons/whole_numbers --final`

The full API (`narrate`, `scene_start`, `play_with`, `at_word`,
`wait_for_narration`) and voice rules are in the main
[README](../README.md#3-writing-a-lesson-animationpy).
