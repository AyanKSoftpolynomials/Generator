# Integers

Whole numbers + their negative reflections, on a number line. Ends with a
zoom toward fractions (transition to Rational Numbers).

- Voice: teacher_a throughout (one narration block per section).
- Scene class: `IntegersVideo(LMSMovingCameraScene)`; the moving-camera base
  is needed for the final `self.camera.frame` zoom.

```powershell
python scripts/generate_video.py lessons/integers            # preview
python scripts/generate_video.py lessons/integers --final    # Full HD
```

Output: `output/integers.mp4` (final) / `output/integers_preview.mp4`.
