import datetime
import calendar
import collections
import os.path
from reportlab.lib import pagesizes
from contextlib import contextmanager
from reportlab.pdfgen.canvas import Canvas
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont
from dateutil import relativedelta
from pprint import pprint


# Calendar dates names:
ORDINALS = {
    1: 'st', 2: 'nd', 3: 'rd',
    21: 'st', 22: 'nd', 23: 'rd',
    31: 'st',
    None: 'th'}

# Calendar params:
Font = collections.namedtuple('Font', ['name', 'size'])
Geom = collections.namedtuple('Geom', ['x', 'y', 'width', 'height'])
Size = collections.namedtuple('Size', ['width', 'height'])

# Moon months:
hmonths = {
    12: 'ADAR',
    5: 'AV',
    6: 'ELUL',
    8: 'HESHVAN',
    2: 'IYYAR',
    9: 'KISLEV',
    1: 'NISAN',
    11: 'SHEVAT',
    3: 'SIVAN',
    4: 'TAMMUZ',
    10: 'TEVETH',
    7: 'TISHRI',
    13: 'VEADAR'}

# Calendar coordinates. Horizontal/vertical step - 157-159px
calendar_coordinates = {
    "00": (58, 160),
    "01": (217, 160),
    "02": (376, 160),
    "03": (535, 160),
    "04": (694, 160),
    "05": (853, 160),
    "06": (1012, 160),
    "10": (58, 319),
    "11": (217, 319),
    "12": (376, 319),
    "13": (535, 319),
    "14": (694, 319),
    "15": (853, 319),
    "16": (1012, 319),
    "20": (58, 478),
    "21": (217, 478),
    "22": (376, 478),
    "23": (535, 478),
    "24": (694, 478),
    "25": (853, 478),
    "26": (1012, 478),
    "30": (58, 635),
    "31": (217, 635),
    "32": (376, 635),
    "33": (535, 635),
    "34": (694, 635),
    "35": (853, 635),
    "36": (1012, 635),
    "40": (58, 794),
    "41": (217, 794),
    "42": (376, 794),
    "43": (535, 794),
    "44": (694, 794),
    "45": (853, 794),
    "46": (1012, 794),
}


@contextmanager
def save_state(canvas):
    """Simple context manager to tidy up saving and restoring canvas state"""
    canvas.saveState()
    yield
    canvas.restoreState()


async def add_calendar_page(canvas, rect, datetime_obj, cell_cb, first_weekday=calendar.SUNDAY):
    """Create a one-month pdf calendar, and return the canvas

    @param rect: A C{Geom} or 4-item iterable of floats defining the shape of
        the calendar in points with any margins already applied.
    @param datetime_obj: A Python C{datetime} object specifying the month
        the calendar should represent.
    @param cell_cb: A callback taking (canvas, day, rect, font) as arguments
        which will be called to render each cell.
        (C{day} will be 0 for empty cells.)

    @type canvas: C{reportlab.pdfgen.canvas.Canvas}
    @type rect: C{Geom}
    @type cell_cb: C{function(Canvas, int, Geom, Font)}
    """
    calendar.setfirstweekday(first_weekday)
    cal = calendar.monthcalendar(datetime_obj.year, datetime_obj.month)
    rect = Geom(*rect)

    # set up constants
    scale_factor = min(rect.width, rect.height)
    line_width = scale_factor * 0.0025
    font = Font('Helvetica', scale_factor * 0.028)
    rows = len(cal)

    # Leave room for the stroke width around the outermost cells
    rect = Geom(rect.x + line_width,
                rect.y + line_width,
                rect.width - (line_width * 2),
                rect.height - (line_width * 2))
    cellsize = Size(rect.width / 7, rect.height / rows)

    # now fill in the day numbers and any data
    for row, week in enumerate(cal):
        for col, day in enumerate(week):
            # Give each call to cell_cb a known canvas state
            with save_state(canvas):

                # Set reasonable default drawing parameters
                canvas.setFont(*font)
                canvas.setLineWidth(line_width)

                cell_cb(canvas, day, Geom(
                    x=rect.x + (cellsize.width * col),
                    y=rect.y + ((rows - row) * cellsize.height),
                    width=cellsize.width, height=cellsize.height),
                    font, scale_factor)

    # finish this page
    canvas.showPage()
    return canvas


