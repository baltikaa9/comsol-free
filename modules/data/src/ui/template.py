# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'template.ui'
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
    QSizePolicy, QStatusBar, QToolBar, QTreeWidget,
    QTreeWidgetItem, QVBoxLayout, QWidget)

from src.widgets.graphics_view import GraphicsView

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1008, 600)
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
        self.actionUploadSSH = QAction(MainWindow)
        self.actionUploadSSH.setObjectName(u"actionUploadSSH")
        icon = QIcon(QIcon.fromTheme(u"network-server"))
        self.actionUploadSSH.setIcon(icon)
        self.actionSSHSettings = QAction(MainWindow)
        self.actionSSHSettings.setObjectName(u"actionSSHSettings")
        icon1 = QIcon(QIcon.fromTheme(u"preferences-system-network"))
        self.actionSSHSettings.setIcon(icon1)
        self.actionSaveProject = QAction(MainWindow)
        self.actionSaveProject.setObjectName(u"actionSaveProject")
        icon2 = QIcon(QIcon.fromTheme(u"document-save"))
        self.actionSaveProject.setIcon(icon2)
        self.actionOpenProject = QAction(MainWindow)
        self.actionOpenProject.setObjectName(u"actionOpenProject")
        icon3 = QIcon(QIcon.fromTheme(u"document-open"))
        self.actionOpenProject.setIcon(icon3)
        self.actionSaveProjectAs = QAction(MainWindow)
        self.actionSaveProjectAs.setObjectName(u"actionSaveProjectAs")
        icon4 = QIcon(QIcon.fromTheme(u"document-save-as"))
        self.actionSaveProjectAs.setIcon(icon4)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.projectTree = QTreeWidget(self.centralwidget)
        __qtreewidgetitem = QTreeWidgetItem(self.projectTree)
        QTreeWidgetItem(__qtreewidgetitem)
        QTreeWidgetItem(__qtreewidgetitem)
        __qtreewidgetitem1 = QTreeWidgetItem(self.projectTree)
        QTreeWidgetItem(__qtreewidgetitem1)
        __qtreewidgetitem2 = QTreeWidgetItem(self.projectTree)
        QTreeWidgetItem(__qtreewidgetitem2)
        QTreeWidgetItem(__qtreewidgetitem2)
        __qtreewidgetitem3 = QTreeWidgetItem(self.projectTree)
        QTreeWidgetItem(__qtreewidgetitem3)
        QTreeWidgetItem(__qtreewidgetitem3)
        self.projectTree.setObjectName(u"projectTree")
        self.projectTree.setMinimumSize(QSize(250, 0))
        font = QFont()
        font.setPointSize(14)
        self.projectTree.setFont(font)

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
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBarShapes = QToolBar(MainWindow)
        self.toolBarShapes.setObjectName(u"toolBarShapes")
        self.toolBarShapes.setFont(font)
        self.toolBarShapes.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toolBarShapes.setFloatable(False)
        self.toolBarShapes.setMovable(False)
        MainWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolBarShapes)
        self.toolBarOps = QToolBar(MainWindow)
        self.toolBarOps.setObjectName(u"toolBarOps")
        self.toolBarOps.setFont(font)
        self.toolBarOps.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toolBarOps.setFloatable(False)
        self.toolBarOps.setMovable(False)
        MainWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolBarOps)
        MainWindow.insertToolBarBreak(self.toolBarOps)
        self.toolBarMisc = QToolBar(MainWindow)
        self.toolBarMisc.setObjectName(u"toolBarMisc")
        self.toolBarMisc.setFont(font)
        self.toolBarMisc.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toolBarMisc.setFloatable(False)
        self.toolBarMisc.setMovable(False)
        MainWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolBarMisc)
        MainWindow.insertToolBarBreak(self.toolBarMisc)

        self.toolBarShapes.addAction(self.actionDrawLineByParams)
        self.toolBarShapes.addAction(self.actionDrawRectByParams)
        self.toolBarShapes.addAction(self.actionDrawCircleByParams)
        self.toolBarShapes.addAction(self.actionDrawCurveByParams)
        self.toolBarShapes.addAction(self.actionDrawParametric)
        self.toolBarOps.addAction(self.actionUnion)
        self.toolBarOps.addAction(self.actionDifference)
        self.toolBarOps.addAction(self.actionIntersection)
        self.toolBarOps.addAction(self.actionMirror)
        self.toolBarOps.addAction(self.actionRotate)
        self.toolBarMisc.addAction(self.actionBuildMesh)
        self.toolBarMisc.addSeparator()
        self.toolBarMisc.addAction(self.actionSaveProject)
        self.toolBarMisc.addAction(self.actionOpenProject)
        self.toolBarMisc.addAction(self.actionSaveProjectAs)
        self.toolBarMisc.addSeparator()
        self.toolBarMisc.addAction(self.actionUploadSSH)
        self.toolBarMisc.addAction(self.actionSSHSettings)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionDrawLineByParams.setText(QCoreApplication.translate("MainWindow", u"\u041b\u0438\u043d\u0438\u044f", None))
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
        self.actionUploadSSH.setText(QCoreApplication.translate("MainWindow", u"\u0417\u0430\u0433\u0440\u0443\u0437\u0438\u0442\u044c \u043d\u0430 \u0441\u0435\u0440\u0432\u0435\u0440", None))
        self.actionSSHSettings.setText(QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438 SSH", None))
        self.actionSaveProject.setText(QCoreApplication.translate("MainWindow", u"\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c \u043f\u0440\u043e\u0435\u043a\u0442", None))
        self.actionOpenProject.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0442\u043a\u0440\u044b\u0442\u044c \u043f\u0440\u043e\u0435\u043a\u0442", None))
        self.actionSaveProjectAs.setText(QCoreApplication.translate("MainWindow", u"\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c \u043a\u0430\u043a...", None))
        ___qtreewidgetitem = self.projectTree.headerItem()
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("MainWindow", u"\u041f\u0440\u043e\u0435\u043a\u0442", None));

        __sortingEnabled = self.projectTree.isSortingEnabled()
        self.projectTree.setSortingEnabled(False)
        ___qtreewidgetitem1 = self.projectTree.topLevelItem(0)
        ___qtreewidgetitem1.setText(0, QCoreApplication.translate("MainWindow", u"Material", None));
        ___qtreewidgetitem2 = ___qtreewidgetitem1.child(0)
        ___qtreewidgetitem2.setText(0, QCoreApplication.translate("MainWindow", u"\u041f\u043b\u043e\u0442\u043d\u043e\u0441\u0442\u044c: \u03c1", None));
        ___qtreewidgetitem3 = ___qtreewidgetitem1.child(1)
        ___qtreewidgetitem3.setText(0, QCoreApplication.translate("MainWindow", u"\u0414\u0438\u043d\u0430\u043c\u0438\u0447\u0435\u0441\u043a\u0430\u044f \u0432\u044f\u0437\u043a\u043e\u0441\u0442\u044c: \u03bc", None));
        ___qtreewidgetitem4 = self.projectTree.topLevelItem(1)
        ___qtreewidgetitem4.setText(0, QCoreApplication.translate("MainWindow", u"Physics", None));
        ___qtreewidgetitem5 = ___qtreewidgetitem4.child(0)
        ___qtreewidgetitem5.setText(0, QCoreApplication.translate("MainWindow", u"Turbulence Model: Laminar", None));
        ___qtreewidgetitem6 = self.projectTree.topLevelItem(2)
        ___qtreewidgetitem6.setText(0, QCoreApplication.translate("MainWindow", u"Initial Conditions", None));
        ___qtreewidgetitem7 = ___qtreewidgetitem6.child(0)
        ___qtreewidgetitem7.setText(0, QCoreApplication.translate("MainWindow", u"Velocity: (0, 0)", None));
        ___qtreewidgetitem8 = ___qtreewidgetitem6.child(1)
        ___qtreewidgetitem8.setText(0, QCoreApplication.translate("MainWindow", u"Pressure: 0", None));
        ___qtreewidgetitem9 = self.projectTree.topLevelItem(3)
        ___qtreewidgetitem9.setText(0, QCoreApplication.translate("MainWindow", u"Boundary Conditions", None));
        ___qtreewidgetitem10 = ___qtreewidgetitem9.child(0)
        ___qtreewidgetitem10.setText(0, QCoreApplication.translate("MainWindow", u"Inlet: Velocity (1, 0)", None));
        ___qtreewidgetitem11 = ___qtreewidgetitem9.child(1)
        ___qtreewidgetitem11.setText(0, QCoreApplication.translate("MainWindow", u"Outlet: Pressure 0", None));
        self.projectTree.setSortingEnabled(__sortingEnabled)

        self.toolBarShapes.setWindowTitle(QCoreApplication.translate("MainWindow", u"\u0424\u0438\u0433\u0443\u0440\u044b", None))
        self.toolBarOps.setWindowTitle(QCoreApplication.translate("MainWindow", u"\u041e\u043f\u0435\u0440\u0430\u0446\u0438\u0438", None))
        self.toolBarMisc.setWindowTitle(QCoreApplication.translate("MainWindow", u"\u0421\u0435\u0442\u043a\u0430 / SSH", None))
    # retranslateUi

