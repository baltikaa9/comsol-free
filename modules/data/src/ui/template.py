# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'template2.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, Qt)
from PySide6.QtGui import (QAction)
from PySide6.QtWidgets import (QHBoxLayout, QLabel,
                               QStatusBar, QToolBar,
                               QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget)

from src.graphics_view import GraphicsView

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(957, 595)
        self.actionSelect = QAction(MainWindow)
        self.actionSelect.setObjectName(u"actionSelect")
        self.actionSelect.setCheckable(True)
        self.actionSelect.setChecked(True)
        self.actionDrawLine = QAction(MainWindow)
        self.actionDrawLine.setObjectName(u"actionDrawLine")
        self.actionDrawLine.setCheckable(True)
        self.actionDrawRect = QAction(MainWindow)
        self.actionDrawRect.setObjectName(u"actionDrawRect")
        self.actionDrawRect.setCheckable(True)
        self.actionDrawCircle = QAction(MainWindow)
        self.actionDrawCircle.setObjectName(u"actionDrawCircle")
        self.actionDrawCircle.setCheckable(True)
        self.actionDrawCurve = QAction(MainWindow)
        self.actionDrawCurve.setObjectName(u"actionDrawCurve")
        self.actionDrawCurve.setCheckable(True)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.mainLayout = QHBoxLayout(self.centralwidget)
        self.mainLayout.setObjectName(u"mainLayout")
        self.projectTree = QTreeWidget(self.centralwidget)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"1");
        self.projectTree.setHeaderItem(__qtreewidgetitem)
        self.projectTree.setObjectName(u"projectTree")
        self.projectTree.setHeaderHidden(True)

        self.mainLayout.addWidget(self.projectTree)

        self.graphicsView = GraphicsView(self.centralwidget)
        self.graphicsView.setObjectName(u"graphicsView")

        self.mainLayout.addWidget(self.graphicsView)

        self.propertiesLayout = QVBoxLayout()
        self.propertiesLayout.setObjectName(u"propertiesLayout")
        self.labelProperties = QLabel(self.centralwidget)
        self.labelProperties.setObjectName(u"labelProperties")

        self.propertiesLayout.addWidget(self.labelProperties)


        self.mainLayout.addLayout(self.propertiesLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.mainToolBar = QToolBar(MainWindow)
        self.mainToolBar.setObjectName(u"mainToolBar")
        MainWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.mainToolBar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.mainToolBar.addAction(self.actionSelect)
        self.mainToolBar.addAction(self.actionDrawLine)
        self.mainToolBar.addAction(self.actionDrawRect)
        self.mainToolBar.addAction(self.actionDrawCircle)
        self.mainToolBar.addAction(self.actionDrawCurve)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Geometry Editor", None))
        self.actionSelect.setText(QCoreApplication.translate("MainWindow", u"Select", None))
        self.actionDrawLine.setText(QCoreApplication.translate("MainWindow", u"Draw Line", None))
        self.actionDrawRect.setText(QCoreApplication.translate("MainWindow", u"Draw Rectangle", None))
        self.actionDrawCircle.setText(QCoreApplication.translate("MainWindow", u"Draw Circle", None))
        self.actionDrawCurve.setText(QCoreApplication.translate("MainWindow", u"Draw Curve", None))
        self.labelProperties.setText(QCoreApplication.translate("MainWindow", u"Properties", None))
        self.mainToolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"Tools", None))
    # retranslateUi

