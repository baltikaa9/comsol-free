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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFormLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QPushButton, QSizePolicy, QVBoxLayout,
    QWidget)

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

        self.lineEdit_data_path = QLineEdit(self.groupBox_plot_settings)
        self.lineEdit_data_path.setObjectName(u"lineEdit_data_path")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.lineEdit_data_path)

        self.label_3 = QLabel(self.groupBox_plot_settings)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_3)

        self.comboBox_expression = QComboBox(self.groupBox_plot_settings)
        self.comboBox_expression.addItem("")
        self.comboBox_expression.addItem("")
        self.comboBox_expression.setObjectName(u"comboBox_expression")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.comboBox_expression)

        self.label_2 = QLabel(self.groupBox_plot_settings)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_2)

        self.checkBox_stream_lines = QCheckBox(self.groupBox_plot_settings)
        self.checkBox_stream_lines.setObjectName(u"checkBox_stream_lines")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.checkBox_stream_lines)

        self.label_4 = QLabel(self.groupBox_plot_settings)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label_4)

        self.lineEdit_levels = QLineEdit(self.groupBox_plot_settings)
        self.lineEdit_levels.setObjectName(u"lineEdit_levels")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.lineEdit_levels)

        self.label_5 = QLabel(self.groupBox_plot_settings)
        self.label_5.setObjectName(u"label_5")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.label_5)

        self.lineEdit_geometry_color = QLineEdit(self.groupBox_plot_settings)
        self.lineEdit_geometry_color.setObjectName(u"lineEdit_geometry_color")

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.lineEdit_geometry_color)


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
        self.label.setText(QCoreApplication.translate("MainWindow", u"\u041f\u043e\u043b\u043d\u044b\u0439 \u043f\u0443\u0442\u044c \u043a \u0434\u0430\u043d\u043d\u044b\u043c", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"\u0427\u0442\u043e \u0440\u0438\u0441\u043e\u0432\u0430\u0442\u044c", None))
        self.comboBox_expression.setItemText(0, QCoreApplication.translate("MainWindow", u"\u0421\u043a\u043e\u0440\u043e\u0441\u0442\u044c", None))
        self.comboBox_expression.setItemText(1, QCoreApplication.translate("MainWindow", u"\u0414\u0430\u0432\u043b\u0435\u043d\u0438\u0435", None))

        self.label_2.setText(QCoreApplication.translate("MainWindow", u"\u041b\u0438\u043d\u0438\u0438 \u0442\u043e\u043a\u0430", None))
        self.checkBox_stream_lines.setText("")
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u0443\u0440\u043e\u0432\u043d\u0435\u0439", None))
        self.lineEdit_levels.setText(QCoreApplication.translate("MainWindow", u"100", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"\u0426\u0432\u0435\u0442 \u043a\u043e\u043d\u0442\u0443\u0440\u0430 \u043a\u0440\u044b\u043b\u0430", None))
        self.lineEdit_geometry_color.setText(QCoreApplication.translate("MainWindow", u"black", None))
        self.pushButton_plot.setText(QCoreApplication.translate("MainWindow", u"\u041f\u043e\u0441\u0442\u0440\u043e\u0438\u0442\u044c", None))
    # retranslateUi

