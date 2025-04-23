# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'template3.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QHeaderView, QMainWindow,
    QMenuBar, QSizePolicy, QStatusBar, QToolBar,
    QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget)

from src.graphics_view import GraphicsView

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.actionSelect = QAction(MainWindow)
        self.actionSelect.setObjectName(u"actionSelect")
        self.actionDrawLine = QAction(MainWindow)
        self.actionDrawLine.setObjectName(u"actionDrawLine")
        self.actionDrawRect = QAction(MainWindow)
        self.actionDrawRect.setObjectName(u"actionDrawRect")
        self.actionDrawCircle = QAction(MainWindow)
        self.actionDrawCircle.setObjectName(u"actionDrawCircle")
        self.actionDrawCurve = QAction(MainWindow)
        self.actionDrawCurve.setObjectName(u"actionDrawCurve")
        self.actionDrawParametric = QAction(MainWindow)
        self.actionDrawParametric.setObjectName(u"actionDrawParametric")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.projectTree = QTreeWidget(self.centralwidget)
        self.projectTree.setObjectName(u"projectTree")

        self.horizontalLayout.addWidget(self.projectTree)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.graphicsView = GraphicsView(self.centralwidget)
        self.graphicsView.setObjectName(u"graphicsView")

        self.verticalLayout.addWidget(self.graphicsView)

        self.propertiesLayout = QHBoxLayout()
        self.propertiesLayout.setObjectName(u"propertiesLayout")

        self.verticalLayout.addLayout(self.propertiesLayout)


        self.horizontalLayout.addLayout(self.verticalLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.mainToolBar = QToolBar(MainWindow)
        self.mainToolBar.setObjectName(u"mainToolBar")
        MainWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.mainToolBar)

        self.mainToolBar.addAction(self.actionSelect)
        self.mainToolBar.addAction(self.actionDrawLine)
        self.mainToolBar.addAction(self.actionDrawRect)
        self.mainToolBar.addAction(self.actionDrawCircle)
        self.mainToolBar.addAction(self.actionDrawCurve)
        self.mainToolBar.addAction(self.actionDrawParametric)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionSelect.setText(QCoreApplication.translate("MainWindow", u"Select", None))
        self.actionDrawLine.setText(QCoreApplication.translate("MainWindow", u"Draw Line", None))
        self.actionDrawRect.setText(QCoreApplication.translate("MainWindow", u"Draw Rectangle", None))
        self.actionDrawCircle.setText(QCoreApplication.translate("MainWindow", u"Draw Circle", None))
        self.actionDrawCurve.setText(QCoreApplication.translate("MainWindow", u"Draw Curve", None))
        self.actionDrawParametric.setText(QCoreApplication.translate("MainWindow", u"Draw Parametric Curve", None))
        ___qtreewidgetitem = self.projectTree.headerItem()
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("MainWindow", u"Project", None));
        self.mainToolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"Tools", None))
    # retranslateUi

