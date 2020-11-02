#
# Display image information
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
import numpy as np
import logging

import pyqtgraph as pg

from PyQt5 import QtCore, QtWidgets, QtGui

from pyastroimageview.uic.imagearea_info_uic import Ui_Form

class ImageAreaInfo(QtWidgets.QWidget):
    view_changed = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()
        #uic.loadUi('../resources/pyastroimage_imagearea_5.ui', self)

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # for now hide binning info!
        self.ui.image_bin_label_label.hide()
        self.ui.image_bin_label.hide()

        # map image_tabs signal to a 'view' model
        self.ui.image_tabs.currentChanged.connect(self.view_changed)

        # create histogram plot for hfr values
        plot_width = 200
        self.ui.hfr_histogram = pg.PlotWidget()
        self.ui.hfr_histogram.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.ui.hfr_histogram.setMinimumSize(plot_width, 125)
        self.ui.hfr_histogram.setMaximumSize(plot_width, 125)
        self.ui.hfr_histogram.plotItem.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.ui.hfr_histogram.plotItem.setMinimumSize(plot_width, 125)
        self.ui.hfr_histogram.plotItem.setMaximumSize(plot_width, 125)
        self.ui.hfr_histogram.plotItem.setContentsMargins(5, 10, 10, 0)
        self.ui.hfr_histogram.plotItem.getAxis('left').setWidth(20)
        self.ui.hfr_histogram.plotItem.getAxis('left').setLabel('#')
        self.ui.hfr_histogram.plotItem.getAxis('bottom').setLabel('HFR')
        self.ui.hfr_histogram.plotItem.plot([0, 1], [0, 1])
        self.ui.hfr_histogram_spot.addWidget(self.ui.hfr_histogram)

        self.ui.pixel_histogram = pg.PlotWidget()
        self.ui.pixel_histogram.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.ui.pixel_histogram.setMinimumSize(plot_width, 125)
        self.ui.pixel_histogram.setMaximumSize(plot_width, 125)
        self.ui.pixel_histogram.plotItem.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.ui.pixel_histogram.plotItem.setMinimumSize(plot_width, 125)
        self.ui.pixel_histogram.plotItem.setMaximumSize(plot_width, 125)
        self.ui.pixel_histogram.plotItem.setContentsMargins(5, 10, 10, 0)
        self.ui.pixel_histogram.plotItem.getAxis('left').setWidth(20)
        self.ui.pixel_histogram.plotItem.getAxis('left').setLabel('#')
        self.ui.pixel_histogram.plotItem.getAxis('bottom').setLabel('Value')
        self.ui.pixel_histogram.plotItem.plot([0, 1], [0, 1])
        self.ui.pixel_histogram_spot.addWidget(self.ui.pixel_histogram)

    def clear_info(self):
        self.ui.hfr_in_label.setText('')
        self.ui.hfr_out_label.setText('')
        self.ui.number_stars_label.setText('')
        self.ui.image_median_label.setText('')
        self.ui.image_size_label.setText('')
        self.ui.image_bin_label.setText('')
        self.ui.hfr_histogram.plotItem.clear()
        self.ui.pixel_histogram.plotItem.clear()

    def update_info(self, image_doc):
        """ Update fields in image info area based on info supplied.

        Any parameters passed as None are ignored.

        The values from hfr_result will override size and median.

        Parameters:
            size : 2 tuple of int
                Tuple containing int (width, height) of image
            binning : int
                Binning of image (X/Y assumed the same!)
            median : float
                Median of image
            hfr_result : MeasureHFRResult
                Result from hfr measurement on frame
        """

        self.ui.image_size_label.setText(f'{image_doc.image_data.shape[1]} x '
                                         f'{image_doc.image_data.shape[0]}')

