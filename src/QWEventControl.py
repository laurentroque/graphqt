#------------------------------
"""
@version $Id: QWEventControl.py 13157 2017-02-18 00:05:34Z dubrovin@SLAC.STANFORD.EDU $

@author Mikhail S. Dubrovin
"""
#------------------------------
import sys
import os

from PyQt4 import QtGui, QtCore
from graphqt.Frame import Frame
from graphqt.Styles import style
#------------------------------

class QWEventControl(Frame) :
    """GUI control on event number
    """
    def __init__ (self, cp, log, parent=None, show_mode=0) :
        """show_mode & 1 - frame
                     & 2 - dt(msec) button
        """
        Frame.__init__(self, parent, mlw=1, vis=show_mode & 1)
        self._name = self.__class__.__name__

        self.cp  = cp
        self.log = log
        self.show_mode = show_mode

        self.event_number = cp.event_number
        self.event_step   = cp.event_step
        self.wait_msec    = cp.wait_msec
        self.max_evt_num = None

        #self.char_expand = cp.char_expand

        self.lab_evt = QtGui.QLabel('Evt:')
        self.lab_stp = QtGui.QLabel('  Step:')
        self.lab_dtw = QtGui.QLabel('  t(ms):')
        self.but_bwd = QtGui.QPushButton('<')
        self.but_fwd = QtGui.QPushButton('>')
        self.but_ctl = QtGui.QPushButton('Start')
        self.edi_evt = QtGui.QLineEdit(str(self.event_number.value()))
        self.edi_stp = QtGui.QLineEdit(str(self.event_step.value()))
        self.edi_dtw = QtGui.QLineEdit(str(self.wait_msec.value()))

        self.set_layout()
        self.set_style()
        self.set_tool_tips()

        self.connect(self.but_bwd, QtCore.SIGNAL('clicked()'), self.on_but_bwd)
        self.connect(self.but_fwd, QtCore.SIGNAL('clicked()'), self.on_but_fwd)
        self.connect(self.but_ctl, QtCore.SIGNAL('clicked()'), self.on_but_ctl)
        self.connect(self.edi_evt, QtCore.SIGNAL('editingFinished()'), self.on_edi_evt)
        self.connect(self.edi_stp, QtCore.SIGNAL('editingFinished()'), self.on_edi_stp)
        self.connect(self.edi_dtw, QtCore.SIGNAL('editingFinished()'), self.on_edi_dtw)

        self.timer = QtCore.QTimer()
        self.connect(self.timer, QtCore.SIGNAL('timeout()'), self.on_timeout)


    def set_layout(self):
        self.hbox = QtGui.QHBoxLayout()
        self.hbox.addWidget(self.lab_evt)
        self.hbox.addWidget(self.but_bwd)
        self.hbox.addSpacing(-5)
        self.hbox.addWidget(self.edi_evt)
        self.hbox.addSpacing(-5)
        self.hbox.addWidget(self.but_fwd)
        self.hbox.addStretch(1)
        self.hbox.addWidget(self.lab_stp)
        self.hbox.addWidget(self.edi_stp)
        self.hbox.addStretch(1)
        self.hbox.addWidget(self.lab_dtw)
        self.hbox.addWidget(self.edi_dtw)
        self.hbox.addStretch(1)
        self.hbox.addWidget(self.but_ctl)
        self.hbox.addStretch(1)
        self.setLayout(self.hbox)
 

    def set_tool_tips(self):
        self.setToolTip('Event number control')


    def set_style(self):
        #self.setMinimumWidth(500)
        #self.setGeometry(10, 25, 400, 600)
        #self.setFixedHeight(100)
        #self.setContentsMargins(QtCore.QMargins(-5,-5,-5,-5))

        self.edi_evt.setValidator(QtGui.QIntValidator(0,100000000,self))
        self.edi_stp.setValidator(QtGui.QIntValidator(-1000000,1000000,self))
        self.edi_dtw.setValidator(QtGui.QIntValidator(0,1000000,self))

        self.lab_evt.setStyleSheet(style.styleLabel)
        self.lab_stp.setStyleSheet(style.styleLabel)
        self.lab_dtw.setStyleSheet(style.styleLabel)
        #self.but_bwd.setFixedSize(27,27)
        #self.but_fwd.setFixedSize(27,27)
        self.but_bwd.setFixedWidth(25)
        self.but_fwd.setFixedWidth(25)
        self.edi_evt.setFixedWidth(50)
        self.edi_stp.setFixedWidth(40)
        self.edi_dtw.setFixedWidth(50)
        self.but_ctl.setFixedWidth(50)
        self.but_ctl.setStyleSheet(style.styleButtonGood)

        self.lab_dtw.setVisible(self.show_mode & 2)
        self.edi_dtw.setVisible(self.show_mode & 2)
        

    #def on_but(self):
    #    if self.but_ins.hasFocus() : print 'on_but ins'
    #    if self.but_exp.hasFocus() : print 'on_but exp'
    #    if self.but_run.hasFocus() : print 'on_but run'


    def on_edi_evt(self):
        num = int(self.edi_evt.displayText())
        self.set_event_number(num)


    def on_edi_stp(self):
        num = int(self.edi_stp.displayText())
        self.event_step.setValue(num)
        self.log.info('Set event step: %d' % num, __name__)


    def on_edi_dtw(self):
        num = int(self.edi_dtw.displayText())
        self.wait_msec.setValue(num)
        self.log.info('Set waii time between events (msec): %d' % num, __name__)


    def on_but_bwd(self):
        num = self.event_number.value() - self.event_step.value()
        self.set_event_number(num)


    def on_but_fwd(self):
        num = self.event_number.value() + self.event_step.value()
        self.set_event_number(num)


    def set_max_event_number(self, num):
        if not isinstance(num, int) : return
        self.max_evt_num = num
        self.edi_evt.setValidator(QtGui.QIntValidator(0,num,self))


    def set_event_number(self, num):
        if num<0 : num = 0
        if self.max_evt_num is not None\
        and num>self.max_evt_num : num = self.max_evt_num
        if num == int(self.event_number.value()) : return
        self.event_number.setValue(num)
        self.edi_evt.setText('%d'%num)
        self.log.info('Set event number: %d' % num, __name__)
        self.emit(QtCore.SIGNAL('new_event_number(int)'), num)


    def connect_new_event_number_to_recipient(self, recip) :
        self.connect(self, QtCore.SIGNAL('new_event_number(int)'), recip)


    def disconnect_new_event_number_from_recipient(self, recip) :
        self.disconnect(self, QtCore.SIGNAL('new_event_number(int)'), recip)


    def test_new_event_number_reception(self, evnum) :
        print '%s.test_new_event_number_reception: %d' % (self._name, evnum)


    def on_timeout(self) :
        self.on_but_fwd()
        self.timer.start(self.wait_msec.value()) 


    def on_but_ctl(self):
        s = self.but_ctl.text()
        if s=='Start' :
            self.but_ctl.setText('Stop')
            self.but_ctl.setStyleSheet(style.styleButtonBad)
            self.on_timeout()
        else :
            self.but_ctl.setText('Start')
            self.but_ctl.setStyleSheet(style.styleButtonGood)
            self.timer.stop()

#------------------------------
#------------------------------
#------------------------------
#------------------------------

if __name__ == "__main__" :

    from graphqt.Logger             import log
    from graphqt.IVConfigParameters import cp

    app = QtGui.QApplication(sys.argv)
    w = QWEventControl(cp, log, parent=None, show_mode=2)
    w.setWindowTitle(w._name)
    w.move(QtCore.QPoint(50,50))
    w.connect_new_event_number_to_recipient(w.test_new_event_number_reception)
    w.show()
    app.exec_()

#------------------------------