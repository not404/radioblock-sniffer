# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\Dropbox\Software\radioblock\sniffer_project\about.ui'
#
# Created: Wed May 01 22:57:45 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(657, 292)
        Dialog.setFocusPolicy(QtCore.Qt.StrongFocus)
        Dialog.setStyleSheet("QToolbar {\n"
"background-image: url(./images/colorado.jpg)}\n"
"\n"
"QLabel#labelBoard { color: yellow; background-color:#ffff99\n"
"; border:4px solid white; border-bottom-color: grey; border-right-color:black;padding-bottom:4px; font:bold}\n"
"\n"
"\n"
"QTextEdit { color: black; background-color:#ffff99  \n"
"\n"
"; border:2px solid #ffff99 ;border-bottom-color: #ffff99 ; border-right-color:#ffff99 ;padding-bottom:5px; font:bold}\n"
"\n"
"QToolButton:pressed\n"
"{\n"
"background-color:     #FFff00;\n"
"\n"
"}")
        Dialog.setModal(True)
        self.labelBoard = QtGui.QLabel(Dialog)
        self.labelBoard.setGeometry(QtCore.QRect(0, 0, 658, 293))
        self.labelBoard.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.labelBoard.setText("")
        self.labelBoard.setPixmap(QtGui.QPixmap("images/about.png"))
        self.labelBoard.setScaledContents(True)
        self.labelBoard.setObjectName("labelBoard")
        self.textEdit = QtGui.QTextEdit(Dialog)
        self.textEdit.setGeometry(QtCore.QRect(250, 90, 391, 121))
        self.textEdit.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textEdit.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textEdit.setReadOnly(True)
        self.textEdit.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.textEdit.setObjectName("textEdit")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "About SM_Sniffer ", None, QtGui.QApplication.UnicodeUTF8))
        self.textEdit.setHtml(QtGui.QApplication.translate("Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:600; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt; font-weight:400;\">SimpleMesh Sniffer has been developed by:</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:12pt; font-weight:400;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt; font-weight:400;\">Colorado Micro Devices</span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt; font-weight:400;\">web: </span><a href=\"http://www.coloradomicrodevices.com\"><span style=\" font-size:12pt; font-weight:400; text-decoration: underline; color:#0000ff;\">www.coloradomicrodevices.com</span></a></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt; font-weight:400;\">email: </span><a href=\"info@coloradomicrodevices.com\"><span style=\" font-size:12pt; font-weight:400; text-decoration: underline; color:#0000ff;\">info@coloradomicrodevices.com</span></a></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:12pt; font-weight:400; text-decoration: underline; color:#0000ff;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt; font-weight:400;\"><br /></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

