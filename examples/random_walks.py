import math
import os
import random
import tqdm

from anim import Frame, VideoWriter

WIDTH = 1280
HEIGHT = 720
FPS = 24

NUM_SECS = 20
NUM_FRAMES = NUM_SECS * FPS

STEPS_PER_LINE = WIDTH
X_STEP = STEPS_PER_LINE / WIDTH
Y_STEP = X_STEP * 3

LINE_WIDTH = 1

INITIAL_STEPS_PER_FRAME = 10
STEPS_PER_FRAME_MULTIPLIER = 1.025

CUR_DIR = os.path.dirname(os.path.realpath(__file__))
VIDEO_OUTPUT_PATH = os.path.join(CUR_DIR, 'random_walks.mov')


def main():
    frame = Frame(WIDTH, HEIGHT)
    video_writer = VideoWriter(FPS)

    steps_per_frame = INITIAL_STEPS_PER_FRAME
    x = 0
    y = HEIGHT / 2

    for _ in tqdm.trange(NUM_FRAMES):
        opacity = math.log(INITIAL_STEPS_PER_FRAME) / math.log(steps_per_frame)
        color = (1, 0, 0, opacity)
        points = [(x, y)]

        for _ in range(int(steps_per_frame)):
            x += X_STEP
            y += Y_STEP if random.randint(0, 1) else -Y_STEP
            points.append((x, y))

            if x > WIDTH:
                frame.line(points, color, LINE_WIDTH)
                x = 0
                y = HEIGHT / 2
                points = [(x, y)]

        frame.line(points, color, LINE_WIDTH)
        video_writer.add_frame(frame)
        steps_per_frame *= STEPS_PER_FRAME_MULTIPLIER

    video_writer.write_video(VIDEO_OUTPUT_PATH)


if __name__ == '__main__':
    main()