def draw_cell(canvas, day, rect, font, scale_factor):
    """Draw a calendar cell with the given characteristics

    @param day: The date in the range 0 to 31.
    @param rect: A Geom(x, y, width, height) tuple defining the shape of the
        cell in points.
    @param scale_factor: A number which can be used to calculate sizes which
        will remain proportional to the size of the entire calendar.
        (Currently the length of the shortest side of the full calendar)

    @type rect: C{Geom}
    @type font: C{Font}
    @type scale_factor: C{float}
    """
    # Skip drawing cells that don't correspond to a date in this month
    if not day:
        return

    margin = Size(font.size * 0.5, font.size * 1.3)

    # Draw the cell border
    canvas.rect(rect.x, rect.y - rect.height, rect.width, rect.height)

    day = str(day)
    ordinal_str = ORDINALS.get(int(day), ORDINALS[None])

    # Draw the number
    text_x = rect.x + margin.width
    text_y = rect.y - margin.height
    canvas.drawString(text_x, text_y, day)

    # Draw the lifted ordinal number suffix
    number_width = canvas.stringWidth(day, font.name, font.size)
    canvas.drawString(text_x + number_width,
                      text_y + (margin.height * 0.1),
                      ordinal_str)


async def generate_pdf(datetime_obj, outfile, size, first_weekday=calendar.MONDAY):
    """Helper to apply add_calendar_page to save a ready-to-print file to disk.

    @param datetime_obj: A Python C{datetime} object specifying the month
        the calendar should represent.
    @param outfile: The path to which to write the PDF file.
    @param size: A (width, height) tuple (specified in points) representing
        the target page size.
    """
    __author__ = "Bill Mill; Stephan Sokolow (deitarion/SSokolow)"
    __license__ = "CC0-1.0"  # https://creativecommons.org/publicdomain/zero/1.0/
    size = Size(*size)
    canvas = Canvas(outfile, size)

    # margins
    wmar, hmar = size.width / 50, size.height / 50
    size = Size(size.width - (2 * wmar), size.height - (2 * hmar))

    data = await add_calendar_page(canvas,
                                   Geom(wmar, hmar, size.width, size.height),
                                   datetime_obj,
                                   draw_cell,
                                   first_weekday)
    data.save()


async def pdf_to_png_converter(pdf_file="calendar.pdf", png_file="calendar.png"):
    try:
        pil_image_lst = convert_from_path(pdf_file)  # This returns a list even for a 1 page pdf
    except Exception as e:
        print(e)
        print(f"ERROR: sudo apt install poppler-utils")
        raise
    pil_obj = pil_image_lst[0]
    pil_obj.save(png_file, "PNG")


async def concatenate_two_png(img1, img2):
    """
    Concatenate two files moon_calendar_exp.png + calendar.png to single one

    :param img1: "/home/stastodd/projects/Raspberrypi4_projects/telegram-bot/images/background_template/moon_calendar_exp.png"
    :param img2: "/home/stastodd/projects/Raspberrypi4_projects/telegram-bot/images/out/calendar.png"
    """
    img1_obj = Image.open(img1)  # expander (head)
    img2_obj = Image.open(img2)  # main (body)
    pil_obj = Image.new('RGB', (img1_obj.width, img1_obj.height + img2_obj.height))
    pil_obj.paste(img1_obj, (0, 0))
    pil_obj.paste(img2_obj, (0, img1_obj.height))
    pil_obj.save(img2)


async def write_calendar_attributes(file, year, month, font, hemisphere="north"):
    """
    Add on the calendar.png text (year + month)

    :param file: "/home/stastodd/projects/Raspberrypi4_projects/telegram-bot/images/out/calendar.png"
    :param year: 2023
    :param month: June
    :param font: "/home/stastodd/projects/Raspberrypi4_projects/telegram-bot/images/fonts/Spartan/static/Spartan-SemiBold.ttf"
    :param hemisphere: "north" | "south"
    """
    font_size = 60
    font_obj = ImageFont.truetype(font, size=font_size)
    img_obj = Image.open(file)
    img_draw_obj = ImageDraw.Draw(img_obj)
    (x, y) = (40, 25)
    text_color = "rgb(60, 42, 33)"
    img_draw_obj.text((x, y), f"{year}, {month} [{hemisphere}]", fill=text_color, font=font_obj)
    img_obj.save(file)


