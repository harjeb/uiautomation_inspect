'''
Author: cjju@nreal.ai
Date: 2023-05-10 09:50:17
LastEditors: cjju@nreal.ai
LastEditTime: 2023-05-16 15:27:49
Description: 

Copyright (c) 2023 by cjju@nreal.ai, All Rights Reserved. 
'''
import sys
from PyQt5.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem, QWidget, QMessageBox,QMenu, QTableWidgetItem
import uiautomation as auto
import os
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt,QThread
import time
from io import StringIO
import traceback


def excepthook(excType, excValue, tracebackobj):
    """
    Global function to catch unhandled exceptions.
    
    @param excType exception type
    @param excValue exception value
    @param tracebackobj traceback object
    """
    separator = '-' * 80
    logFile = "error.log"
    notice = \
        """An unhandled exception occurred. Please report the problem\n"""\
        """using the error reporting dialog or via email to <%s>.\n"""\
        """A log has been written to "%s".\n\nError information:\n""" % \
        ("harjeb@outlook.com", "")
    versionInfo="0.0.1"
    timeString = time.strftime("%Y-%m-%d, %H:%M:%S")
    
    tbinfofile = StringIO()
    traceback.print_tb(tracebackobj, None, tbinfofile)
    tbinfofile.seek(0)
    tbinfo = tbinfofile.read()
    errmsg = '%s: \n%s' % (str(excType), str(excValue))
    sections = [separator, timeString, separator, errmsg, separator, tbinfo]
    msg = '\n'.join(sections)
    try:
        f = open(logFile, "w")
        f.write(msg)
        f.write(versionInfo)
        f.close()
    except IOError:
        pass
    errorbox = QMessageBox()
    errorbox.setText(str(notice)+str(msg)+str(versionInfo))
    errorbox.exec_()

sys.excepthook = excepthook

class Ui_UI_Inspect(object):
    def setupUi(self, UI_Inspect):
        UI_Inspect.setObjectName("UI_Inspect")
        UI_Inspect.resize(933, 621)
        self.horizontalLayout = QtWidgets.QHBoxLayout(UI_Inspect)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.fresh_btn = QtWidgets.QPushButton(UI_Inspect)
        self.fresh_btn.setText("刷新")
        self.fresh_btn.setObjectName("fresh_btn")
        self.verticalLayout.addWidget(self.fresh_btn)
        self.treeWidget = QtWidgets.QTreeWidget(UI_Inspect)
        self.treeWidget.setMinimumSize(QtCore.QSize(300, 500))
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.headerItem().setText(0, "UI元素树状图")
        self.verticalLayout.addWidget(self.treeWidget)
        self.horizontalLayout.addLayout(self.verticalLayout)
        spacerItem = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_2 = QtWidgets.QLabel(UI_Inspect)
        self.label_2.setText("")
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.tableWidget = QtWidgets.QTableWidget(UI_Inspect)
        self.tableWidget.setMinimumSize(QtCore.QSize(300, 500))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.verticalLayout_2.addWidget(self.tableWidget)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
    

        self.retranslateUi(UI_Inspect)
        QtCore.QMetaObject.connectSlotsByName(UI_Inspect)

    def retranslateUi(self, UI_Inspect):
        _translate = QtCore.QCoreApplication.translate
        UI_Inspect.setWindowTitle(_translate("UI_Inspect", "UI_Inspect"))
    
    
class Get_Tree_Text(QThread):
    tree_text = QtCore.pyqtSignal(str)

    def __init__(self, handle_id):
        super(Get_Tree_Text, self).__init__()
        self.handle_id = handle_id
    
    def run(self):
        try:
            # 获取当前文件所在的绝对路径
            current_path = os.path.realpath(sys.executable)
            #current_path = os.path.dirname(__file__)
            # 获取该路径下的文件夹路径
            folder_path = os.path.dirname(current_path)
            # 判断文件是否存在，并删除
            file_path = os.path.join(folder_path, "@AutomationLog.txt")
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    with open(file_path,'w', encoding='utf-8') as t:
                        t.write('')
            if True:        
                with auto.UIAutomationInitializerInThread(debug=True):
                    newRoot = auto.GetRootControl()  # ok, root control created in current thread
                    auto.EnumAndLogControl(newRoot)
            else:
                with auto.UIAutomationInitializerInThread(debug=True):
                    new = auto.ControlFromHandle(self.handle_id)  # ok, root control created in current thread
                    auto.EnumAndLogControl(new,5)                
            tree_string = self.get_tree_text("@AutomationLog.txt")
            self.tree_text.emit(tree_string)
        except Exception as e:
            print(e)
            self.tree_text.emit("")
    
    def get_tree_text(self, filepath):
        with open(filepath,'r', encoding='utf-8') as t:
            text_lines = t.readlines()[:-1]
            in_block = True
            newlines = []
            for i in text_lines:
                if not i.startswith("ControlType") and in_block:
                    continue
                else:
                    newlines.append(i)
                    in_block = False
        tree_text = "".join(newlines) 
        return tree_text
        
    
