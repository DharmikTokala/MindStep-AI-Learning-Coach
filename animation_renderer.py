import json
import os
import textwrap

from manim import *


def wrap_text(
    text,
    width=45
):

    if not text:
        return [""]

    return textwrap.wrap(
        text,
        width=width
    )[:5]


class StoryboardAnimation(Scene):

    def construct(self):

        storyboard_path = os.getenv(
            "STORYBOARD_JSON"
        )

        if not storyboard_path:

            raise RuntimeError(
                "Storyboard JSON not found."
            )

        with open(
            storyboard_path,
            "r",
            encoding="utf-8"
        ) as file:

            storyboard = json.load(
                file
            )


        # =================================================
        # TITLE
        # =================================================

        title_lines = wrap_text(
            storyboard.get(
                "title",
                "JEE Physics Lesson"
            ),
            35
        )

        title = Paragraph(
            *title_lines,
            alignment="center",
            font_size=38
        )

        self.play(
            FadeIn(title)
        )

        self.wait(1)

        self.play(
            FadeOut(title)
        )


        # =================================================
        # LEARNING GOAL
        # =================================================

        learning_goal = storyboard.get(
            "learning_goal",
            ""
        )

        if learning_goal:

            goal = Paragraph(
                *wrap_text(
                    learning_goal,
                    55
                ),
                alignment="center",
                font_size=27
            )

            self.play(
                FadeIn(goal)
            )

            self.wait(2)

            self.play(
                FadeOut(goal)
            )


        # =================================================
        # SCENES
        # =================================================

        for scene in storyboard.get(
            "scenes",
            []
        ):

            scene_number = scene.get(
                "scene_number",
                ""
            )

            scene_title_text = scene.get(
                "scene_title",
                ""
            )


            scene_title = Paragraph(
                *wrap_text(
                    f"Scene {scene_number}: "
                    f"{scene_title_text}",
                    45
                ),
                alignment="center",
                font_size=27
            )

            scene_title.to_edge(
                UP
            )

            self.play(
                FadeIn(
                    scene_title
                )
            )


            visual = self.create_visual(
                scene
            )

            visual.scale(
                0.85
            )

            self.play(
                FadeIn(
                    visual,
                    shift=UP * 0.2
                )
            )


            # Simple motion
            self.play(
                visual.animate.scale(
                    1.06
                ),
                run_time=0.6
            )

            self.play(
                visual.animate.scale(
                    1 / 1.06
                ),
                run_time=0.6
            )


            narration_text = scene.get(
                "narration",
                ""
            )

            narration = Paragraph(
                *wrap_text(
                    narration_text,
                    55
                ),
                alignment="center",
                font_size=20
            )

            narration.to_edge(
                DOWN
            )

            self.play(
                FadeIn(
                    narration
                )
            )


            focus_text = scene.get(
                "student_focus",
                ""
            )

            if focus_text:

                focus = Paragraph(
                    *wrap_text(
                        focus_text,
                        45
                    ),
                    alignment="center",
                    font_size=18
                )

                focus.next_to(
                    narration,
                    UP
                )

                self.play(
                    FadeIn(
                        focus
                    )
                )

            else:

                focus = None


            self.wait(
                3
            )


            remove_items = [
                scene_title,
                visual,
                narration
            ]

            if focus is not None:

                remove_items.append(
                    focus
                )


            self.play(
                *[
                    FadeOut(item)
                    for item
                    in remove_items
                ]
            )


        # =================================================
        # END
        # =================================================

        complete = Text(
            "Concept Complete",
            font_size=40
        )

        self.play(
            FadeIn(
                complete
            )
        )

        self.wait(
            1
        )


    # =====================================================
    # PHYSICS VISUALS
    # =====================================================

    def create_visual(
        self,
        scene
    ):

        text = (
            scene.get(
                "visual",
                ""
            )
            + " "
            + scene.get(
                "animation",
                ""
            )
            + " "
            + scene.get(
                "scene_title",
                ""
            )
        ).lower()


        # =================================================
        # CAPACITOR
        # =================================================

        if (
            "capacitor" in text
            or
            "parallel plate" in text
        ):

            left_plate = Line(
                UP * 1.7,
                DOWN * 1.7
            ).shift(
                LEFT * 1.5
            )

            right_plate = Line(
                UP * 1.7,
                DOWN * 1.7
            ).shift(
                RIGHT * 1.5
            )

            plus = Text(
                "+ + +",
                font_size=28
            ).next_to(
                left_plate,
                LEFT
            )

            minus = Text(
                "- - -",
                font_size=28
            ).next_to(
                right_plate,
                RIGHT
            )

            field_arrow = Arrow(
                LEFT * 1.1,
                RIGHT * 1.1
            )

            return VGroup(
                left_plate,
                right_plate,
                plus,
                minus,
                field_arrow
            )


        # =================================================
        # DIPOLE
        # =================================================

        if "dipole" in text:

            positive_circle = Circle(
                radius=0.5
            )

            positive_text = Text(
                "+q",
                font_size=26
            )

            positive = VGroup(
                positive_circle,
                positive_text
            ).shift(
                LEFT * 2
            )


            negative_circle = Circle(
                radius=0.5
            )

            negative_text = Text(
                "-q",
                font_size=26
            )

            negative = VGroup(
                negative_circle,
                negative_text
            ).shift(
                RIGHT * 2
            )


            connector = Line(
                positive.get_right(),
                negative.get_left()
            )


            return VGroup(
                connector,
                positive,
                negative
            )


        # =================================================
        # DIELECTRIC
        # =================================================

        if (
            "dielectric" in text
            or
            "polarisation" in text
            or
            "polarization" in text
        ):

            box = Rectangle(
                width=3,
                height=2
            )

            label = Text(
                "Dielectric",
                font_size=27
            )

            arrows = VGroup()

            for y in [
                -0.6,
                0,
                0.6
            ]:

                arrow = Arrow(
                    LEFT * 0.8,
                    RIGHT * 0.8
                )

                arrow.shift(
                    UP * y
                )

                arrows.add(
                    arrow
                )


            return VGroup(
                box,
                label,
                arrows
            )


        # =================================================
        # CONDUCTOR
        # =================================================

        if "conductor" in text:

            conductor = Circle(
                radius=1.5
            )

            label = Text(
                "Conductor",
                font_size=27
            )

            charges = VGroup()

            positions = [
                UP * 1.5,
                DOWN * 1.5,
                LEFT * 1.5,
                RIGHT * 1.5
            ]

            for position in positions:

                charge = Text(
                    "+",
                    font_size=26
                )

                charge.move_to(
                    position
                )

                charges.add(
                    charge
                )


            return VGroup(
                conductor,
                label,
                charges
            )


        # =================================================
        # ELECTRIC CHARGE / POTENTIAL
        # =================================================

        if (
            "charge" in text
            or
            "potential" in text
            or
            "electric field" in text
        ):

            source_circle = Circle(
                radius=0.6
            )

            source_text = Text(
                "+Q",
                font_size=28
            )

            source = VGroup(
                source_circle,
                source_text
            )


            ring_1 = Circle(
                radius=1.4
            )

            ring_2 = Circle(
                radius=2.2
            )


            point = Dot(
                RIGHT * 2.2
            )

            point_label = Text(
                "P",
                font_size=24
            ).next_to(
                point,
                UP
            )


            distance = Line(
                source.get_right(),
                point.get_left()
            )


            distance_label = Text(
                "r",
                font_size=24
            ).next_to(
                distance,
                DOWN
            )


            return VGroup(
                ring_2,
                ring_1,
                source,
                distance,
                distance_label,
                point,
                point_label
            )


        # =================================================
        # GENERIC
        # =================================================

        circle = Circle(
            radius=1.2
        )

        arrow = Arrow(
            LEFT * 2.5,
            RIGHT * 2.5
        )

        label = Text(
            "Physics",
            font_size=28
        )

        return VGroup(
            circle,
            arrow,
            label
        )