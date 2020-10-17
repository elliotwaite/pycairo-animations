import os
import random
import tqdm

import anim

WIDTH = 3840
HEIGHT = 2160
FPS = 24

NUM_SECS = 20
LINES_PER_SEC = 4
STEPS_PER_LINE = WIDTH

NUM_FRAMES = NUM_SECS * FPS
STEPS_PER_FRAME = int(STEPS_PER_LINE * LINES_PER_SEC / FPS)

X_STEP = STEPS_PER_LINE / WIDTH
Y_STEP = X_STEP * 5

LINE_COLOR = (1, 0, 0, 0.025)
LINE_WIDTH = 1

CUR_DIR = os.path.dirname(os.path.realpath(__file__))
VIDEO_OUTPUT_PATH = os.path.join(CUR_DIR, 'random_walk.py')


def main():
    video_writer = anim.VideoWriter(FPS)
    frame = anim.Frame(WIDTH, HEIGHT)

    steps_per_frame = 10
    x = 0
    y = HEIGHT / 2
    for _ in tqdm.trange(NUM_FRAMES):
        points = [(x, y)]
        for _ in range(int(steps_per_frame)):
            x += X_STEP
            y += Y_STEP if random.randint(0, 1) else -Y_STEP
            points.append((x, y))
            if x > WIDTH:
                frame.line(points, LINE_COLOR, LINE_WIDTH)
                x = 0
                y = HEIGHT / 2
                points = [(x, y)]
        frame.line(points, LINE_COLOR, LINE_WIDTH)
        video_writer.add_frame(frame)
        steps_per_frame = steps_per_frame * 1.025

    video_writer.write_video(VIDEO_OUTPUT_PATH)


if __name__ == '__main__':
    main()