async def add_layer_into_calendar(calendar_file, new_layer, coordinates):
    """
    Write new layer png images to the calendar image

    :param calendar_file: "/home/stastodd/projects/Raspberrypi4_projects/telegram-bot/images/out/calendar.png"
    :param new_layer: "/home/stastodd/projects/Raspberrypi4_projects/telegram-bot/images/moon/first_quarter_moon/icons8-first-quarter-moon-96.png"
    :param coordinates: (58, 160)
    """
    img1 = Image.open(calendar_file)
    img2 = Image.open(new_layer)
    img1.paste(img2, coordinates, img2)
    img1.save(calendar_file)


async def moonphase(work_datetime, do_print=False):
    __doc__ = """
    Using calculator from

    http://gmmentalgym.blogspot.com/2013/01/moon-phase-for-any-date.html

    which is based on Conway's moon phase algorithm from "Winning Ways for
    your Mathematical Plays, Volume 2" (1980).

    Estimate the age of the moon from 0 to 29 for a particular date
    29,30=0,1 new moon
    2-6 waxing crescent
    7-8 first quarter
    9-13 waxing gibbous
    14-16 full
    17-21 waning gibbous
    22-23 last quarter
    24-28 waning (de)crescent

    If year, month and day are not provided, input is requested.

    Handles years from 1700 to 3099.
    """

    year = work_datetime.year
    month = work_datetime.month
    day = work_datetime.day

    h = year // 100  # integer division for the century
    yy = year % 100  # year within the century

    # The "golden number" for this year is the year modulo 19, but
    # adjusted to be centered around 0 -- i.e., -9 to 9 instead
    # of 0 to 19. This improves the accuracy of the approximation
    # to within +/- 1 day.
    g = (yy + 9) % 19 - 9

    # There is an interesting 6 century near-repetition in the
    # century correction. It would be interesting to find an
    # algorithm that handles the different corrections between
    # centuries 17|23|29, 20|26, 21|27, and 24|30.
    try:
        c = {17: 7,
             18: 1, 19: -4, 20: -8, 21: 16, 22: 11, 23: 6,
             24: 1, 25: -4, 26: -9, 27: 15, 28: 11, 29: 6,
             30: 0}[h]
    except KeyError:
        print(f"No century correction available for {h}00-{h}99")
        return

    # Golden number correction: modulo 30, from -29 to 29.
    # gc = g * 11
    # while gc < -29: gc += 30;
    # if gc > 0: gc %= 30;
    gc = g * 11
    while gc < -29:
        gc += 30
        if gc > 0:
            gc %= 30

    # January/February correction:
    if month < 3:
        mc = 2
    else:
        mc = 0

    phase = (month + mc + day + gc + c + 30) % 30

    # if do_print:
    #     # It's nice to see what the Golden correction for the year
    #     # plus the century correction is. This lets us quickly calculate the
    #     # correction for any other date in the same year.
    #     gcpc = (gc + c) % 30
    #     if gcpc <= 0:
    #         gcpc_alt = gcpc + 30
    #     else:
    #         gcpc_alt = gcpc - 30
    #
    #     print("yy =", yy)
    #     print("g =", g)
    #     print("month + day + mc =", month + day + mc)
    #     print("gc =", gc)
    #     print("c =", c)
    #     print("Dates in the year", year,
    #           "have moon phase correction gc + c =",
    #           gcpc, "or", gcpc_alt)
    #     print(("\n\t{:04}/{:02}/{:02} has "
    #            "estimated moon phase = {}\n").format(year,
    #                                                  month,
    #                                                  day,
    #                                                  phase))
    #     if phase < 2:
    #         print("\tNew moon after")
    #     elif phase < 7:
    #         print("\tWaxing crescent")
    #     elif phase < 9:
    #         print("\tFirst quarter")
    #     elif phase < 14:
    #         print("\tWaxing gibbous")
    #     elif phase < 16:
    #         print("\tFull moon")
    #     elif phase < 22:
    #         print("\tWaning gibbous")
    #     elif phase < 24:
    #         print("\tLast quarter")
    #     elif phase < 29:
    #         print("\tWaning crescent")
    #     elif phase < 31:
    #         print("\tNew moon before")
    #
    #     try:
    #         # If you have the ephem package installed, you
    #         # can compare the estimate to the actual lunar phase
    #         import ephem
    #         thisdate = ephem.Date('{:04}/{:02}/{:02} 00:00:01'.format(year, month, day))
    #         prevmoon = ephem.previous_new_moon(thisdate)
    #         nextmoon = ephem.next_new_moon(thisdate)
    #         prevfull = ephem.previous_full_moon(thisdate)
    #         nextfull = ephem.next_full_moon(thisdate)
    #         prevymd = prevmoon.tuple()[:3]
    #         nextymd = nextmoon.tuple()[:3]
    #         pfymd = prevfull.tuple()[:3]
    #         nfymd = nextfull.tuple()[:3]
    #         print(f"\n\t{prevmoon}", "UTC = Previous New Moon")
    #         print(f"\t{nextmoon}", "UTC = Next New Moon")
    #         print(f"\t{prevfull}", "UTC = Previous Full Moon")
    #         print(f"\t{nextfull}", "UTC = Next Full Moon")
    #         try:
    #             from convertdate import julianday
    #             thisjdc = julianday.from_gregorian(year, month, day)
    #             prevjdc = julianday.from_gregorian(*prevymd)
    #             nextjdc = julianday.from_gregorian(*nextymd)
    #             pfjdc = julianday.from_gregorian(*pfymd)
    #             nfjdc = julianday.from_gregorian(*nfymd)
    #             print("\t{:2} days since prev new moon".format(int(thisjdc - prevjdc)))
    #             print("\t{:2} days until next new moon".format(int(nextjdc - thisjdc)))
    #             print("\t{:2} days since prev full moon".format(int(thisjdc - pfjdc)))
    #             print("\t{:2} days until next full moon".format(int(nfjdc - thisjdc)))
    #         except:
    #             print("julianday doesn't work")
    #             pass
    #     except:
    #         pass
    #
    #     try:
    #         # If you have convertdate installed, you can compare the lunar
    #         # phase to the hebrew calendar date:
    #         from convertdate import hebrew
    #         hyear, hmonth, hday = hebrew.from_gregorian(year, month, day)
    #         print(f"\n\tHebrew date = {hday} {hmonths[hmonth]}, {hyear}\n")
    #     except:
    #         pass
    return phase


