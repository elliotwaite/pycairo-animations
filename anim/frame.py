import collections

import cairo
from PIL import Image, ImageChops, ImageFilter

DEFAULT_WIDTH = 1920
DEFAULT_HEIGHT = 1080
DEFAULT_FG_COLOR = (1, 1, 1, 1)
DEFAULT_BG_COLOR = (0, 0, 0, 1)

DEFAULT_FONT_FACE = 'Montserrat'
DEFAULT_FONT_SLANT = cairo.FontSlant.NORMAL
DEFAULT_FONT_WEIGHT = cairo.FontWeight.NORMAL
DEFAULT_FONT_SIZE = 64

DEFAULT_TIME_TEXT_SPACING = 0.15


TextExtents = collections.namedtuple(
    'TextExtents', ['x_bearing', 'y_bearing', 'width', 'height', 'x_advance', 'y_advance']
)


def color_to_rgba(color):
    """Converts a color (tuple or string) to an RGBA tuple.
    
    This function does not validate the input, so if the input format
    does not match one of the formats listed below, the output format
    is not guaranteed.

     Args:
         color: The color to be converted. It can be:
             An RGB tuple. 3 ints/floats between 0.0 and 1.0.
                e.g. (1, 0, 0)
             An RGBA tuple. 4 ints/floats between 0.0 and 1.0 (in which 
                case it is returned as is).
                e.g. (1, 0, 0, 0.5)
             An RGB hex string.
                e.g. #ff0000, ff0000, #f00, f00 (these are all 
                equivalent)
             An RGBA hex string.
                e.g. #ff0000cc, #f00c, ff0000cc, f00c (these are all 
                equivalent)
    Returns:
        A RGBA tuple of 4 ints/floats between the values 0.0 and 1.0.
    """
    if isinstance(color, tuple):
        if len(color) == 4:
            return color
        if len(color) == 3:
            return (*color, 1)

    if isinstance(color, str):
        _color = color.lstrip('#')
        if len(_color) == 3:
            _color = _color[0] * 2 + _color[1] * 2 + _color[2] * 2 + 'ff'
        elif len(_color) == 4:
            _color = _color[0] * 2 + _color[1] * 2 + _color[2] * 2 + _color[3] * 2
        elif len(_color) == 6:
            _color += 'ff'
        if len(_color) == 8:
            return tuple(int(_color[i : i + 2], 16) / 255 for i in range(0, 8, 2))

    raise ValueError(f'Invalid color: {color}')


def secs_to_time_str(secs, keep_mins=False):
    h = int(secs / 3600)
    m = int((secs % 3600) / 60)
    s = int(secs % 60)
    if h:
        return f'{h}:{m:02}:{s:02}'
    if m or keep_mins:
        return f'{m}:{s:02}'
    return f'{s}'


