#!@PYTHON@
"""
Created on September 9, 2016
@author: Mikhail Dubrovin
Class GUViewHist is a QWidget for interactive image.

Usage ::

   Emits signals
   -------------
   'axes_limits_changed(float,float,float,float)'
   'statistics_updated(float,float,float,float,float,float,float,float,float)'
   'mean_std_updated(float,float)'
   'cursor_bin_changed(float,float,float,float)'
    w.connect_histogram_updated_to(w.test_histogram_updated_reception)
    #w.disconnect_histogram_updated_from(w.test_histogram_updated_reception)
"""

#import os
#import math
#import math
from math import floor
from graphqt.GUViewAxes import *
from pyimgalgos.HBins import HBins
import numpy as np
import math

#------------------------------

def image_to_hist_arr(arr) :
    
    amin, amax = math.floor(arr.min()), math.ceil(arr.max())
    #mean, std = arr.mean(), arr.std()
    #amin, amax = mean-2*std, mean+10*std
    nbins = int(amax-amin)

    NBINS_MAX = (1<<15) - 1

    print 'XXX:NBINS_MAX', NBINS_MAX
    
    if nbins>NBINS_MAX : nbins=NBINS_MAX

    #print 'XXX arr.shape:\n', arr.shape
    #print 'XXX amin, amax, nbins:\n', amin, amax, nbins
    #print 'XXX arr.mean(), arr.std():\n', arr.mean(), arr.std()

    hb = HBins((amin,amax), nbins)
    values = hb.bin_count(arr)

    return amin, amax, nbins, values

#------------------------------

class GUViewHist(GUViewAxes) :
    
    def __init__(self, parent=None, rectax=QtCore.QRectF(0, 0, 1, 1), origin='DL', scale_ctl='HV', rulers='TBLR',\
                 margl=None, margr=None, margt=None, margb=None) :

        #xmin, xmax = np.amin(x), np.amax(x) 
        #ymin, ymax = np.amin(y), np.amax(y) 
        #w, h = xmax-xmin, ymax-ymin

        GUViewAxes.__init__(self, parent, rectax, origin, scale_ctl, rulers, margl, margr, margt, margb)

        self._name = self.__class__.__name__

        self.countemit = 0
        self.ibin_old = None
        
        self.do_cursor_scope = True
        if self.do_cursor_scope : self._init_cursor_scope()

        self.lst_items = []
        self.lst_hbins = []

        #self.connect_mean_std_updated_to(self.test_hist_mean_std_updated_reception)
        #self.disconnect_mean_std_updated_from(self.test_hist_mean_std_updated_reception)

        #self.connect_statistics_updated_to(self.test_statistics_std_reception)
        #self.disconnect_statistics_updated_from(self.test_statistics_std_reception)

        self.connect_axes_limits_changed_to(self.on_axes_limits_changed)
        #self.disconnect_axes_limits_changed_from(self.on_axes_limits_changed)


    def _init_cursor_scope(self) :
        self.pen1=QtGui.QPen(Qt.white, 0, Qt.DashLine)
        self.pen2=QtGui.QPen(Qt.black, 0, Qt.DashLine)
        #pen1.setCosmetic(True)
        #pen2.setCosmetic(True)

        ptrn = [10,10]
        self.pen1.setDashPattern(ptrn)
        self.pen2.setDashPattern(ptrn)
        #print 'pen1.dashPattern()', self.pen1.dashPattern()
        self.pen2.setDashOffset(ptrn[0])
        self.cline1i = self.scene().addLine(QtCore.QLineF(), self.pen1)
        self.cline2i = self.scene().addLine(QtCore.QLineF(), self.pen2)
        self.cline1i.setZValue(10)
        self.cline2i.setZValue(10)


    def set_style(self) :
        GUViewAxes.set_style(self)
        self.setWindowTitle("GUViewHist")
        #w.setContentsMargins(-9,-9,-9,-9)
        #self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint)
        #self.setAttribute(Qt.WA_TranslucentBackground)