async def get_moonphase_image(moonphase_number, **kwargs):
    """
    :param moonphase_number: int() | 2
    :return: str() | "/home/stastodd/projects/Raspberrypi4_projects/telegram-bot/images/moon/new_moon.png"
    """
    # Moon phases ranges:
    moon_phases = {
        "New moon after": list(range(2)),
        "Waxing crescent": list(range(2, 7)),
        "First quarter": list(range(7, 9)),
        "Waxing gibbous": list(range(9, 14)),
        "Full moon": list(range(14, 16)),
        "Waning gibbous": list(range(16, 22)),
        "Last quarter": list(range(22, 24)),
        "Waning crescent": list(range(24, 29)),
        "New moon before": list(range(29, 31)),
    }

    moon_phases_img = kwargs.get("moon_phases_img")

    moon_phase_name = str()
    for phase_name, phase_range in moon_phases.items():
        if moonphase_number in phase_range:
            moon_phase_name = phase_name
            break
    return moon_phases_img.get(moon_phase_name, str())


async def calendar_creator(calendar_path_filename, work_datetime, **kwargs):
    # calendar_path = params.get("calendar_path", "~/")
    # calendar_png_filename = f"{calendar_path}calendar.png"

    # work_datetime = params.get("datetime", datetime.datetime.now())
    work_datetime_year = work_datetime.year
    work_datetime_month = work_datetime.month
    num_days = calendar.monthrange(work_datetime_year, work_datetime_month)[1]  # 31
    all_days_objects = [datetime.date(work_datetime_year, work_datetime_month, day) for day in range(1, num_days + 1)]

    dates = calendar.monthcalendar(work_datetime_year, work_datetime_month)
    """
    dates = 
    [[0, 0, 1, 2, 3, 4, 5],
     [6, 7, 8, 9, 10, 11, 12],
     [13, 14, 15, 16, 17, 18, 19],
     [20, 21, 22, 23, 24, 25, 26],
     [27, 28, 29, 30, 0, 0, 0]]
    """

    for day_obj in all_days_objects:
        day_obj_moonphase_number = await moonphase(day_obj, do_print=False)
        moon_image = await get_moonphase_image(day_obj_moonphase_number, **kwargs)

        for line_number, line_days in enumerate(dates):
            if day_obj.day in line_days:
                day_weekday = day_obj.weekday()  # 0 - 6
                await add_layer_into_calendar(calendar_path_filename, moon_image, calendar_coordinates[f"{line_number}{day_weekday}"])
                break


