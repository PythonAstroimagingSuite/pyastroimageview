#
# Image viewing area
#
# Copyright 2019 Michael Fulbright
#
#
#    pyastroimageview is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import logging
import astropy.io.fits as pyfits
import numpy as np
from PyQt5 import QtCore, QtWidgets, QtGui
import pyqtgraph as pg

from pyastroimageview.MTFStretchItem import MTFSliderItem

class StarObj(QtWidgets.QGraphicsObject):
    def __init__(self, r, num=None):
        super().__init__()
        pg.GraphicsScene.registerObject(self)
        self.r = r
        self.num = num

    def paint(self, p, *args):
        # FIXME shouldnt hard code color
        p.setPen(pg.mkPen(200, 200, 200))

        p.drawRect(self.boundingRect())

        font = p.font()
        text_zoom = p.transform().m11()  # assume aspect doesnt change!
        font_size = 12.0 / text_zoom
        final_font_size = int(max(3, font_size))
        font.setPixelSize(final_font_size)
        p.setFont(font)

        pre_bbox = QtCore.QRect(-40, min(-25, -20 / text_zoom), 80, max(50, 40/text_zoom))

        text_str = ''
        if self.num:
            text_str += f'({self.num}) - '
        text_str += f'{self.r:4.2f}'

        text_bbox = p.boundingRect(pre_bbox, QtCore.Qt.AlignTop|QtCore.Qt.AlignHCenter, text_str)

        p.drawText(text_bbox, QtCore.Qt.AlignTop|QtCore.Qt.AlignHCenter, text_str)

    def boundingRect(self):
        # make a box proportinal to HFR of star
        r_fact = 3 * self.r
        return QtCore.QRectF(-r_fact, -r_fact, 2 * r_fact, 2 * r_fact)

#    def hoverEvent(self, evt):
#        logging.info(f'hoverEvent: {evt}')

#    def mouseClickEvent(self, ev):
#        logging.info(f'starobj: mouseClickEvent: {ev}')

#class ImageWindowSTFSignals(QtCore.QObject):
#    image_mouse_click = QtCore.pyqtSignal(object)

class ImageWindowSTF(pg.GraphicsLayoutWidget):
    image_mouse_move = QtCore.Signal(int, int, float)
    image_mouse_click = QtCore.Signal(object)

    def __init__(self):
        """ Create a widget which can display a FITS image and label detected stars.
        """
        super().__init__()

        self.setBackground(pg.mkColor((32, 32, 32)))

        self.ci.layout.setSpacing(0)
        self.ci.layout.setColumnSpacing(0, 0)
        self.ci.layout.setColumnSpacing(1, 0)
        self.ci.layout.setColumnSpacing(2, 0)
        self.ci.layout.setContentsMargins(0, 0, 0, 0)

        self.view = self.addViewBox()
        self.view.setAspectLocked(True)
        self.view.invertY(True)  # flipped for some reason
        self.image_item = pg.ImageItem()
        self.image_item.setOpts(axisOrder='row-major')
        self.view.addItem(self.image_item)

        # FIXME not sure this is best way to get events!
        self.image_item.mouseClickEvent = self.image_item_mouse_click_event

        # MTF slider with gradient preview
        self.mtf_win = pg.GraphicsLayout()
#       self.mtf_win.setBorder('w')
        self.addItem(self.mtf_win)
        self.mtf_win.setContentsMargins(0, 0, 0, 0)

        # compute gradient - make it 1000x100 pixel
        self.mtf_slider_win = pg.GraphicsLayout()
        self.mtf_slider_win.setBorder('w')
        self.mtf_win.addItem(self.mtf_slider_win)
        gradient_image = np.tile(np.arange(0, 65535, 65535.0 / 1000), [100, 1])
        self.gradient_view = self.addViewBox()
        self.gradient_image_item = pg.ImageItem()
        self.gradient_image_item.setImage(gradient_image, autoLevels=False,
                                          levels=(0, 65535))
        self.gradient_view.addItem(self.gradient_image_item)
        self.mtf_slider_win.addItem(self.gradient_view)
        # magic to keep gradient image nice and thin
        self.mtf_slider_win.layout.setColumnMaximumWidth(0, 15)

        self.stf_slider = STFSlider(orientation='right', allowAdd=False)
        self.stf_slider.slider_changed.connect(self.stf_slider_changed)
        self.mtf_win.addItem(self.stf_slider)

        self.mtf_slider_win.layout.setSpacing(0)
        self.mtf_slider_win.layout.setColumnSpacing(0, 0)
        self.mtf_slider_win.layout.setRowSpacing(0, 0)

        self.mtf_win.layout.setSpacing(0)
        self.mtf_win.layout.setColumnSpacing(0, 0)
        self.mtf_win.layout.setRowSpacing(0, 0)

        proxy = QtGui.QGraphicsProxyWidget()
        button = QtGui.QPushButton('Auto')
        button.pressed.connect(self.auto_stretch_button_cb)
        button.setMaximumWidth(40)
        proxy.setWidget(button)
        self.mtf_win.nextRow()
        self.mtf_win.addItem(proxy, colspan=2)

        # FIXME need to remove? It was mostly for debugging