#    def display_pixel_pos(self, e):
#        p = self.mapToScene(e.pos())
#        ix, iy = floor(p.x()), floor(p.y())
#        v = None
#        if ix<0\
#        or iy<0\
#        or ix>arr.shape[0]-1\
#        or iy>arr.shape[1]-1 : pass
#        else : v = self.arr[ix,iy]
#        vstr = 'None' if v is None else '%.1f' % v 
#        #print 'mouseMoveEvent, current point: ', e.x(), e.y(), ' on scene: %.1f  %.1f' % (p.x(), p.y()) 
#        self.setWindowTitle('GUViewHist x=%d y=%d v=%s' % (ix, iy, vstr))
#        #return ix, iy, v


    def set_limits(self):
        '''Set vertical limits on histogram image in the current axes rect
        '''
        rax = self.rectax
        x1, x2 = rax.left(),   rax.right()
        y1, y2 = rax.bottom(), rax.top()

        #print 'ax x1, x2, y1, y2:', x1, x2, y1, y2

        ymin, ymax = None, None

        for hb in self.lst_hbins :
            i1,i2 = hb.bin_indexes((x1,x2))
            hmin = hb.values[i1] if i1==i2 else hb.values[i1:i2].min()            
            hmax = hb.values[i1] if i1==i2 else hb.values[i1:i2].max()
            ymin = hmin #if ymin is None else min(hmin,ymin) 
            ymax = hmax + 0.12*(hmax-hmin) #if ymax is None else max(hmax,ymax) 
            #print hb.values

        #print 'i1, i2, hmin, hmax:', i1, i2, hmin, hmax
        #self._ymin = ymin*1.4 if ymin<0 else 0
        ##self._ymin = 0
        #self._ymax = ymax*1.1 if ymax>0 else 0 

        if ymax == ymin : ymax = ymin+1
        #print 'XXX:  ymin, ymax', ymin, ymax

        ml, mr, mt, mb = self.margl, self.margr, self.margt, self.margb
        hsc = (ymax-ymin)/(1 - mt - mb)
        #self._ymin = -hsc*mb # ymin-hsc*mb if ymin<0 else -hsc*mb
        self._ymin = ymin-hsc*mb if ymin<0 else -hsc*mb
        self._ymax = ymax+hsc*mt if ymax>0 else  hsc*mt

        self.evaluate_hist_mean_std()

#------------------------------

    def visible_hist_vce(self, ihis=0):
        '''Returns arrays of values, bin centers, and edges for visible part of the hystogram
        '''
        rax = self.rectax
        x1, x2 = rax.left(),   rax.right()
        y1, y2 = rax.bottom(), rax.top()

        #print 'ax x1, x2, y1, y2:', x1, x2, y1, y2
        if len(self.lst_hbins) < ihis+1 : return None

        hb = self.lst_hbins[ihis]
        i1,i2 = hb.bin_indexes((x1,x2))
        if i1 == i2 :
            if i2<hb.nbins()-1 : i2+=1
            else               : i1-=1
        
        values  = hb.values[i1:i2]
        centers = hb.bincenters()[i1:i2]
        edges   = hb.binedges()[i1:i2+1] 

        #print 'XXX: i1,i2', i1,i2
        #print 'XXX: values', values
        #print 'XXX: edges', edges

        return values, centers, edges


    def visible_hist_stat(self, ihis=0):
        '''Returns statistical parameters of visible part of the hystogram
        '''
        from graphqt.GUUtils import proc_stat

        values, centers, edges = self.visible_hist_vce(ihis)

        mean, rms, err_mean, err_rms, neff, skew, kurt, err_err, sum_w = proc_stat(values,edges)
        return mean, rms, err_mean, err_rms, neff, skew, kurt, err_err, sum_w


    def visible_hist_mean_std(self, ihis=0):
        '''Returns mean and std for visible part of the histogram
        '''
        from graphqt.GUUtils import proc_stat_v2

        values, centers, edges = self.visible_hist_vce(ihis)
        mean, std = proc_stat_v2(values, centers)
        return mean, std

#------------------------------

    def on_axes_limits_changed(self, x1, x2, y1, y2):
        #print 'GUViewHist.on_axes_limits_changed  x1: %.2f  x2: %.2f  y1: %.2f  y2: %.2f' % (x1, x2, y1, y2)      
        self.evaluate_hist_statistics()

#------------------------------

    def evaluate_hist_statistics(self):
        """Evaluates histogram statistical parameters and emits them with signal"""
        mean, rms, err_mean, err_rms, neff, skew, kurt, err_err, sum_w = self.visible_hist_stat()
        #self.test_statistics_std_reception(mean, rms, err_mean, err_rms, neff, skew, kurt, err_err, sum_w)
        self.emit(QtCore.SIGNAL('statistics_updated(float,float,float,float,float,float,float,float,float)'),\
                  mean, rms, err_mean, err_rms, neff, skew, kurt, err_err, sum_w)

    def connect_statistics_updated_to(self, recip) :
        self.connect(self, QtCore.SIGNAL('statistics_updated(float,float,float,float,float,float,float,float,float)'), recip)

    def disconnect_statistics_updated_from(self, recip) :
        self.disconnect(self, QtCore.SIGNAL('statistics_updated(float,float,float,float,float,float,float,float,float)'), recip)

    def test_statistics_std_reception(self, mean, rms, err_mean, err_rms, neff, skew, kurt, err_err, sum_w) :
        print 'GUViewHist.test_statistics_std_reception: ',\
              'mean, rms, err_mean, err_rms, neff, skew, kurt, err_err, sum_w\n',\
               mean, rms, err_mean, err_rms, neff, skew, kurt, err_err, sum_w

