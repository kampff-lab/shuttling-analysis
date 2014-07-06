# Copyright: Luis Pedro Coelho <luis@luispedro.org>, 2012
# License: MIT
import numpy as np

def read_roi(fileobj):
    '''
    points = read_roi(fileobj)

    Read ImageJ's ROI format
    '''
# This is based on:
# http://rsbweb.nih.gov/ij/developer/source/ij/io/RoiDecoder.java.html
# http://rsbweb.nih.gov/ij/developer/source/ij/io/RoiEncoder.java.html
    # offsets
    VERSION_OFFSET = 4
    TYPE = 6
    TOP = 8
    LEFT = 10
    BOTTOM = 12
    RIGHT = 14
    N_COORDINATES = 16
    X1 = 18
    Y1 = 22
    X2 = 26
    Y2 = 30
    XD = 18
    YD = 22
    WIDTHD = 26
    HEIGHTD = 30
    STROKE_WIDTH = 34
    SHAPE_ROI_SIZE = 36
    STROKE_COLOR = 40
    FILL_COLOR = 44
    SUBTYPE = 48
    OPTIONS = 50
    ARROW_STYLE = 52
    ELLIPSE_ASPECT_RATIO = 52
    ARROW_HEAD_SIZE = 53
    ROUNDED_RECT_ARC_SIZE = 54
    POSITION = 56
    HEADER2_OFFSET = 60
    COORDINATES = 64
    # header2 offsets
    C_POSITION = 4
    Z_POSITION = 8
    T_POSITION = 12
    NAME_OFFSET = 16
    NAME_LENGTH = 20
    OVERLAY_LABEL_COLOR = 24
    OVERLAY_FONT_SIZE = 28 #short
    AVAILABLE_BYTE1 = 30  #byte
    IMAGE_OPACITY = 31  #byte
    IMAGE_SIZE = 32  #int
    FLOAT_STROKE_WIDTH = 36  #float
        
    # subtypes
    TEXT = 1
    ARROW = 2
    ELLIPSE = 3
    IMAGE = 4
    
    # options
    SPLINE_FIT = 1
    DOUBLE_HEADED = 2
    OUTLINE = 4
    OVERLAY_LABELS = 8
    OVERLAY_NAMES = 16
    OVERLAY_BACKGROUNDS = 32
    OVERLAY_BOLD = 64
    SUB_PIXEL_RESOLUTION = 128
    DRAW_OFFSET = 256    
    
    
    HEADER2_OFFSET = 60

    SPLINE_FIT = 1
    DOUBLE_HEADED = 2
    OUTLINE = 4
    OVERLAY_LABELS = 8
    OVERLAY_NAMES = 16
    OVERLAY_BACKGROUNDS = 32
    OVERLAY_BOLD = 64
    SUB_PIXEL_RESOLUTION = 128
    DRAW_OFFSET = 256
    
    data = bytearray(fileobj.read())

    pos = [4]
    def get8(base):
        return data[base]&255

    def get16(base):
        b0 = get8(base)
        b1 = get8(base+1)
        return (b0 << 8) | b1

    def get32(base):
        s0 = get16(base)
        s1 = get16(base+2)
        return (s0 << 16) | s1

    def getfloat(base):
        v = np.int32(get32(base))
        return v.view(np.float32)

    #magic = fileobj.read(4)
    if get8(0) != 73 or get8(1) != 111: #'Iout':
        raise IOError('Magic number not found')
    version = get16(VERSION_OFFSET)

    # It seems that the roi type field occupies 2 Bytes, but only one is used
    roi_type = get8(TYPE)
    # Discard second Byte:
    #get8()

    if not (0 <= roi_type < 11):
        raise ValueError('roireader: ROI type %s not supported' % roi_type)

    if roi_type != 0:
        raise ValueError('roireader: ROI type %s not supported (!= 7)' % roi_type)

    top = get16(TOP)
    left = get16(LEFT)
    bottom = get16(BOTTOM)
    right = get16(RIGHT)
    n_coordinates = get16(N_COORDINATES)

    x1 = getfloat(X1) 
    y1 = getfloat(Y1) 
    x2 = getfloat(X2) 
    y2 = getfloat(Y2)
    stroke_width = get16(STROKE_WIDTH)
    shape_roi_size = get32(SHAPE_ROI_SIZE)
    stroke_color = get32(STROKE_COLOR)
    fill_color = get32(FILL_COLOR)
    subtype = get16(SUBTYPE)
    if subtype != 0:
        raise ValueError('roireader: ROI subtype %s not supported (!= 0)' % subtype)
    options = get16(OPTIONS)
    arrow_style = get8(ARROW_STYLE)
    arrow_head_size = get8(ARROW_HEAD_SIZE)
    rect_arc_size = get16(ROUNDED_RECT_ARC_SIZE)
    position = get32(POSITION)
    header2offset = get32(HEADER2_OFFSET)

    if options & SUB_PIXEL_RESOLUTION:
        getc = getfloat
        pointsize = 1
        points = np.empty((n_coordinates, 2), dtype=np.float32)
    else:
        getc = get16
        pointsize = 2
        points = np.empty((n_coordinates, 2), dtype=np.int16)
    points[:,1] = [getc(COORDINATES+i*pointsize) for i in xrange(n_coordinates)]
    points[:,0] = [getc(COORDINATES+i*pointsize) for i in xrange(n_coordinates)]
    points[:,1] += left
    points[:,0] += top
    points -= 1
    return points

def read_roi_zip(fname):
    import zipfile
    with zipfile.ZipFile(fname) as zf:
        return [read_roi(zf.open(n))
                    for n in zf.namelist()]