async def main(requested_datetime):
    """
    :param requested_datetime: '/this_month' | '/next_month' | '2024-1'
    """
    kwargs = dict()

    # Check and requested_datetime argument:
    if requested_datetime == "/this_month":
        work_datetime = datetime.date.today()
    elif requested_datetime == "/next_month":
        work_datetime = datetime.date.today() + relativedelta.relativedelta(months=1)
    else:
        try:
            year_month = requested_datetime.split("-")  # ['2024', '1']
            work_datetime = datetime.datetime(int(year_month[0]), int(year_month[1]), 1)
        except Exception:
            work_datetime = datetime.date.today()

    # TODO: move path to the external config file
    # Handle new calendar params:
    calendar_pdf_filename = "calendar.pdf"
    calendar_path = "/home/stastodd/projects/telegram-bot/images/out/"
    calendar_png_expander = "/home/stastodd/projects/telegram-bot/images/background_template/moon_calendar_exp.png"
    text_font = "/home/stastodd/projects/telegram-bot/images/fonts/Spartan/static/Spartan-SemiBold.ttf"

    # TODO: move path to the external config file
    # Moon phases images:
    moon_phases_img = {
        "New moon after": "/home/stastodd/projects/telegram-bot/images/moon/new_moon.png",
        "Waxing crescent": "/home/stastodd/projects/telegram-bot/images/moon/waxing_crescent_moon.png",
        "First quarter": "/home/stastodd/projects/telegram-bot/images/moon/first_quarter_moon.png",
        "Waxing gibbous": "/home/stastodd/projects/telegram-bot/images/moon/waxing_gibbous_moon.png",
        "Full moon": "/home/stastodd/projects/telegram-bot/images/moon/full_moon.png",
        "Waning gibbous": "/home/stastodd/projects/telegram-bot/images/moon/waning_gibbous_moon.png",
        "Last quarter": "/home/stastodd/projects/telegram-bot/images/moon/last_quarter_moon.png",
        "Waning crescent": "/home/stastodd/projects/telegram-bot/images/moon/waning_crescent_moon.png",
        "New moon before": "/home/stastodd/projects/telegram-bot/images/moon/new_moon.png",
    }
    kwargs["moon_phases_img"] = moon_phases_img

    # If calendar file exists, just return it:
    calendar_path_filename = f"{calendar_path}{work_datetime.year}_{work_datetime.month}.png"
    if os.path.exists(calendar_path_filename):
        return calendar_path_filename

    # Create calendar.pdf:
    await generate_pdf(work_datetime,
                       f"{calendar_path}{calendar_pdf_filename}",
                       pagesizes.landscape(pagesizes.A6))

    # Create calendar.png:
    await pdf_to_png_converter(pdf_file=f"{calendar_path}{calendar_pdf_filename}", png_file=calendar_path_filename)

    # Concatenate two png images (body + header) to single one:
    await concatenate_two_png(calendar_png_expander, calendar_path_filename)

    # Write year and month names on calendar.png:
    datetime_month_name = work_datetime.strftime("%B")  # June
    datetime_year_number = work_datetime.year  # 2024
    await write_calendar_attributes(calendar_path_filename, datetime_year_number, datetime_month_name, text_font)

    # Write moon data on the png calendar:
    await calendar_creator(calendar_path_filename, work_datetime, **kwargs)

    return calendar_path_filename
