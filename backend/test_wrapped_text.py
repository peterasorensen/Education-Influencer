from manim import *
import random
import math


class EducationalScene(Scene):
    def construct(self):
        # Initialize elapsed time tracker
        elapsed_time = 0

        # Create all objects
        # Create text: title
        title = Text("Introduction to Mathematical Concepts and\nTheir Applications", font_size=48, color=BLUE)
        title.move_to(np.array([0.00, 0.00, 0]))

        # Create text: description
        description = Text("This is a very long description that explains the concept in\ndetail and would normally overflow off the screen if we\ndidn't have automatic text wrapping enabled", font_size=36, color=WHITE)
        description.move_to(np.array([0.00, 2.00, 0]))

        # Create text: small_note
        small_note = Text("Small footnote", font_size=24, color=GRAY)
        small_note.move_to(np.array([-0.00, -1.50, 0]))


        # Animations
        # Write: title
        wait_time = 0.00 - elapsed_time
        if wait_time > 0:
            self.wait(wait_time)
            elapsed_time = 0.00
        self.play(Write(title), run_time=2.00)
        elapsed_time += 2.00

        # Fade in: description
        wait_time = 2.50 - elapsed_time
        if wait_time > 0:
            self.wait(wait_time)
            elapsed_time = 2.50
        self.play(FadeIn(description), run_time=1.50)
        elapsed_time += 1.50

        # Fade in: small_note
        wait_time = 4.50 - elapsed_time
        if wait_time > 0:
            self.wait(wait_time)
            elapsed_time = 4.50
        self.play(FadeIn(small_note), run_time=1.00)
        elapsed_time += 1.00