class Frame:
    def __init__(
        self,
        width=DEFAULT_WIDTH,
        height=DEFAULT_HEIGHT,
        fg_color=DEFAULT_FG_COLOR,
        bg_color=DEFAULT_BG_COLOR,
    ):
        self.width = width
        self.height = height
        self.fg_color = fg_color
        self.bg_color = bg_color
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        self.ctx = cairo.Context(self.surface)
        self.font_face = DEFAULT_FONT_FACE
        self.font_slant = DEFAULT_FONT_SLANT
        self.font_weight = DEFAULT_FONT_WEIGHT
        self.font_size = DEFAULT_FONT_SIZE
        self.ctx.select_font_face(self.font_face, self.font_slant, self.font_weight)
        self.ctx.set_font_size(self.font_size)
        self.clear()

    def _set_source_color(self, color):
        if color is not None:
            self.ctx.set_source_rgba(*color_to_rgba(color))
        else:
            self.ctx.set_source_rgba(*color_to_rgba(self.fg_color))

    def set_font(self, font_face=None, font_slant=None, font_weight=None, font_size=None):
        if font_face is not None or font_slant is not None or font_weight is not None:
            if font_face is not None:
                self.font_face = font_face
            if font_slant is not None:
                self.font_slant = font_slant
            if font_weight is not None:
                self.font_weight = font_weight
            self.ctx.select_font_face(self.font_face, self.font_slant, self.font_weight)

        if font_size is not None:
            self.font_size = font_size
            self.ctx.set_font_size(self.font_size)

    def clear(self):
        self.ctx.set_source_rgba(*color_to_rgba(self.bg_color))
        self.ctx.set_operator(cairo.Operator.SOURCE)
        self.ctx.paint()

    def clear_rect(self, x, y, width, height):
        self.ctx.set_source_rgba(*color_to_rgba(self.bg_color))
        self.ctx.set_operator(cairo.Operator.SOURCE)
        self.ctx.rectangle(x, y, width, height)
        self.ctx.fill()

    def line(self, points=None, color=None, line_width=2, close_path=False):
        """Draws a line connected by points.
        
        You can either specify the points as (x, y) tuples, or 

        Args:
            points (list of tuples of ints / floats): The list of (x, y)
                points that will be connected by lines.
            color (tuple of 3 or 4 ints or floats): The line color in
                rgb or rgba.
            line_width (int / float): The line width. Integer points
                are centered at the intersections of pixels, so odd line
                widths for lines that connect integer points in straight
                lines may appear blurry (use even line widths instead).
            close_path (bool): If True, a line will be drawn from the
                last point to the first point to close the path.
        """
        self._set_source_color(color)
        self.ctx.set_operator(cairo.Operator.OVER)
        self.ctx.set_line_width(line_width)

        self.ctx.move_to(*points[0])
        for point in points[1:]:
            self.ctx.line_to(*point)

        if close_path:
            self.ctx.close_path()

        self.ctx.stroke()

    def blur(self, blur_radius, translate_x=0, translate_y=0, multiply_count=0):
        """Applies a Gaussian blur to to the entire frame.

        Args:
            [See `blur_rect` below for argument descriptions.]
        """
        self.blur_rect(
            0, 0, self.width, self.height, blur_radius, translate_x, translate_y, multiply_count
        )

    def blur_rect(
        self, x, y, width, height, blur_radius, translate_x=0, translate_y=0, multiply_count=0
    ):
        """Applies a Gaussian blur to a rectangle of the frame.

        Args:
            x (int / float): Rectangle's x position.
            y (int / float): Rectangle's y position.
            width (int / float): Rectangle's width.
            height (int / float): Rectangle's height.
            blur_radius (int / float): Blur radius in pixels.
            translate_x (int / float): Applies a translation after the
                blur in the x direction (e.g. for a drop shadow).
            translate_y (int / float): Applies a translation after the
                blur in the y direction (e.g. for a drop shadow).
            multiply_count (int): The number of times to multiply the
                result of the blur with itself (e.g. to make drop
                shadows darker if they are too light).
        """
        # Note to self: We use set_source_surface() to position the
        # source over the destination, then we use rectangle() to
        # position the rectangle on the destination where data from the
        # source will be copied to the destination, or we use paint() to
        # copy the entire area from the source that is overlapping the
        # destination.
        tmp_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        tmp_ctx = cairo.Context(tmp_surface)
        tmp_ctx.set_operator(cairo.Operator.SOURCE)
        tmp_ctx.set_source_surface(self.surface, -x, -y)
        tmp_ctx.paint()

        img = Image.frombuffer(
            'RGBA', (width, height), tmp_surface.get_data(), 'raw', 'RGBA', 0, 1
        )
        img = img.filter(ImageFilter.GaussianBlur(blur_radius))
        for _ in range(multiply_count):
            img = ImageChops.multiply(img, img)
        arr = memoryview(bytearray(img.tobytes('raw', 'RGBA')))
        tmp_surface = cairo.ImageSurface.create_for_data(arr, cairo.FORMAT_ARGB32, width, height)
        self.ctx.set_operator(cairo.Operator.SOURCE)
        self.ctx.set_source_surface(tmp_surface, x + translate_x, y + translate_y)
        self.ctx.rectangle(x + translate_x, y + translate_y, width, height)
        self.ctx.fill()

    def text(self, text, x, y, color=None, font_size=None, align='center'):
        self.set_font(font_size=font_size)
        x_bearing, y_bearing, width, height, x_advance, y_advance = self.ctx.text_extents(text)
        if align == 'left':
            offset_x = x - x_bearing
        elif align == 'center':
            offset_x = x - width / 2 - x_bearing
        elif align == 'right':
            offset_x = x - width - x_bearing
        else:
            raise ValueError(f'Invalid align value: {align}')
        self.ctx.move_to(offset_x, y)
        self._set_source_color(color)
        self.ctx.set_operator(cairo.Operator.OVER)
        self.ctx.show_text(text)

    def time(
        self,
        secs,
        x,
        y,
        color=None,
        font_size=None,
        spacing=DEFAULT_TIME_TEXT_SPACING,
        align='center',
        keep_mins=False,
    ):
        """Writes a monospaced time text.

        This method can even be used with non-monospaced fonts and a
        monospaced version of the string will be printed.
        """
        text = secs_to_time_str(secs, keep_mins)

        self.set_font(font_size=font_size)
        extents = {char: TextExtents(*self.ctx.text_extents(char)) for char in '0123456789:'}

        self._set_source_color(color)
        self.ctx.set_operator(cairo.Operator.OVER)

        num_colons = text.count(':')
        num_numbers = len(text) - num_colons
        num_gaps = len(text) - 1
        gap_width = self.font_size * spacing
        width = (
            num_colons * extents[':'].width
            + num_numbers * extents['0'].width
            + num_gaps * gap_width
        )

        if text[0] == '1':
            width -= extents['0'].width - extents['1'].width

        if align == 'left':
            cur_x = x
        elif align == 'center':
            cur_x = x - width / 2
        elif align == 'right':
            cur_x = x - width
        else:
            raise ValueError(f'Invalid align value: {align}')

        for char_index, char in enumerate(text):
            if char == ':':
                char_x = cur_x - extents[':'].x_bearing
                cur_x += extents[':'].width + gap_width
            else:
                if char_index == 0 and char == '1':
                    char_x = cur_x - extents['1'].x_bearing
                    cur_x += extents['1'].width + gap_width
                else:
                    width_diff = extents['0'].width - extents[char].width
                    char_x = cur_x + width_diff / 2 - extents[char].x_bearing
                    cur_x += extents['0'].width + gap_width

            self.ctx.move_to(char_x, y)
            self.ctx.show_text(char)

    def write_to_png(self, path):
        self.surface.write_to_png(path)