#        self.lut_plot = pg.PlotWindow()
#        self.lut_plot.win.hide()

        self.star_items = []
        self.star_visibility = True
        self.image_data = None

        # follow mouse position
        self.mouse_proxy = pg.SignalProxy(self.image_item.scene().sigMouseMoved,
                                          rateLimit=60,
                                          slot=self.image_item_mouse_moved_event)

    def image_item_mouse_moved_event(self, evt):
        pos = evt[0]  # using signal proxy turns original arguments into a tuple
#        logging.info(f'mouse_moved: {mousePoint.x()}, {mousePoint.y()}')

        if self.image_item.sceneBoundingRect().contains(pos):
            mousePoint = self.view.mapSceneToView(pos)

            if self.image_data is not None:
                x = int(mousePoint.x())
                y = int(mousePoint.y())
                val = float(self.image_data[y][x])
            self.image_mouse_move.emit(x, y, val)

    def image_item_mouse_click_event(self, ev):
        #logging.info(f'image_item_mouse_click_event: {ev}')
        self.image_mouse_click.emit(ev)

    def auto_stretch_button_cb(self):
        self.auto_stretch()

    def stf_slider_changed(self, sc, mc, hc):
        logging.info(f'stf_slider_changed: {sc} {mc} {hc}')

        self.set_mtf(sc, mc, hc)

    def show_image(self, image_file):
        """Load the fits file and display it

        Parameters
        ----------
        image_file : str
        Filename of FITS file.
        """

        logging.debug(f'show_image: {image_file}')
        logging.debug('Removing star obj')

        # remove any existing star labels
        for item in self.star_items:
            self.view.removeItem(item)

        self.star_items = []

        logging.debug('loading fits file')

        self.image_data = pyfits.getdata(image_file)

        logging.debug('setting image data')

        self.image_item.setImage(self.image_data, autoLevels=False,
                                 levels=(0, 65535), autoRange=False)

    def show_data(self, image_data):
        # remove any existing star labels
        for item in self.star_items:
            self.view.removeItem(item)

        self.star_items = []

        self.image_data = image_data

#        logging.info(f'show_data shape = {image_data.shape}')

        self.image_item.setImage(self.image_data, autoLevels=False,
                                 levels=(0, 65535), autoRange=False)

    def set_mtf(self, sc, mc, hc):
        """ Computes and applies LUT for image based on sc, mc, hc.

        Must have sc < hc.

        mc is defined to be from 0 to 1 and acts as a 'gamma' adjustment.

        Parameters
        ----------
        sc : float
            Shadow cutoff (0-1)
        mc : float
            Midtone (0-1)
        hc : float
            Highlights cutoff (0-1)
        """

        def compute_mtf(x, sc, mc, hc):
            if x < sc:
                return 0.0
            elif x > hc:
                return 1.0
            else:
                y = (x - sc) / (hc - sc)
                a = ((mc - 1.0) * y)
                b = ((2.0 * mc - 1.0) * y - mc)
                r = a / b
                v = r
                return v

        logging.debug(f'set_mtf: {sc} {mc} {hc}')

        lut = []
        for x in np.arange(0, 1, 1 / 65535):
            val = min(255, 255 * compute_mtf(x, sc, mc, hc))
            lut.append(int(val))

        if lut[-1] < 255:
            lut.append(255)

        if lut[0] != 0:
            lut = [0] + lut

        lut = np.array(lut)
        color_lut = np.vstack((lut, lut, lut)).T
        self.image_item.setLookupTable(color_lut)
        self.gradient_image_item.setLookupTable(color_lut)

    def get_autostretch_values(self):
        """Based on http://pixinsight.com/doc/docs/XISF-1.0-spec/XISF-1.0-spec.html#__XISF_Data_Objects_:_XISF_Image_:_Adaptive_Display_Function_Algorithm__"""

        def compute_mtf(x, m):
            return ((m - 1.0) * x) / ((2.0 * m - 1.0) * x - m)

        # normalize image
        norm_image = self.image_data / 65535.0

        image_median = np.median(norm_image)

        # eq 24
        mad = 1.4826 * np.median(np.abs(norm_image - image_median))

        # clipping pt
        clip_pt = -2.8
        target_bg = 0.25

        logging.debug(f'autostretch: med={image_median} mad={mad}')

        if image_median < 0.5:
            ac = 0
        else:
            ac = 1

        if ac == 1 or mad < 1e-6:
            sc = 0
        else:
            sc = min(1.0, max(0, image_median + clip_pt * mad))

        if ac == 0 or mad < 1e-6:
            hc = 1
        else:
            hc = min(1.0, max(0, image_median - clip_pt * mad))

        if ac == 0:
            mc = compute_mtf(image_median - sc, target_bg)
        else:
            mc = compute_mtf(target_bg, hc - image_median)

        logging.debug(f'autostretch: clip_pt={clip_pt} target_bg={target_bg} '
                      f'ac={ac} sc={sc} hc={hc} mc={mc}')

        return (sc, mc, hc)

    def auto_stretch(self):
        sc, mc, hc = self.get_autostretch_values()
        self.set_mtf(sc, mc, hc)
        self.stf_slider.setSTFValues(sc, mc, hc)

    def overlay_stars(self, hfr_result, filter=False):
        """Overlay star labels onto image.

        Given a MeasureHFRResult this method will label each with an index
        number and its HFR value as well as a small square proportional to the
        HFR value.

        Parameters
        ----------
        hfr_result : MultipleStarFitHFD.StarFitResult
            Result from star detection routine.
        filter : bool
            If True then restrict to values near median of HFR to reject invalid star detections.
        """

        if filter:
            min_cut = np.percentile(hfr_result.star_r, 5)
            max_cut = np.percentile(hfr_result.star_r, 90)
        else:
            min_cut = 0.0
            max_cut = np.inf

        logging.info(f'overlay_stars min_cut={min_cut} max_cut={max_cut}')
        logging.info(f'overlay_stars; min_hfr = {np.min(hfr_result.star_r)} '
                     f'max_hfr={np.max(hfr_result.star_r)}')

        idx = range(1, len(hfr_result.star_cx) + 1)
        ndrawn = 0
        for i, x, y, r in zip(idx, hfr_result.star_cx, hfr_result.star_cy, hfr_result.star_r):
