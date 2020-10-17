import glob
import os
import subprocess
import tempfile

DEFAULT_FPS = 24
DEFAULT_OUTPUT_PATH = 'video.mov'

# Set `FFMPEG_PATH` to the local path of your installation of ffmpeg.
# I use the Homebrew version: https://formulae.brew.sh/formula/ffmpeg
DEFAULT_FFMPEG_PATH = glob.glob('/usr/local/Cellar/ffmpeg/*/bin/ffmpeg')[-1]


class VideoWriter:
    def __init__(self, fps=DEFAULT_FPS, frames_dir=None, ffmpeg_path=DEFAULT_FFMPEG_PATH):
        self.fps = fps
        self.frames_dir = frames_dir
        self.ffmpeg_path = ffmpeg_path
        self.tmp_dir_handle = None

        if self.frames_dir is None:
            self.tmp_dir_handle = tempfile.TemporaryDirectory()
            self.frames_dir = self.tmp_dir_handle.name

        self.frame_num = 0
        self.audio_path = None

    def add_frame(self, frame):
        frame.write_to_png(os.path.join(self.frames_dir, f'{self.frame_num}.png'))
        self.frame_num += 1

    def add_audio(self, audio_path):
        self.audio_path = audio_path

    def write_video(self, output_path=DEFAULT_OUTPUT_PATH):
        frame_pattern = os.path.join(self.frames_dir, '%d.png')
        args = [
            self.ffmpeg_path,
            '-y',
            '-f',
            'image2',
            '-framerate',
            str(self.fps),
            '-i',
            frame_pattern,
        ]

        if self.audio_path is not None:
            args.extend(['-i', self.audio_path])

        args.extend(['-c:v', 'prores_ks', '-profile:v', '3', output_path])

        print(f'Writing video...')
        subprocess.run(args)

    def __del__(self):
        if self.tmp_dir_handle is not None:
            self.tmp_dir_handle.cleanup()
