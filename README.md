# Pycairo Animation Library

A library for generating animations using [Pycairo](https://pycairo.readthedocs.io/en/latest/) (the Python version of Cairo) and [ffmpeg](https://ffmpeg.org/ffmpeg.html). Pycairo is used to generate each frame of the animation and then an ffmpeg process is called to merge all those frames into a ProRes (.mov) video file.

### Requirements

* [pycairo](https://pypi.org/project/pycairo/) - `conda install pycairo` or `pip install pycairo`
* [Pillow](https://pypi.org/project/Pillow/) - `conda install pillow` or `pip install Pillow`
* [ffmpeg](https://formulae.brew.sh/formula/ffmpeg) - `brew install ffmpeg`
    * To use a different version of ffmpeg (A non-Homebrew version), just specify the `ffmpeg_path` argument when initializing an instance of `VideoWriter` (it should be the path to the ffmpeg bin file that you want to use). 

### Overview

The [anim](/anim) directory contains two classes, `Frame` and `VideoWriter`.
The `Frame` class manages a Cairo surface (the image data) and a Cairo context (what Cairo uses to update the image data). The `Frame` class has methods for drawing lines, writing text, applying a blur, and clearing parts or all of the image. A `Frame` instance can be passed to a `VideoWriter` instance to write that frame to disk as a PNG image file in a temporary directory. Once all the frames have been written to disk, call the `write_video()` method on the `VideoWriter` instance to run the ffmpeg process that merges all those frames into a video file.

The [examples](/examples) directory contains examples of using the library. Here's the output from [`hello_world.py`](/examples/hello_world.py) (converted to a GIF):

![](/examples/hello_world.gif)


⚠️ There are currently very few methods available on the `Frame` class. I've only added the methods that I've needed for my personal use cases. But you can easily extend the class to meet your needs. If you want to extend the class, but you're not familiar with Pycairo, here's a great tutorial that explains how Pycairo works: [Cairo Tutorial for Python Programmers](http://www.tortall.net/mu/wiki/CairoTutorial)