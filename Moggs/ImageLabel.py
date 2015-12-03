import glob
from PIL import Image, ImageDraw, ImageTk, ImageFont, ImageFilter, _imaging, _imagingft


def VerticalLabel(text, fontName="Arial", fontSize=10):
    
    font = fontFinder(fontName, fontSize)
    
    im = Image.new("RGB", (800, 800), (255, 255, 255))
    draw = ImageDraw.Draw(im)
    draw.text((0,0), text, fill="black", font=font)
    #~ width, height = draw.textsize(text)
    width, height = font.getsize(text)
    
    im = im.crop((0, 0, width, height))
    im = im.transpose(Image.ROTATE_90)
    return ImageTk.PhotoImage(im)

def HorizontalLabel(text, fontName="Arial", fontSize=10):
    font = fontFinder(fontName, fontSize)
    ## guess the size!
    width, height = font.getsize(text)
    im = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(im)
    draw.text((0,0), text, fill="black", font=font)
    c = cropper(im)
    return ImageTk.PhotoImage(c)


def fontFinder(fontName="Arial", size=10):
    ## should cache these for all times at start... boring though!
    for file in glob.glob("C:/Windows/Fonts/*.ttf"):
        font = ImageFont.truetype(file, size)
        name, style = font.getname()
        #~ print name, style
        if name == fontName:
            #~ print "Font found", fontName
            break
    else:
        font = ImageFont.load_default()  
        #~ print "Font not found :("
    return font



def cropper(im):
    ## slow for large images!
    pixels = im.load()
    width, height = im.size
    max_x = max_y = 0
    min_y = height
    min_x = width

    # find the corners that bound the letter by looking for
    # non-transparent pixels
    transparent = (255, 255, 255)
    for x in range(width):
        for y in range(height):
            p = pixels[x,y]
            #~ print((x,y,p))
            if p != transparent:
                min_x = min(x, min_x)
                min_y = min(y, min_y)
                max_x = max(x, max_x)
                max_y = max(y, max_y)
    cropped = im.crop((min_x, min_y, max_x+1, max_y+1))    
    return cropped


font = fontFinder("Arial")
    
    
    