class UI_Inspect_Win(QWidget,Ui_UI_Inspect):
    def __init__(self, parent=None):
        super(UI_Inspect_Win,self).__init__(parent)
        self.setupUi(self)
        self.fresh_btn.setEnabled(False)
        self.fresh_btn.setText("初始化中...")
        self.init_tree =  Get_Tree_Text(0)
        self.init_tree.tree_text.connect(self.get_text)
        self.init_tree.start()

        self.fresh_btn.clicked.connect(self.fresh_tree)
        self.treeWidget.itemClicked.connect(self.update_table)
        # 隐藏行头
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(['类型', '值'])

    def get_text(self,tree_text):
        if not tree_text:
            self.fresh_btn.setEnabled(True)
            print("error pops")
        self.tree_string = tree_text
        self.build_model(self.tree_string.split("\n"))
        self.fresh_btn.setEnabled(True)
        self.fresh_btn.setText("刷新")
        
    def fresh_tree(self):
        self.treeWidget.clear()
        self.fresh_btn.setEnabled(False)
        self.fresh_thread = Get_Tree_Text(592302)
        self.fresh_thread.tree_text.connect(self.get_text)
        self.fresh_thread.start()

    def update_table(self,item):
        result = item.data(1, Qt.UserRole)
        # 设置表格行数和列数
        self.tableWidget.setRowCount(len(result))

        # 遍历字典，将每个键值对插入到表格中
        for i, (key, value) in enumerate(result.items()):
            self.tableWidget.setItem(i, 0, QTableWidgetItem(key))
            if not value:
                self.tableWidget.setItem(i, 1, QTableWidgetItem(''))
            else:
                self.tableWidget.setItem(i, 1, QTableWidgetItem(value))
        # 自适应大小
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()
        
        # 设置右键菜单
        self.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        def copy():
            selected = self.tableWidget.currentItem()
            if selected is not None:
                QApplication.clipboard().setText(selected.text())

        menu = QMenu()
        copy_action = menu.addAction('复制')
        copy_action.triggered.connect(copy)
        self.tableWidget.customContextMenuRequested.connect(lambda pos: menu.exec_(self.tableWidget.mapToGlobal(pos)))

    # def build_model(self, lines, parent_item, last_indentation):
    #     while lines:
    #         line = lines.pop(0)
    #         if not line.strip():
    #             continue
    #         indentation = len(line) - len(line.lstrip())
    #         data = self.get_data(line)
    #         item = QTreeWidgetItem()
    #         item.setText(0,self.get_controlname(line))
    #         item.setData(1, Qt.UserRole, data)
    #         if last_indentation < 0:
    #             self.treeWidget.addTopLevelItem(item)
    #             parent_item = item
    #         elif indentation > last_indentation:
    #             parent_item.addChild(item)
    #             parent_item = item  # 更新父级节点
    #         else:
    #             while parent_item and indentation <= last_indentation:
    #                 parent_item = parent_item.parent()
    #                 last_indentation -= 4
    #             if parent_item:
    #                 parent_item.addChild(item)
    #                 parent_item = item  # 更新父级节点
    #             else:
    #                 self.treeWidget.addTopLevelItem(item)
    #                 parent_item = item
    #         last_indentation = indentation
    #         while lines and len(lines[0]) - len(lines[0].lstrip()) > indentation:
    #             self.build_model(lines, parent_item, indentation)
    #             if not lines:
    #                 break
                
    def build_model(self, lines):
        self.treeWidget.setColumnCount(1)

        parents = [self.treeWidget.invisibleRootItem()]
        current_indent = -1

        for line in lines:
            indent = len(line) - len(line.lstrip())

            while indent <= current_indent and len(parents) > 1:
                parents.pop()
                current_indent -= 4
            
            parent = parents[-1]
            item = QTreeWidgetItem(parent, [self.get_controlname(line)])
            data = self.get_data(line)
            item.setData(1, Qt.UserRole, data)
            parents.append(item)
            current_indent = indent
                

    def get_data(self,line):
        lst = line.split("    ")
        result = {}
        for item in lst:
            temp = item.strip()
            if temp:
                key_value = temp.split(':', 1)
                if len(key_value) == 2:
                    key, value = key_value[0], key_value[1]
                    if value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    elif value.lower() == 'none':
                        value = None
                    result[key] = value.strip()
                elif len(key_value) == 1 and key_value[0]:
                    result[key_value[0]] = ''
        try:
            result["ClassName"] = result["ClassName"].strip("'")
            result["Name"] = result["Name"].strip("'")
            result["AutomationId"] = result["AutomationId"].strip("'")
            if result["AutomationId"] == '':
                result["自动化定位代码"] = 'Element("{}",{},"{}","{}")'.format(result["ControlType"],result["Depth"],result["ClassName"] or '',result["Name"] or '')
            else:
                result["自动化定位代码"] = 'Element("{}",{},"{}","{}",AutomationId="{}")'.format(result["ControlType"],result["Depth"],result["ClassName"] or '',result["Name"] or '',result["AutomationId"])
            return result
        except:
            return None



    def get_controlname(self,string):
        control_type = ''
        # class_name = ''
        name = ''

        if string.startswith("PaneControl"):
            string = 'ControlType: ' + string

        lst = string.split("    ")
        result = {}
        for item in lst:
            temp = item.strip()
            if temp:
                key_value = temp.split(':', 1)
                if len(key_value) == 2:
                    key, value = key_value[0], key_value[1]
                    if value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    elif value.lower() == 'none':
                        value = None
                    result[key] = value.strip()
                elif len(key_value) == 1 and key_value[0]:
                    result[key_value[0]] = ''

        try:
            control_type = result["ControlType"]
            name = result["Name"]
            result_string = f"{control_type}|{name}"
        except:
            result_string = ''
        return result_string

if __name__ == '__main__':    
    app = QApplication(sys.argv)
    tree_view = UI_Inspect_Win()
    tree_view.show()
    sys.exit(app.exec_())
