import os
import sys

# Set up directories for fonts and images
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'display/pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'display/lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

from display.lib.waveshare_epd import epd2in13b_V4
from PIL import Image, ImageDraw, ImageFont

PADDING_LEFT = 6


class EPaperDisplayManager:
    def __init__(self):
        self.epd = epd2in13b_V4.EPD()
        self.font_path = os.path.join(picdir, 'OpenSans-Regular.ttf')
        self.font_path_bold = os.path.join(picdir, 'OpenSans-ExtraBold.ttf')
        self.display_width = self.epd.height  # Width and height are reversed
        self.display_height = self.epd.width
        self.quadrant_width = self.display_width // 2
        self.quadrant_height = self.display_height // 2
        self.estimated_font_size = self.quadrant_height // 5
        self.estimated_font_size_big = self.quadrant_height // 3
        self.estimated_font_size_small = (self.estimated_font_size_big // 2) + 1
        self.font_content = ImageFont.truetype(self.font_path, self.estimated_font_size_big)
        self.font_title = ImageFont.truetype(self.font_path_bold, self.estimated_font_size)
        self.font_content_small = ImageFont.truetype(self.font_path, self.estimated_font_size_small)

    def _wrap_text(self, text, max_width, font):
        """ Wraps text to fit within a specified width. """
        lines = []
        words = text.split()

        while words:
            line = ''
            while words and font.getsize(line + words[0])[0] <= max_width - PADDING_LEFT:
                line += (words.pop(0) + ' ')
            lines.append(line)

        return lines

    def _draw_in_quadrant(self, draw, title, text, quadrant):
        """ Draws text in the specified quadrant. """
        wrapped_title = self._wrap_text(title, self.quadrant_width, self.font_title)
        wrapped_text = self._wrap_text(text, self.quadrant_width, self.font_content)

        x_offset = 0 if quadrant in [1, 3] else self.quadrant_width + PADDING_LEFT
        y_offset = 0 if quadrant in [1, 2] else self.quadrant_height

        x_offset_content = x_offset
        y_offset_content = y_offset + (self.estimated_font_size * 2)

        for line in wrapped_title:
            draw.text((x_offset, y_offset), line, font=self.font_title, fill=0)
            y_offset += self.font_title.getsize(line)[1]

        for text in wrapped_text:
            draw.text((x_offset_content, y_offset_content), text, font=self.font_content, fill=0)
            y_offset_content += self.font_content.getsize(text)[1]

    def _draw_in_quadrant_custom(self, draw_black, draw_red, title, content, quadrant, vertical_align="center"):
        wrapped_title = self._wrap_text(title, self.quadrant_width, self.font_title)

        x_offset_title = 0 if quadrant in [1, 3] else self.quadrant_width + PADDING_LEFT
        y_offset_title = 0 if quadrant in [1, 2] else self.quadrant_height

        x_offset_content = x_offset_title
        y_offset_content = y_offset_title + self.estimated_font_size

        if vertical_align == "center":
            y_offset_content = y_offset_title + (self.estimated_font_size * 2)

        # Vykreslenie titulku
        for line in wrapped_title:
            draw_black.text((x_offset_title, y_offset_title), line, font=self.font_title, fill=0)
            y_offset_title += self.font_title.getsize(line)[1]

        # Vykreslenie obsahu
        for i, item in enumerate(content):
            obj, newline, color, size = item
            draw = draw_red if color == "red" else draw_black
            font = self.font_content_small if size == "small" else self.font_content

            if isinstance(obj, str):
                # Vykreslenie textu
                lines = self._wrap_text(obj, self.quadrant_width, font)
                for line in lines:
                    draw.text((x_offset_content, y_offset_content), line, font=font, fill=0)

                    if newline == "n" and i != len(content) - 1:
                        y_offset_content += font.getsize(line)[1]  # Pridá riadok len ak to nie je posledný prvok

            elif isinstance(obj, Image.Image):
                # Vykreslenie obrázka
                draw.bitmap((x_offset_content, y_offset_content), obj, fill=0)
                y_offset_content += obj.height
                if newline == "n" and i != len(content) - 1:
                    y_offset_content += self.estimated_font_size_big  # Pridá riadok len ak to nie je posledný prvok

            # Prípadná medzera medzi prvky (len ak to nie je posledný prvok)
            if newline == "s" and i != len(content) - 1:
                x_offset_content += obj.width if isinstance(obj, Image.Image) else font.getsize(obj)[0]

    def update_display(self, display_data):
        """ Updates the display with provided data. """
        # Extract titles and texts directly from the display_data dictionary
        titles = list(display_data.keys())
        texts = [str(value) for value in display_data.values()]

        self.display_text_in_quadrants(titles, texts)

    def display_text_in_quadrants(self, titles, texts):
        """ Displays texts in the four quadrants. """
        if len(titles) != 4:
            raise ValueError("Four titles entries are required, one for each quadrant.")

        if len(texts) != 4:
            raise ValueError("Four text entries are required, one for each quadrant.")

        self.epd.init()
        self.epd.Clear()

        black_image = Image.new('1', (self.display_width, self.display_height), 255)
        red_image = Image.new('1', (self.display_width, self.display_height), 255)
        draw_black = ImageDraw.Draw(black_image)
        draw_red = ImageDraw.Draw(red_image)

        # Draw dividing lines
        draw_red.line((self.quadrant_width, 0, self.quadrant_width, self.display_height), fill=0)
        draw_red.line((0, self.quadrant_height, self.display_width, self.quadrant_height), fill=0)

        # Draw text in each quadrant
        for i, (title, text) in enumerate(zip(titles, texts)):
            if isinstance(text, str):
                self._draw_in_quadrant(draw_black, title, text, i + 1)
            else:
                self._draw_in_quadrant_custom(draw_black, draw_red, title, text, i + 1)

        black_image = black_image.rotate(180)
        red_image = red_image.rotate(180)

        # Update the display
        self.epd.display(self.epd.getbuffer(black_image), self.epd.getbuffer(red_image))
        self.epd.sleep()

# Usage example
# display_manager = EPaperDisplayManager()
#
# tits = ["Fear & Greed Index", "Bitcoin Price (€)", "Average Buy Price (€)", "Last transaction"]
# txtx = ["25", "39845.45", "39845.45", "12.12.2023"]
# display_manager.display_text_in_quadrants(tits, txtx)