#------------------------------

    def evaluate_hist_mean_std(self):
        """Evaluates histogram mean and std (standard deviation) and emits them with signal"""
        mean, rms = self.visible_hist_mean_std()
        self.countemit+=1
        #print '%5d  mean: %.2f  rms: %.2f' % (self.countemit, mean, rms)
        self.emit(QtCore.SIGNAL('mean_std_updated(float,float)'), mean, rms)

    def connect_mean_std_updated_to(self, recip) :
        self.connect(self, QtCore.SIGNAL('mean_std_updated(float,float)'), recip)

    def disconnect_mean_std_updated_from(self, recip) :
        self.disconnect(self, QtCore.SIGNAL('mean_std_updated(float,float)'), recip)

    def test_hist_mean_std_updated_reception(self, mean, rms) :
        print 'GUViewHist.test_hist_mean_std_updated_reception mean: %.2f  rms: %.2f' % (mean, rms)

#------------------------------

    def hist_bin_value(self, x, ihis=0):
        '''Returns arrays of values, bin centers, and edges for visible part of the hystogram
        '''
        if len(self.lst_hbins) < ihis+1 : return None
        hb = self.lst_hbins[ihis]
        ind = hb.bin_index(x)
        return ind, hb.values[ind]

#------------------------------
 
    def mouseReleaseEvent(self, e):
        GUViewAxes.mouseReleaseEvent(self, e)
        #print 'GUViewHist.mouseReleaseEvent'

#------------------------------
 
    def closeEvent(self, e):
        #print 'GUViewHist.closeEvent'
        self.lst_items = []
        self.lst_hbins = []
        GUViewAxes.closeEvent(self, e)
        #print '%s.closeEvent' % self._name

#------------------------------

    def mouseMoveEvent(self, e):
        GUViewAxes.mouseMoveEvent(self, e) # calls display_pixel_pos(e)

        if self.do_cursor_scope : 
            p = self.mapToScene(e.pos())
            x, y = p.x(), p.y()
            if x<self.rectax.left() : return
            y1, y2 = self.rectax.bottom(), self.rectax.top()
            self.cline1i.setLine(x, y1, x, y2)
            self.cline2i.setLine(x, y1, x, y2)
            
            ibin, val = self.hist_bin_value(x)
            if ibin != self.ibin_old :
                #print 'x, ibin, val', x, ibin, val
                self.ibin_old = ibin
                self.emit(QtCore.SIGNAL('cursor_bin_changed(float,float,float,float)'), x, y, ibin, val)
               
        if self.pos_click is None : return
        self.set_limits()

    def connect_cursor_bin_changed_to(self, recip) :
        self.connect(self, QtCore.SIGNAL('cursor_bin_changed(float,float,float,float)'), recip)

    def disconnect_cursor_bin_changed_from(self, recip) :
        self.disconnect(self, QtCore.SIGNAL('cursor_bin_changed(float,float,float,float)'), recip)

#------------------------------

    def wheelEvent(self, e) :
        GUViewAxes.wheelEvent(self, e)
        self.set_limits()


    def enterEvent(self, e) :
    #    print 'enterEvent'
        GUViewAxes.enterEvent(self, e)
        if self.do_cursor_scope : 
            self.cline1i.setPen(self.pen1)
            self.cline2i.setPen(self.pen2)
        

    def leaveEvent(self, e) :
    #    print 'leaveEvent'
        GUViewAxes.leaveEvent(self, e)
        if self.do_cursor_scope : 
            self.cline1i.setPen(QtGui.QPen())
            self.cline2i.setPen(QtGui.QPen())


    def keyPressEvent(self, e) :
        #print 'keyPressEvent, key=', e.key()         
        if   e.key() == Qt.Key_Escape :
            self.close()

        elif e.key() == Qt.Key_R : 
            self.reset_original_hist()

        elif e.key() == Qt.Key_N :
            from graphqt.GUViewFWImage import image_with_random_peaks
            print '%s: Test set new histogram' % self._name
            arr = image_with_random_peaks((50, 50))
            self.remove_all_graphs()
            hcolor = Qt.green # Qt.yellow Qt.blue Qt.yellow 
            self.add_array_as_hist(arr, pen=QtGui.QPen(hcolor, 0), brush=QtGui.QBrush(hcolor))

    
    def reset_original_hist(self) :
        #print 'Reset original size'
        self.set_view()
        self.update_my_scene()
        self.set_limits()
        self.update_my_scene()
        self.check_axes_limits()


    def _add_path_to_scene(self, path, pen=QtGui.QPen(Qt.yellow), brush=QtGui.QBrush()) :
        self.lst_items.append(self.scene().addPath(path, pen, brush))
        self.update_my_scene()

