import matplotlib.pyplot as plt
from fpdf import FPDF
from PIL import Image, ImageColor

import dataframe_image as dfi


class Team_PDF(FPDF):
    def __init__(self, team_name, image_path, color_hex):
        # Adding super class init
        super().__init__()

        # Add first page
        self.add_page()

        self.create_header(team_name, image_path)

        # Adding layout / rectangles
        self.set_fill_color(*ImageColor.getrgb(color_hex))
        self.rect(x=0, y=40, w=210, h=297 - 40, style='F')

        self.set_fill_color(255, 255, 255)
        self.rect(x=20, y=60, w=190, h=297 - 60, style='F')

    def create_header(self, text, image_path):
        # Set the font and font size
        self.set_font('Helvetica', 'BIU', 40)

        # Add the title text
        self.cell(w=190, h=20, txt=text, border=False, align="C")

        # Add a line below the title
        self.line(x1=0, y1=40, x2=210, y2=40)

        # Add the image
        self.image(image_path, x=10, y=5, w=20, h=0)

    def create_table(self, dataframe, title):
        # Set the font and font size
        self.set_font('Helvetica', 'B', 16)
        # Add the table title
        self.ln(10)
        self.x = 40
        self.write(h=110, txt=title)

        # Create table from dataframe
        dfi.export(dataframe, "../images/table.png", table_conversion="chrome")

        # Add the table
        self.image("../images/table.png", x=40, y=80, w=150)

    def create_card(self, text, image_path, data):
        # Set the font and font size
        self.set_font('Helvetica', 'B', 16)
        self.ln(10)
        self.x = 40
        self.y = 180

        # Add title
        if len(text) > 28:
            text = text[0:26] + '...'
        self.write(h=0, txt=text)
        self.ln(5)

        # Add image
        self.image_with_border(image_path, x=40, y=185, h=40)

        # Create table from data
        dfi.export(data, "../images/player_details.png", table_conversion="chrome")
        self.image("../images/player_details.png", x=73, y=185, h=40)

    def create_graph(self, title, dataframe):
        # Create piechart
        fig = plt.figure(figsize=(6, 6))
        total_goals = dataframe["FieldGoalsMade"].sum()
        data = [total_goals, dataframe["FieldGoalsAttempted"].sum() - total_goals]
        labels = ["Field goals made", "Field goals missed"]
        plt.pie(data, labels=labels, colors=['#FF4949', '#0F4392'], autopct='%.0f%%')
        plt.savefig("../images/pie.png", bbox_inches='tight')

        # Set the font and font size
        self.set_font('Helvetica', 'B', 16)
        self.ln(10)
        self.x = 120
        self.y = 180

        # Add title
        self.write(h=0, txt=title)
        self.ln(5)

        # Add graph
        self.image("../images/pie.png", x=120, w=70)

    def create_text_card(self, title, text):
        # Set the font and font size
        self.set_font('Helvetica', 'B', 16)
        self.ln(10)
        self.x = 40
        self.y = 240
        self.write(h=0, txt=title)
        self.ln(5)
        self.x = 40
        self.y = 248
        self.set_font('Helvetica', '', 12)
        self.write(h=0, txt=text)

    def create_footer(self, text, subtext):
        # Write text
        self.set_font('Helvetica', 'B', 16)
        self.ln(10)
        self.x = 40
        self.y = 260
        self.write(h=0, txt=text)

        # Write subtext
        self.set_font('Helvetica', '', 12)
        self.ln(10)
        self.x = 40
        self.y = 268
        self.write(h=0, txt=subtext)

    def image_with_border(self, path, x=0, y=0, h=0, border=True):
        image_obj = Image.open(path)
        image_width, image_height = image_obj.size

        # Calculate the width based on the aspect ratio of the image
        w = h * image_width / image_height

        self.image(path, x, y, w, h)
        if border:
            self.rect(x, y, w, h)
