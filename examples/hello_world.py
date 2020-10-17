import math

import cairo
import tqdm

from anim import Frame, VideoWriter

WIDTH = 720
HEIGHT = 320
FPS = 24
COUNT_DOWN_SECS = 10


def main():
    frame = Frame(WIDTH, HEIGHT)
    video_writer = VideoWriter(fps=FPS)

    center_x = frame.width / 2
    center_y = frame.height / 2

    # Write 'Hello, World!' in the middle of the frame, then blur the
    # frame, then write the text again. This will generate a text glow
    # effect.
    frame.text(
        text='Hello, World!',
        x=center_x,
        y=center_y - 30,
        color='00f0ffcc',
        font_size=100,
        align='center',
    )
    frame.blur(blur_radius=8)
    frame.text(
        text='Hello, World!',
        x=center_x,
        y=center_y - 30,
        color='00f0ff',
        font_size=100,
        align='center',
    )

    bar_width = WIDTH - 100
    bar_height = 30
    bar_x = center_x - bar_width / 2
    bar_y = HEIGHT - 50 - bar_height / 2
    bar_blur_radius = 8

    count_down_frames = COUNT_DOWN_SECS * FPS + 1

    # Set the font for the countdown time text.
    frame.set_font(font_face='Helvetica')

    for frame_num in tqdm.trange(count_down_frames):
        cur_secs = frame_num / FPS
        progress = cur_secs / COUNT_DOWN_SECS
        secs_left = COUNT_DOWN_SECS - cur_secs

        frame.clear_rect(
            x=bar_x - 50, y=bar_y - 100, width=bar_width + 100, height=bar_height + 200,
        )

        # Draw the progress bar foreground with a glow blur.
        frame.line(
            points=[(bar_x, bar_y), (bar_x + bar_width * progress, bar_y)],
            color='f0f',
            line_width=30,
        )
        frame.blur_rect(
            x=bar_x - bar_blur_radius * 2,
            y=bar_y - bar_height / 2 - bar_blur_radius * 2,
            width=bar_width + bar_blur_radius * 4,
            height=bar_height + bar_blur_radius * 4,
            blur_radius=bar_blur_radius,
        )
        frame.line(
            points=[(bar_x, bar_y), (bar_x + bar_width * progress, bar_y)],
            color='f0f',
            line_width=30,
        )

        # Draw the progress bar background. We have to do this after the
        # foreground so that it won't get blurred.
        frame.line(
            points=[(bar_x, bar_y), (bar_x + bar_width, bar_y)], color='f0f3', line_width=30,
        )

        # Draw the countdown time.
        frame.time(
            secs=math.ceil(secs_left),
            x=bar_x + bar_width - 2,
            y=bar_y - 40,
            color='f0f',
            font_size=32,
            align='right',
            keep_mins=True,
        )

        video_writer.add_frame(frame)

    video_writer.write_video('hello_world.mov')


if __name__ == '__main__':
    main()
