"""
Example Manim Code with Word-Synchronized Animations
Demonstrates how to implement dynamic, engaging animations synced to narration.
"""

from manim import *
import numpy as np


class EducationalScene(Scene):
    """Einstein's E=mc^2 with word-synchronized animations."""

    def sync_to_word(self, target_time, elapsed_time):
        """
        Wait until target word time, then return that time.
        This helper function ensures animations sync perfectly with narration.
        """
        if target_time > elapsed_time:
            self.wait(target_time - elapsed_time)
        return target_time

    def construct(self):
        # Track elapsed time for synchronization
        elapsed_time = 0

        # ===== SCENE 1: Introduction (0.0s - 5.0s) =====
        # Narration: "Let's explore Einstein's famous equation E equals M C squared"

        # Create title
        title = Text("Einstein's Equation", font_size=48, color=BLUE)
        title.move_to(UP * 2.5)

        # Create equation (split into parts for word-sync highlighting)
        equation = MathTex(r"E", "=", "m", "c", r"^{2}", font_size=72)
        equation.move_to(ORIGIN)

        # Initial animations
        self.play(FadeIn(title), run_time=0.8)
        elapsed_time += 0.8

        self.play(Write(equation), run_time=1.5)
        elapsed_time += 1.5

        # WORD-SYNC ANIMATIONS for Scene 1

        # "Einstein's" at 1.2s - Flash the title
        elapsed_time = self.sync_to_word(1.6, elapsed_time)
        self.play(Flash(title, color=YELLOW, line_length=0.5), run_time=0.3)
        elapsed_time += 0.3

        # "famous" at 1.8s - Make title pop with scale
        elapsed_time = self.sync_to_word(2.1, elapsed_time)
        self.play(title.animate.scale(1.2), run_time=0.15)
        self.play(title.animate.scale(1/1.2), run_time=0.15)
        elapsed_time += 0.3

        # "equation" at 2.5s - Circumscribe the equation
        elapsed_time = self.sync_to_word(2.8, elapsed_time)
        self.play(Circumscribe(equation, color=RED, fade_out=True), run_time=0.6)
        elapsed_time += 0.6

        # Wait until scene transition
        self.wait(5.0 - elapsed_time)
        elapsed_time = 5.0

        # ===== SCENE 2: Breaking down the equation (5.0s - 10.0s) =====
        # Narration: "E represents energy, M is mass, and C is the speed of light"

        # Fade out title, keep equation
        self.play(FadeOut(title), run_time=0.5)
        elapsed_time += 0.5

        # Move equation up to make room for labels
        self.play(equation.animate.shift(UP * 1.5), run_time=0.8)
        elapsed_time += 0.8

        # WORD-SYNC ANIMATIONS for Scene 2

        # "E" at 5.5s - Indicate E variable
        elapsed_time = self.sync_to_word(5.2, elapsed_time)
        self.play(Indicate(equation[0], scale_factor=1.5, color=YELLOW), run_time=0.4)
        elapsed_time += 0.4

        # "energy" at 5.8s - Color pulse E
        elapsed_time = self.sync_to_word(6.5, elapsed_time)
        original_color_e = equation[0].get_color()
        self.play(equation[0].animate.set_color(GREEN), run_time=0.2)
        self.play(equation[0].animate.set_color(original_color_e), run_time=0.2)
        elapsed_time += 0.4

        # Add energy label
        energy_label = Text("Energy", font_size=28, color=GREEN)
        energy_label.next_to(equation[0], DOWN, buff=0.5)
        self.play(FadeIn(energy_label), run_time=0.3)
        elapsed_time += 0.3

        # "M" at 6.5s - Indicate M variable
        elapsed_time = self.sync_to_word(6.8, elapsed_time)
        self.play(Indicate(equation[2], scale_factor=1.5, color=ORANGE), run_time=0.4)
        elapsed_time += 0.4

        # "mass" at 6.8s - Wiggle M
        elapsed_time = self.sync_to_word(7.4, elapsed_time)
        self.play(Wiggle(equation[2], scale_value=1.3), run_time=0.4)
        elapsed_time += 0.4

        # Add mass label
        mass_label = Text("Mass", font_size=28, color=ORANGE)
        mass_label.next_to(equation[2], DOWN, buff=0.5)
        self.play(FadeIn(mass_label), run_time=0.3)
        elapsed_time += 0.3

        # "C" at 7.8s - Indicate C variable
        elapsed_time = self.sync_to_word(8.0, elapsed_time)
        self.play(Indicate(equation[3], scale_factor=1.5, color=BLUE), run_time=0.4)
        elapsed_time += 0.4

        # "speed" at 8.2s - Circumscribe C
        elapsed_time = self.sync_to_word(8.8, elapsed_time)
        self.play(Circumscribe(equation[3], color=BLUE, fade_out=True), run_time=0.5)
        elapsed_time += 0.5

        # "light" at 8.6s - Flash C (light reference!)
        elapsed_time = self.sync_to_word(9.5, elapsed_time)
        self.play(Flash(equation[3], color=YELLOW, line_length=0.4), run_time=0.3)
        elapsed_time += 0.3

        # Add speed of light label
        light_label = Text("Speed of Light", font_size=28, color=BLUE)
        light_label.next_to(equation[3], DOWN, buff=0.5)
        self.play(FadeIn(light_label), run_time=0.3)
        elapsed_time += 0.3

        # Wait until scene transition
        self.wait(10.0 - elapsed_time)
        elapsed_time = 10.0

        # ===== SCENE 3: Interchangeability (10.0s - 15.0s) =====
        # Narration: "This equation shows that mass and energy are interchangeable"

        # Clean up labels
        self.play(
            FadeOut(energy_label),
            FadeOut(mass_label),
            FadeOut(light_label),
            run_time=0.5
        )
        elapsed_time += 0.5

        # Move equation back to center
        self.play(equation.animate.move_to(ORIGIN), run_time=0.8)
        elapsed_time += 0.8

        # Create mass and energy representations
        mass_circle = Circle(radius=0.8, color=ORANGE, fill_opacity=0.7)
        mass_circle.move_to(LEFT * 3)
        mass_text = Text("Mass", font_size=32, color=WHITE)
        mass_text.move_to(mass_circle.get_center())

        energy_circle = Circle(radius=0.8, color=GREEN, fill_opacity=0.7)
        energy_circle.move_to(RIGHT * 3)
        energy_text = Text("Energy", font_size=32, color=WHITE)
        energy_text.move_to(energy_circle.get_center())

        # Arrows showing interchangeability
        arrow_right = Arrow(mass_circle.get_right(), energy_circle.get_left(), buff=0.2, color=YELLOW)
        arrow_left = Arrow(energy_circle.get_left(), mass_circle.get_right(), buff=0.2, color=YELLOW)
        arrow_left.shift(DOWN * 0.3)
        arrow_right.shift(UP * 0.3)

        # Create representations
        self.play(
            Create(mass_circle),
            Write(mass_text),
            run_time=0.6
        )
        elapsed_time += 0.6

        self.play(
            Create(energy_circle),
            Write(energy_text),
            run_time=0.6
        )
        elapsed_time += 0.6

        # WORD-SYNC ANIMATIONS for Scene 3

        # "This" at 10.2s - Focus on equation
        elapsed_time = self.sync_to_word(10.3, elapsed_time)
        self.play(FocusOn(equation), run_time=0.3)
        elapsed_time += 0.3

        # "mass" at 11.5s - Indicate mass circle
        elapsed_time = self.sync_to_word(12.0, elapsed_time)
        self.play(Indicate(mass_circle, scale_factor=1.3), run_time=0.4)
        elapsed_time += 0.4

        # "energy" at 12.2s - Indicate energy circle
        elapsed_time = self.sync_to_word(12.9, elapsed_time)
        self.play(Indicate(energy_circle, scale_factor=1.3), run_time=0.4)
        elapsed_time += 0.4

        # Create arrows
        self.play(Create(arrow_right), Create(arrow_left), run_time=0.6)
        elapsed_time += 0.6

        # "interchangeable" at 13.0s - Wiggle arrows to show interchange
        elapsed_time = self.sync_to_word(14.5, elapsed_time)
        self.play(
            Wiggle(arrow_right, scale_value=1.3),
            Wiggle(arrow_left, scale_value=1.3),
            run_time=0.5
        )
        elapsed_time += 0.5

        # Ending: Pulse everything together
        self.play(
            Indicate(mass_circle, scale_factor=1.2),
            Indicate(energy_circle, scale_factor=1.2),
            Indicate(equation, scale_factor=1.2),
            run_time=0.6
        )
        elapsed_time += 0.6

        # Final wait
        self.wait(15.0 - elapsed_time)


if __name__ == "__main__":
    # This allows running the file directly for testing
    import os
    os.system(f"manim -pql {__file__} EducationalScene")
