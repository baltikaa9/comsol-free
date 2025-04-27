# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'template5.ui'
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
        self.actionDrawLineByParams = QAction(MainWindow)
        self.actionDrawLineByParams.setObjectName(u"actionDrawLineByParams")
        self.actionDrawRect = QAction(MainWindow)
        self.actionDrawRect.setObjectName(u"actionDrawRect")
        self.actionDrawRectByParams = QAction(MainWindow)
        self.actionDrawRectByParams.setObjectName(u"actionDrawRectByParams")
        self.actionDrawCircle = QAction(MainWindow)
        self.actionDrawCircle.setObjectName(u"actionDrawCircle")
        self.actionDrawCircleByParams = QAction(MainWindow)
        self.actionDrawCircleByParams.setObjectName(u"actionDrawCircleByParams")
        self.actionDrawCurve = QAction(MainWindow)
        self.actionDrawCurve.setObjectName(u"actionDrawCurve")
        self.actionDrawCurveByParams = QAction(MainWindow)
        self.actionDrawCurveByParams.setObjectName(u"actionDrawCurveByParams")
        self.actionDrawParametric = QAction(MainWindow)
        self.actionDrawParametric.setObjectName(u"actionDrawParametric")
        self.actionUnion = QAction(MainWindow)
        self.actionUnion.setObjectName(u"actionUnion")
        self.actionDifference = QAction(MainWindow)
        self.actionDifference.setObjectName(u"actionDifference")
        self.actionIntersection = QAction(MainWindow)
        self.actionIntersection.setObjectName(u"actionIntersection")
        self.actionMirror = QAction(MainWindow)
        self.actionMirror.setObjectName(u"actionMirror")
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
        self.mainToolBar.addAction(self.actionDrawLineByParams)
        self.mainToolBar.addAction(self.actionDrawRect)
        self.mainToolBar.addAction(self.actionDrawRectByParams)
        self.mainToolBar.addAction(self.actionDrawCircle)
        self.mainToolBar.addAction(self.actionDrawCircleByParams)
        self.mainToolBar.addAction(self.actionDrawCurve)
        self.mainToolBar.addAction(self.actionDrawCurveByParams)
        self.mainToolBar.addAction(self.actionDrawParametric)
        self.mainToolBar.addAction(self.actionUnion)
        self.mainToolBar.addAction(self.actionDifference)
        self.mainToolBar.addAction(self.actionIntersection)
        self.mainToolBar.addAction(self.actionMirror)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionSelect.setText(QCoreApplication.translate("MainWindow", u"Select", None))
        self.actionDrawLine.setText(QCoreApplication.translate("MainWindow", u"Draw Line (Mouse)", None))
        self.actionDrawLineByParams.setText(QCoreApplication.translate("MainWindow", u"Draw Line (Params)", None))
        self.actionDrawRect.setText(QCoreApplication.translate("MainWindow", u"Draw Rectangle (Mouse)", None))
        self.actionDrawRectByParams.setText(QCoreApplication.translate("MainWindow", u"Draw Rectangle (Params)", None))
        self.actionDrawCircle.setText(QCoreApplication.translate("MainWindow", u"Draw Circle (Mouse)", None))
        self.actionDrawCircleByParams.setText(QCoreApplication.translate("MainWindow", u"Draw Circle (Params)", None))
        self.actionDrawCurve.setText(QCoreApplication.translate("MainWindow", u"Draw Curve (Mouse)", None))
        self.actionDrawCurveByParams.setText(QCoreApplication.translate("MainWindow", u"Draw Curve (Params)", None))
        self.actionDrawParametric.setText(QCoreApplication.translate("MainWindow", u"Draw Parametric Curve", None))
        self.actionUnion.setText(QCoreApplication.translate("MainWindow", u"Union", None))
        self.actionDifference.setText(QCoreApplication.translate("MainWindow", u"Difference", None))
        self.actionIntersection.setText(QCoreApplication.translate("MainWindow", u"Intersection", None))
        self.actionMirror.setText(QCoreApplication.translate("MainWindow", u"Mirror", None))
        ___qtreewidgetitem = self.projectTree.headerItem()
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("MainWindow", u"Project", None));
        self.mainToolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"Tools", None))
    # retranslateUi