#            logging.info(f'Star #{i} x/r/r -> {x}, {y}, {r}')

#            text = pg.TextItem(f'{r:3.2f}', anchor=(0.5,2.0), border='r')
#            text.setZValue(100)
#            text.setPos(x, y)
            if max_cut > r > min_cut:
                star_item = StarObj(r) # add this to get each star numbered for debugging! -> ", num=i)"
                star_item.setPos(x, y)
                star_item.setVisible(self.star_visibility)
                self.view.addItem(star_item)
                self.star_items.append(star_item)
                ndrawn += 1

        logging.info(f'overlay_stars: drew {ndrawn} stars.')

        # need to force repaint?  Otherwise text doesn't seem to be displayed
        # reliably until a mouse enter event.
        self.repaint()

    def set_stars_visibility(self, state):
        for s in self.star_items:
            s.setVisible(state)
        self.repaint()
        self.star_visibility = state

    def get_stars_visibility(self):
        return self.star_visibility

class STFSlider(MTFSliderItem):
    slider_changed = QtCore.pyqtSignal(float, float, float)
    """ sends sc, mc, hc """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.tick_white = self.addTick(1.0, color=pg.mkColor(255, 255, 255),
                                       removable=False)
        self.tick_mid = self.addTick(0.5, color=pg.mkColor(128, 128, 128),
                                     removable=False)
        self.tick_black = self.addTick(0.0, color=pg.mkColor(0, 0, 0),
                                       removable=False)

        # make sure we can move mid
        self.tick_mid.setZValue(10)

        # keep up with midpt independently
        self.midtone = 0.5

    def updateGradient(self):
        pass

    def setTickValues(self, black, mid, white):
        logging.info(f'setTickValues: {black} {mid} {white}')

        self.setTickValue(self.tick_black, black)
        self.setTickValue(self.tick_mid, mid)
        self.setTickValue(self.tick_white, white)

    def setSTFValues(self, sc, mc, hc):
        """ Convert sc, mc, hc to slider values

        The black/mid/white sliders in the STFSlider do not map directly to
        STF variables.  The mid slider position is related to sc, hc and mc.

        mid_slider_value = sc + (hc-sc)*mc

        """

        self.midtone = mc
        black = sc
        white = hc
        mid = sc + (hc - sc) * mc

        self.setTickValues(black, mid, white)

    def tickMoveFinished(self, tick):
        black = self.tickValue(self.tick_black)
        mid = self.tickValue(self.tick_mid)
        white = self.tickValue(self.tick_white)

        logging.info(f'tickmovefinished: raw tick values -> {black} {mid} {white}')

        if tick is self.tick_black:
            if black > white:
                black = white
        elif tick is self.tick_white:
            if white < black:
                white = black
        elif tick is self.tick_mid:
            if mid < black:
                mid = black
            elif mid > white:
                mid = white

            self.midtone = (mid - black) * (white - black)

        # if mid wasnt move then adjust to new position of either black or white
        if tick is not self.tick_mid:
            mid = black + self.midtone * (white - black)

        logging.info(f'tickmovefinished: corrected tick values -> '
                     f'{black} {mid} {white}')
        logging.info(f'tickmovefinished: midpt = {self.midtone}')

        # reflect adjusted values in sliders
        self.setTickValues(black, mid, white)

        # send 'STF' values out
        self.slider_changed.emit(black, self.midtone, white)


if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)

    app = QtGui.QApplication([])

    imgwin = ImageWindowSTF()
    imgwin.show_image('test3.fits')

    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

    logging.error("DONE")
