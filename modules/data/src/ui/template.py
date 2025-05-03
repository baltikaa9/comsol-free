# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'template7.ui'
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
        MainWindow.resize(1008, 600)
        self.actionSelect = QAction(MainWindow)
        self.actionSelect.setObjectName(u"actionSelect")
        self.actionDrawLineByParams = QAction(MainWindow)
        self.actionDrawLineByParams.setObjectName(u"actionDrawLineByParams")
        self.actionDrawRectByParams = QAction(MainWindow)
        self.actionDrawRectByParams.setObjectName(u"actionDrawRectByParams")
        self.actionDrawCircleByParams = QAction(MainWindow)
        self.actionDrawCircleByParams.setObjectName(u"actionDrawCircleByParams")
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
        self.actionRotate = QAction(MainWindow)
        self.actionRotate.setObjectName(u"actionRotate")
        self.actionBuildMesh = QAction(MainWindow)
        self.actionBuildMesh.setObjectName(u"actionBuildMesh")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.projectTree = QTreeWidget(self.centralwidget)
        __qtreewidgetitem = QTreeWidgetItem(self.projectTree)
        QTreeWidgetItem(__qtreewidgetitem)
        __qtreewidgetitem1 = QTreeWidgetItem(self.projectTree)
        QTreeWidgetItem(__qtreewidgetitem1)
        QTreeWidgetItem(__qtreewidgetitem1)
        __qtreewidgetitem2 = QTreeWidgetItem(self.projectTree)
        QTreeWidgetItem(__qtreewidgetitem2)
        QTreeWidgetItem(__qtreewidgetitem2)
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
        self.menubar.setGeometry(QRect(0, 0, 1008, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.mainToolBar = QToolBar(MainWindow)
        self.mainToolBar.setObjectName(u"mainToolBar")
        MainWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.mainToolBar)

        self.mainToolBar.addAction(self.actionSelect)
        self.mainToolBar.addAction(self.actionDrawLineByParams)
        self.mainToolBar.addAction(self.actionDrawRectByParams)
        self.mainToolBar.addAction(self.actionDrawCircleByParams)
        self.mainToolBar.addAction(self.actionDrawCurveByParams)
        self.mainToolBar.addAction(self.actionDrawParametric)
        self.mainToolBar.addAction(self.actionUnion)
        self.mainToolBar.addAction(self.actionDifference)
        self.mainToolBar.addAction(self.actionIntersection)
        self.mainToolBar.addAction(self.actionMirror)
        self.mainToolBar.addAction(self.actionRotate)
        self.mainToolBar.addAction(self.actionBuildMesh)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionSelect.setText(QCoreApplication.translate("MainWindow", u"\u0412\u044b\u0431\u043e\u0440", None))
        self.actionDrawLineByParams.setText(QCoreApplication.translate("MainWindow", u"\u041f\u0440\u044f\u043c\u0430\u044f", None))
        self.actionDrawRectByParams.setText(QCoreApplication.translate("MainWindow", u"\u041f\u0440\u044f\u043c\u043e\u0443\u0433\u043e\u043b\u044c\u043d\u0438\u043a", None))
        self.actionDrawCircleByParams.setText(QCoreApplication.translate("MainWindow", u"\u042d\u043b\u043b\u0438\u043f\u0441", None))
        self.actionDrawCurveByParams.setText(QCoreApplication.translate("MainWindow", u"\u041a\u0440\u0438\u0432\u0430\u044f \u0411\u0435\u0437\u044c\u0435", None))
        self.actionDrawParametric.setText(QCoreApplication.translate("MainWindow", u"\u041f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u0438\u0447\u0435\u0441\u043a\u0430\u044f \u043a\u0440\u0438\u0432\u0430\u044f", None))
        self.actionUnion.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0431\u044a\u0435\u0434\u0438\u043d\u0435\u043d\u0438\u0435", None))
        self.actionDifference.setText(QCoreApplication.translate("MainWindow", u"\u0420\u0430\u0437\u043d\u0438\u0446\u0430", None))
        self.actionIntersection.setText(QCoreApplication.translate("MainWindow", u"\u041f\u0435\u0440\u0435\u0441\u0435\u0447\u0435\u043d\u0438\u0435", None))
        self.actionMirror.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0442\u0440\u0430\u0436\u0435\u043d\u0438\u0435", None))
        self.actionRotate.setText(QCoreApplication.translate("MainWindow", u"\u041f\u043e\u0432\u043e\u0440\u043e\u0442", None))
        self.actionBuildMesh.setText(QCoreApplication.translate("MainWindow", u"\u041f\u043e\u0441\u0442\u0440\u043e\u0438\u0442\u044c \u0441\u0435\u0442\u043a\u0443", None))
        ___qtreewidgetitem = self.projectTree.headerItem()
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("MainWindow", u"Project", None));

        __sortingEnabled = self.projectTree.isSortingEnabled()
        self.projectTree.setSortingEnabled(False)
        ___qtreewidgetitem1 = self.projectTree.topLevelItem(0)
        ___qtreewidgetitem1.setText(0, QCoreApplication.translate("MainWindow", u"Physics", None));
        ___qtreewidgetitem2 = ___qtreewidgetitem1.child(0)
        ___qtreewidgetitem2.setText(0, QCoreApplication.translate("MainWindow", u"Turbulence Model: Laminar", None));
        ___qtreewidgetitem3 = self.projectTree.topLevelItem(1)
        ___qtreewidgetitem3.setText(0, QCoreApplication.translate("MainWindow", u"Initial Conditions", None));
        ___qtreewidgetitem4 = ___qtreewidgetitem3.child(0)
        ___qtreewidgetitem4.setText(0, QCoreApplication.translate("MainWindow", u"Velocity: (0, 0)", None));
        ___qtreewidgetitem5 = ___qtreewidgetitem3.child(1)
        ___qtreewidgetitem5.setText(0, QCoreApplication.translate("MainWindow", u"Pressure: 0", None));
        ___qtreewidgetitem6 = self.projectTree.topLevelItem(2)
        ___qtreewidgetitem6.setText(0, QCoreApplication.translate("MainWindow", u"Boundary Conditions", None));
        ___qtreewidgetitem7 = ___qtreewidgetitem6.child(0)
        ___qtreewidgetitem7.setText(0, QCoreApplication.translate("MainWindow", u"Inlet: Velocity (1, 0)", None));
        ___qtreewidgetitem8 = ___qtreewidgetitem6.child(1)
        ___qtreewidgetitem8.setText(0, QCoreApplication.translate("MainWindow", u"Outlet: Pressure 0", None));
        self.projectTree.setSortingEnabled(__sortingEnabled)

        self.mainToolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"Tools", None))
    # retranslateUi

