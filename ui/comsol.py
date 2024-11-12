# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'comsol.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QFormLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QPushButton, QSizePolicy, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.groupBox_plot_settings = QGroupBox(self.centralwidget)
        self.groupBox_plot_settings.setObjectName(u"groupBox_plot_settings")
        self.groupBox_plot_settings.setMaximumSize(QSize(384, 16777215))
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_plot_settings)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(self.groupBox_plot_settings)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)

        self.lineEdit = QLineEdit(self.groupBox_plot_settings)
        self.lineEdit.setObjectName(u"lineEdit")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.lineEdit)

        self.label_2 = QLabel(self.groupBox_plot_settings)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_2)

        self.comboBox = QComboBox(self.groupBox_plot_settings)
        self.comboBox.setObjectName(u"comboBox")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.comboBox)

        self.label_3 = QLabel(self.groupBox_plot_settings)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_3)

        self.lineEdit_3 = QLineEdit(self.groupBox_plot_settings)
        self.lineEdit_3.setObjectName(u"lineEdit_3")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.lineEdit_3)

        self.label_7 = QLabel(self.groupBox_plot_settings)
        self.label_7.setObjectName(u"label_7")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label_7)

        self.comboBox_3 = QComboBox(self.groupBox_plot_settings)
        self.comboBox_3.setObjectName(u"comboBox_3")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.comboBox_3)


        self.verticalLayout_3.addLayout(self.formLayout)

        self.pushButton_plot = QPushButton(self.groupBox_plot_settings)
        self.pushButton_plot.setObjectName(u"pushButton_plot")

        self.verticalLayout_3.addWidget(self.pushButton_plot)


        self.horizontalLayout.addWidget(self.groupBox_plot_settings)

        self.widget_visualisation = QWidget(self.centralwidget)
        self.widget_visualisation.setObjectName(u"widget_visualisation")

        self.horizontalLayout.addWidget(self.widget_visualisation)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.groupBox_plot_settings.setTitle(QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"\u0414\u0430\u043d\u043d\u044b\u0435", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"\u0422\u0438\u043f \u0433\u0440\u0430\u0444\u0438\u043a\u0430", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"\u0412\u044b\u0440\u0430\u0436\u0435\u043d\u0438\u0435", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"\u0415\u0434. \u0438\u0437\u043c\u0435\u0440\u0435\u043d\u0438\u044f", None))
        self.pushButton_plot.setText(QCoreApplication.translate("MainWindow", u"\u041f\u043e\u0441\u0442\u0440\u043e\u0438\u0442\u044c", None))
    # retranslateUi

