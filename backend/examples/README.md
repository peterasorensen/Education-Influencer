# Word-Sync Examples Directory

This directory contains working examples demonstrating word-level timestamp synchronization and dynamic Manim animations.

## Files

### 1. example_word_timestamps.json
Sample word-level timestamp data extracted from audio.

**Contains:**
- 3 segments with narration text
- Word-by-word timing for each segment
- Start/end times for every word

**Use case:** Shows the data format from `timestamp_extractor.py`

### 2. example_storyboard_word_sync.json
Complete storyboard with word-synchronized animation actions.

**Contains:**
- 3 scenes covering Einstein's E=mc² explanation
- 15+ word-sync actions mapped to narration
- All sync action types demonstrated

**Use case:** Shows the storyboard format from `storyboard_generator.py`

### 3. example_word_sync_manim.py
Working Manim code implementing all word-synchronized animations.

**Contains:**
- Complete Scene class with sync_to_word() helper
- 15+ synchronized animations
- Proper timing coordination
- All animation action types

**Run it:**
```bash
cd examples
manim -pql example_word_sync_manim.py EducationalScene
```

This will generate a 15-second video showing:
- Flash effects on title mentions
- Scale pops for emphasis
- Circumscribe for equation highlighting
- Indicate for variable explanations
- Wiggle for interchangeability
- Color pulses and focus effects

## Quick Start

### Test Word Extraction
```bash
# View the word timestamp format
cat example_word_timestamps.json | python -m json.tool
```

### Test Storyboard Format
```bash
# View the storyboard with word-sync
cat example_storyboard_word_sync.json | python -m json.tool
```

### Test Manim Rendering
```bash
# Render the example animation
manim -pql example_word_sync_manim.py EducationalScene

# For high quality
manim -qh example_word_sync_manim.py EducationalScene
```

## Animation Timeline

The example demonstrates this animation sequence:

```
0.0s - Title appears: "Einstein's Equation"
0.8s - Equation writes in: E = mc²

[Word-Synchronized Animations]
1.6s - "Einstein's" → Flash title (0.3s)
2.1s - "famous" → Scale pop title (0.3s)
2.8s - "equation" → Circumscribe equation (0.6s)

5.0s - Title fades out
5.5s - Equation moves up

5.2s - "E" → Indicate E variable (0.4s)
6.5s - "energy" → Color pulse E (0.4s)
6.8s - "M" → Indicate M variable (0.4s)
7.4s - "mass" → Wiggle M (0.4s)
8.0s - "C" → Indicate C variable (0.4s)
8.8s - "speed" → Circumscribe C (0.5s)
9.5s - "light" → Flash C (0.3s)

10.0s - Mass and energy circles appear
12.0s - "mass" → Indicate mass circle (0.4s)
12.9s - "energy" → Indicate energy circle (0.4s)
14.5s - "interchangeable" → Wiggle arrows (0.5s)

15.0s - End
```

## Expected Output

When you run the Manim example, you should see:

1. **Title Animation**
   - Smooth fade in
   - Flash effect when "Einstein" mentioned
   - Pop effect when "famous" mentioned

2. **Equation Breakdown**
   - Write animation revealing E=mc²
   - Circumscribe highlighting whole equation
   - Individual variable highlights as mentioned

3. **Energy-Mass Relationship**
   - Circles representing mass and energy
   - Bidirectional arrows
   - Wiggle effect showing interchangeability

## Word-Sync Actions Used

| Action | Count | Usage |
|--------|-------|-------|
| indicate | 7 | Variable emphasis |
| flash | 2 | Title attention |
| circumscribe | 2 | Equation highlighting |
| wiggle | 2 | Playful motion |
| scale_pop | 1 | Title emphasis |
| color_pulse | 1 | Variable coloring |

**Total:** 15 synchronized animations in 15 seconds (1 per second average)

## Customization

### Modify Timing
Edit the `word_sync` array in `example_storyboard_word_sync.json`:
```json
{
  "word": "Einstein's",
  "time": 1.6,  // Change this
  "action": "flash",
  "target": "title"
}
```

### Change Actions
Edit the action type:
```json
{
  "word": "equation",
  "time": 2.8,
  "action": "wiggle",  // Try different actions
  "target": "equation"
}
```

Available actions:
- indicate
- flash
- circumscribe
- wiggle
- focus
- color_pulse
- scale_pop

### Add More Sync Points
Add entries to the word_sync array:
```json
{
  "word": "squared",
  "time": 4.9,
  "action": "indicate",
  "target": "exponent"
}
```

## Performance Notes

- Each animation is 0.3-0.6s (short and punchy)
- Total animation time: ~5.5s out of 15s (37% coverage)
- Word coverage: 70% (7 out of 10 key words)
- Animation density: Optimal for engagement

## Integration with Your Pipeline

To integrate word-sync in your own content:

1. **Extract word timestamps:**
   ```python
   await extractor.extract_timestamps(
       audio_path=audio,
       output_word_timestamps_path=Path("word_timestamps.json")
   )
   ```

2. **Generate storyboard with sync:**
   ```python
   storyboard = await generator.generate_storyboard(
       script=script,
       word_timestamps=word_timestamps
   )
   ```

3. **Generate Manim code:**
   ```python
   await manim_gen.generate_manim_code(
       visual_instructions=storyboard["scenes"]
   )
   ```

4. **Render:**
   ```bash
   manim -qh generated_code.py EducationalScene
   ```

## Troubleshooting

### Animation not appearing?
- Check that Manim is installed: `pip install manim`
- Verify file path is correct
- Try low quality first: `-ql` instead of `-qh`

### Timing seems off?
- Word timestamps are from the example, not real audio
- In production, these come from Whisper API
- Adjust timing in JSON if needed

### Want to add narration audio?
```python
# In the construct method, before animations
self.add_sound("narration.mp3")
```

## Resources

- **Full Documentation:** `../WORD_SYNC_DOCUMENTATION.md`
- **Quick Start:** `../WORD_SYNC_QUICK_START.md`
- **Implementation:** `../IMPLEMENTATION_SUMMARY.md`
- **Test Suite:** `../test_word_sync_integration.py`

## Next Steps

1. Run the example: `manim -pql example_word_sync_manim.py`
2. Watch the output video
3. Modify word_sync actions in the JSON
4. Re-run to see changes
5. Integrate into your own content!

---

**Happy animating! Make it POP! 🎬✨**