#        if binning:
#            self.image_bin_label.setText(f'{binning}')
        logging.debug('update_info: START')

        self.ui.image_median_label.setText(f'{image_doc.median:6.1f}')

        if image_doc.hfr_result:
            self.ui.hfr_in_label.setText(f'{np.median(image_doc.hfr_result.star_r):4.2f}')
            #self.ui.hfr_out_label.setText(f'{image_doc.hfr_result.hfr_out:4.2f}')
            self.ui.number_stars_label.setText(f'{image_doc.hfr_result.nstars}')
            #self.ui.image_median_label.setText(f'{image_doc.hfr_result.bgest:6.1f}')
            self.ui.image_size_label.setText(f'{image_doc.hfr_result.width} x '
                                             f'{image_doc.hfr_result.height}')

            # update histogram plot
            logging.debug('update_info: Start hist calc')
            max_star_r = np.max(image_doc.hfr_result.star_r*2)
            hy, hx = np.histogram(image_doc.hfr_result.star_r,
                                  range=(0, max_star_r))
            logging.debug('update_info: End hist calc')
            self.ui.hfr_histogram.plotItem.clear()
            #self.hfr_histogram.plotItem.setLogMode(x=True)
            self.ui.hfr_histogram.plotItem.vb.setXRange(0, max_star_r)
            logging.debug('update_info: Start hist plot')
            curve = pg.PlotCurveItem(hx, hy, stepMode=True, fillLevel=0, brush=(0, 0, 255, 80))
            self.ui.hfr_histogram.plotItem.addItem(curve)
            self.ui.hfr_histogram.autoRange()
            logging.debug('update_info: End hist plotc')

        if image_doc.image_data is not None:
            logging.info('update_info: Start perc calc')

            # subsample to speed up calcs
            sub_image_data = image_doc.image_data[1::2, 1::2]

            logging.info(f'image_data.shape = {image_doc.image_data.shape} sub_image_data.shape={sub_image_data.shape}')

            # plot between 0 and 99 percentile
            if not hasattr(image_doc, 'perc01'):
                image_doc.perc01 = np.percentile(sub_image_data, 1)
            if not hasattr(image_doc, 'perc99'):
                image_doc.perc99 = np.percentile(sub_image_data, 99)
            logging.info('update_info: End perc calc')

            py, px = np.histogram(sub_image_data, range=(image_doc.perc01, image_doc.perc99), bins=100)
            self.ui.pixel_histogram.plotItem.clear()
            curve = pg.PlotCurveItem(px, py, stepMode=True, fillLevel=0, brush=(0, 0, 255, 80))
            self.ui.pixel_histogram.plotItem.addItem(curve)
            infline = pg.InfiniteLine(pos=image_doc.median, angle=90)
            self.ui.pixel_histogram.plotItem.addItem(infline)
            self.ui.pixel_histogram.autoRange()

        logging.debug('update_info: DONE')

    # lets hide implementation of views
    def add_view(self, image_widget, name):
        """Add image_widget to a view with associated name and return index for view
        """
        return self.ui.image_tabs.addTab(image_widget, name)

    def get_current_view_index(self):
        """Return index of currently visible view
        """
        return self.ui.image_tabs.currentIndex()

    def set_current_view_index(self, idx):
        """Sets view with given index to be visible
        """
        self.ui.image_tabs.setCurrentIndex(idx)

    def get_current_view_widget(self):
        return self.ui.image_tabs.currentWidget()

    def set_current_view_widget(self, widget):
        self.ui.image_tabs.setCurrentWidget(widget)

    def find_view_index(self, name):
        """Find view with matching name
        """
        ntabs = self.ui.image_tabs.count()
        for tidx in range(0, ntabs):
            if self.ui.image_tabs.tabText(tidx) == name:
                tab_index = tidx
                break
        else:
            tab_index = None

        return tab_index

    def find_view_widget(self, name):
        """Find view with matching name
        """
        ntabs = self.ui.image_tabs.count()
        for tidx in range(0, ntabs):
            if self.ui.image_tabs.tabText(tidx) == name:
                tab_widget = self.ui.image_tabs.widget(tidx)
                break
        else:
            tab_widget = None

        return tab_widget

    def find_index_widget(self, widget):
        ntabs = self.ui.image_tabs.count()
        for tidx in range(0, ntabs):
            if self.ui.image_tabs.widget(tidx) == widget:
                tab_index = tidx
                break
        else:
            tab_index = None

        return tab_index