#------------------------------

    def add_hist(self, values, edges, pen=QtGui.QPen(Qt.black), brush=QtGui.QBrush(), vtype=np.float) :
        nbins = len(values) #if isinstance(values, (list,tuple)) else values.size
        hb   = HBins(edges, nbins) #, vtype)
        binl = hb.binedgesleft()
        binr = hb.binedgesright()
        v0 = 0
        hb.values = values

        self.lst_hbins.append(hb)

        points = [QtCore.QPointF(binl[0], v0),]     # first point
        for bl, br, v in zip(binl, binr, values) :
            points.append(QtCore.QPointF(bl, v))
            points.append(QtCore.QPointF(br, v))
        points.append(QtCore.QPointF(binr[-1], v0)) # last point

        path = QtGui.QPainterPath()
        polygon = QtGui.QPolygonF(points)
        path.addPolygon(polygon)
        self._add_path_to_scene(path, pen, brush)

        self.set_limits()
        self.update_my_scene()
        self.check_axes_limits()

        self.emit(QtCore.SIGNAL('histogram_updated()'))

#------------------------------

    def connect_histogram_updated_to(self, recip) :
        self.connect(self, QtCore.SIGNAL('histogram_updated()'), recip)

    def disconnect_histogram_updated_from(self, recip) :
        self.connect(self, QtCore.SIGNAL('histogram_updated()'), recip)

    def test_histogram_updated_reception(self) :
        print 'GUViewHist.test_histogram_updated_reception'

#------------------------------


    def add_array_as_hist(self, arr, pen=QtGui.QPen(Qt.black), brush=QtGui.QBrush(), vtype=np.float) :
        """Adds array (i.e. like image) as a histogram of intensities
        """
        amin, amax, nbins, values = image_to_hist_arr(arr)
        vmin, vmax = values.min(), values.max()
        #self._xmin = amin
        #self._xmax = amax
        self._ymin = None
        self._ymax = vmax
        self.raxes = QtCore.QRectF(amin, vmin, amax-amin, vmax-vmin) 
        #self.check_limits()
        self.add_hist(values, (amin,amax), pen, brush, vtype)
        self.reset_original_hist()


    def remove_all_graphs(self) :
        #print 'GUViewHist.remove_all_graphs len(self.lst_items)', len(self.lst_items)
        for item in self.lst_items :
            self.scene().removeItem(item)
        self.lst_items = []
        self.lst_hbins = []


    def __del__(self) :
        self.remove_all_graphs()

#------------------------------

if __name__ == "__main__" :

    import sys
    import numpy as np

    nbins = 1000
    x = np.array(range(nbins))-10.1
    x1 = 3.1415927/100 * x
    x2 = 3.1415927/200 * x
    y1 = np.sin(x1)/x1
    y2 = np.sin(x2)/x2
    #y2 = np.random.random((nbins,))

    rectax=QtCore.QRectF(0, -1.2, 100, 2.4)    
    app = QtGui.QApplication(sys.argv)
    w = GUViewHist(None, rectax, origin='DL', scale_ctl='H', rulers='DL',\
                    margl=0.12, margr=0.02, margt=0.02, margb=0.06)
    #w._xmin =-100
    #w._xmax = 200
    w._ymin =-1.2
    w._ymax = 1.2
    #w._ymin =-5
    #w._ymax = 5
    
    w.connect_axes_limits_changed_to(w.test_axes_limits_changed_reception)
    #w.disconnect_axes_limits_changed_from(w.test_axes_limits_changed_reception)

    w.add_hist(y1, (0,100), pen=QtGui.QPen(Qt.blue, 0), brush=QtGui.QBrush(Qt.green))
    w.add_hist(y2, (0,100), pen=QtGui.QPen(Qt.red,  0), brush=QtGui.QBrush(Qt.yellow))

    #w.connect_mean_std_updated_to(w.test_hist_mean_std_updated_reception)
    #w.disconnect_mean_std_updated_from(w.test_hist_mean_std_updated_reception)

    #w.connect_statistics_updated_to(w.test_statistics_std_reception)
    #w.disconnect_statistics_updated_from(w.test_statistics_std_reception)

    w.connect_histogram_updated_to(w.test_histogram_updated_reception)
    #w.disconnect_histogram_updated_from(w.test_histogram_updated_reception)

    w.show()
    app.exec_()

#-----------------------------