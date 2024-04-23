from Ui_MBR_filter import Ui_mainwindow
import resources_rc

from PyQt5.QtWidgets import QLineEdit

from PyQt5.QtGui import QDragEnterEvent, QDropEvent

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QPixmap
# try to import qdarktheme, if not exist, skip it
try:
    import qdarktheme
except ImportError:
    pass

import sys
import os
import pandas as pd


class MBR_filter(Ui_mainwindow):
    def __init__(self, mainwindow):
        super().__init__()
        self.setupUi(mainwindow)
        self.progressBar.setVisible(False)
        # set size of the window
        mainwindow.resize(900, 600)
        # set icon: qt_resource_data
        self.icon = QIcon(":/icon/icon.png")
        mainwindow.setWindowIcon(self.icon)   
        
        # reset title
        mainwindow.setWindowTitle("MBR Filter V1.3")
        
        self.pep_table = None
        self.meta_table = None
        self.no_meta = False
        self.meta_list = None
        
        # set default values
        self.intensity_cols_start = None
        self.detct_cols_start = None
        self.filter_meta = None
        self.mini_num = None
        self.filter_flag = None
        self.save_path = None
        
        # chaed to page 1
        self.default_path = os.path.expanduser("~/Desktop")
        self.toolBox.setCurrentIndex(0)
        
        self.lineEdit_pep_path = self.make_line_edit_drag_drop(self.lineEdit_pep_path, mode='file')
        self.lineEdit_meta_path = self.make_line_edit_drag_drop(self.lineEdit_meta_path, mode='file')
        self.lineEdit_save_path = self.make_line_edit_drag_drop(self.lineEdit_save_path, mode='folder', default_filename='filtered_pep.tsv')
        
        self.pushButton_open_pep_path.clicked.connect(self.open_pep_path)
        self.pushButton_open_meta_path.clicked.connect(self.open_meta_path)
        self.pushButton_open_save_path.clicked.connect(self.open_save_path)
        self.pushButton_load_tables.clicked.connect(self.run_load_table)
        self.pushButton_run_filter.clicked.connect(self.run_filter)
        

    def open_pep_path(self):
        file_path = QtWidgets.QFileDialog.getOpenFileName(None, "Select pep file", self.default_path, "pep files (*.tsv *.csv, *.txt)")
        if file_path[0]:
            self.lineEdit_pep_path.setText(file_path[0])
            self.default_path = os.path.dirname(file_path[0])
    
    from PyQt5 import QtWidgets, QtCore

    def open_meta_path(self):
        file_path = QtWidgets.QFileDialog.getOpenFileName(None, "Select meta file", self.default_path, "meta files (*.tsv *.csv, *.txt)")
        if file_path[0]:
            self.lineEdit_meta_path.setText(file_path[0])
            self.default_path = os.path.dirname(file_path[0])

    def open_save_path(self):
        # select a folder, enable to input a file name, default file name is "filtered_pep.tsv"
        default_file_path = os.path.join(self.default_path, "filtered_pep.tsv")
        file_path = QtWidgets.QFileDialog.getSaveFileName(None, "Select save path", default_file_path, "tsv files (*.tsv)", options=QtWidgets.QFileDialog.DontConfirmOverwrite)
        if file_path[0]:
            self.lineEdit_save_path.setText(file_path[0])
            self.default_path = os.path.dirname(file_path[0])

                
    
        
    def make_line_edit_drag_drop(self, old_lineEdit, mode='file', default_filename=''):
        new_line_edit = FileDragDropLineEdit(old_lineEdit.parent(), mode, default_filename)
        new_line_edit.setText(old_lineEdit.text())
        new_line_edit.setReadOnly(old_lineEdit.isReadOnly())

        # get the position of old_lineEdit in its layout
        layout = old_lineEdit.parent().layout()
        index = layout.indexOf(old_lineEdit)
        position = layout.getItemPosition(index)

        # remove old_lineEdit from its layout
        old_lineEdit.deleteLater()

        # add new_line_edit to its layout
        layout.addWidget(new_line_edit, *position[0:2])  # position is a tuple of 4 elements including (row, column, rowspan, columnspan)

        return new_line_edit
        
        
    def update_save_path(self):
        # set same path to lineEdit_save_path
        # add "filtered_" to the file name
        pep_path = self.lineEdit_pep_path.text()
        file_name = os.path.basename(pep_path)
        file_name = "filtered_" + file_name
        save_path = os.path.join(os.path.dirname(pep_path), file_name)
        self.lineEdit_save_path.setText(save_path)
        

    def show_message(self,message,title='Information'):
        self.msg = QtWidgets.QMessageBox(mainwindow)
        self.msg.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)
        self.msg.setEnabled(False)

        self.msg.setWindowModality(Qt.NonModal)
        self.msg.setWindowTitle(title)
        if not hasattr(self, 'msgbox_style'):
            self.msgbox_style = "QLabel{min-width: 400px; color: black; font-size: 12px;} QMessageBox{background-color: white;}"
        self.msg.setStyleSheet(self.msgbox_style)
        self.msg.setText(message)
        
        self.msg.setStandardButtons(QtWidgets.QMessageBox.NoButton)
        self.msg.show()  
        QTimer.singleShot(200, self.msg.accept)
        QtWidgets.QApplication.processEvents()
        
        
        
    def run_load_table(self):
        pep_path  = self.lineEdit_pep_path.text()
        meta_path = self.lineEdit_meta_path.text()
        # show message box without blocking the main window
        
        
        self.show_message("Loading tables...")
        if not os.path.exists(pep_path):
            QtWidgets.QMessageBox.warning(None, "Warning", "The pep file does not exist.")
            return
        else:
            self.pep_table = pd.read_csv(pep_path, sep='\t')
            
            
        if not os.path.exists(meta_path):
            self.show_message("The meta file does not exist.")
            self.meta_list = ['MS/MS Only']
            self.no_meta = True
        else:
            self.meta_table = pd.read_csv(meta_path, sep='\t')
            self.no_meta = False
            # check if at least 2 columns in the meta table
            if self.meta_table.shape[1] < 2:
                QtWidgets.QMessageBox.warning(None, "Warning", "The meta table should have at least 2 columns.\n\
                The first column is the sample name and the second column is the meta data.")
                return
            # check if some rows are duplicated, remove the duplicated rows
            if self.meta_table.duplicated().sum() > 0:
                self.meta_table = self.meta_table.drop_duplicates()
                QtWidgets.QMessageBox.warning(None, "Warning", "Some rows in the meta table are duplicated and removed.")
                
            self.meta_table.set_index(self.meta_table.columns[0], inplace=True)
            self.meta_list = self.meta_table.columns.tolist()+ ['MS/MS Only']
            
        
        # set comboBox_meta
        self.comboBox_meta.clear()
        self.comboBox_meta.addItems(self.meta_list)
        
        # set default values for save path
        self.update_save_path()
        # chane to page 2
        self.toolBox.setCurrentIndex(1)
        

    def read_params(self):
        self.intensity_cols_start = self.lineEdit_intensity_cols_start.text()
        self.detct_cols_start = self.lineEdit_detection_cols_start.text()
        self.filter_meta = self.comboBox_meta.currentText()
        self.mini_num = self.spinBox_mini_num_for_filter.value()
        self.filter_flag = self.lineEdit_filter_texet.text()
        self.save_path = self.lineEdit_save_path.text()
    
    def filter_by_meta(self):
        self.show_message(f"Filtering by meta data: {self.filter_meta}...")
        # filter intensity columns that have at least min_num samples with detected type 'By MS/MS' by grouping by the meta data
        #create a dict to store the group
        pep_df = self.pep_table.copy()

        group_dict = {}
        group_list = self.meta_table[self.filter_meta].unique().tolist()
        for group in group_list:
            group_dict[group] = self.meta_table[self.meta_table[self.filter_meta] == group].index.tolist()
            
        # print(group_dict)
        intensity_cols = [col for col in pep_df.columns if col.startswith(self.intensity_cols_start)]
        # remove the intensity columns that are equal to intensity_cols_start
        intensity_cols = [col for col in intensity_cols if col != self.intensity_cols_start]
        # print(intensity_cols)
        detct_cols = [col for col in pep_df.columns if col.startswith(self.detct_cols_start)]
        # print(detct_cols)
        # check if the intensity columns and the meta data columns have the same samples
        sample_num_pep = len(intensity_cols)
        sample_num_meta = self.meta_table.shape[0]
        if sample_num_pep != sample_num_meta:
            QtWidgets.QMessageBox.warning(None, "Warning", f"{sample_num_pep} samples in the pep table but {sample_num_meta} samples in the meta table.\n\nPlease check the meta data.")
            return
        
        # filter the intensity columns by the meta data
        for group, samples in group_dict.items():
            print(f'Start filtering group: [{group}], pelase wait...')
            # print(samples)
            # intensity_cols_group = samples in intensity_cols
            intensity_cols_group = []
            detct_cols_group = []
            for sample in samples:
                sample = sample.strip()
                for col in intensity_cols:
                    if sample == col.replace(self.intensity_cols_start, '').strip():
                        intensity_cols_group.append(col)
                for col in detct_cols:
                    if sample == col.replace(self.detct_cols_start, '').strip():
                        detct_cols_group.append(col)

            # check if the intensity columns and the detection columns have the same samples
            len_lisy = [len(intensity_cols_group), len(detct_cols_group), len(samples)]
            if len(set(len_lisy)) != 1:
                raise ValueError('Error: The number of samples in the intensity columns and the detection columns are not the same.')
            # print(intensity_cols_group)
            # print(detct_cols_group) 
            
            # 计算每行中filter_flag的数量
            detected_flags_count = pep_df[detct_cols_group].apply(lambda x: x == self.filter_flag).sum(axis=1)
            print(f'Number of [{self.filter_flag}] in first 5 rows: {detected_flags_count.head()}')
            # 确定哪些行的detected_flags_count小于min_num
            rows_to_update = detected_flags_count < self.mini_num
            
            # 创建一个与pep_df[detct_cols_group]相同形状的DataFrame，其中True表示detection type是filter_flag
            is_filter_flag = pep_df[detct_cols_group] == self.filter_flag
            
            # 对于需要更新的行，将detection type不是filter_flag的对应intensity列设置为0
            for col in intensity_cols_group:
                detct_col = col.replace(self.intensity_cols_start, self.detct_cols_start)
                pep_df.loc[rows_to_update & (~is_filter_flag[detct_col]), col] = 0
                
        # remove the rows that all the intensities are 0
        pep_df = pep_df.loc[pep_df[intensity_cols].sum(axis=1) > 0]
        pep_df = pep_df.reset_index(drop=True)
        return pep_df

            

    def filter_only_MSMS(self):      
        self.show_message("Filtering, keep only MS/MS peptides...")
        pep_df = self.pep_table.copy()
        intensity_cols = [col for col in pep_df.columns if col.startswith(self.intensity_cols_start)]
        # remove the intensity columns that are equal to intensity_cols_start
        intensity_cols = [col for col in intensity_cols if col != self.intensity_cols_start]
        print(intensity_cols)
        detct_cols = [col for col in pep_df.columns if col.startswith(self.detct_cols_start)]
        print(detct_cols)
        sample_list = [col.replace(self.intensity_cols_start, '').strip() for col in intensity_cols]
        print(sample_list)
        for i in range(len(intensity_cols)):
            pep_df.loc[pep_df[detct_cols[i]] != self.filter_flag, intensity_cols[i]] = 0
        # remove the rows that all the intensities are 0
        pep_df = pep_df.loc[pep_df[intensity_cols].sum(axis=1) > 0]
        pep_df = pep_df.reset_index(drop=True)
        return pep_df
        
    def check_meta_match(self):
        if self.no_meta:
            return True
        else:
            sampel_list_from_meta = self.meta_table.index.tolist()
            sample_list_from_pep = [col.replace(self.intensity_cols_start, '').strip() for col in self.pep_table.columns if col.startswith(self.intensity_cols_start)]
            # remove "" in sample_list_from_pep
            sample_list_from_pep = [sample for sample in sample_list_from_pep if sample != ""]
            # compare if they are the same (ignore the order of samples)
            if set(sampel_list_from_meta) != set(sample_list_from_pep):
                # find the difference in each list
                diff_meta = list(set(sampel_list_from_meta) - set(sample_list_from_pep))
                diff_pep = list(set(sample_list_from_pep) - set(sampel_list_from_meta))
                msg = "The samples in the pep table and the meta table are not the same." 
                msg += f"\n\nThe samples in the meta table but not in the pep table: {diff_meta}" if len(diff_meta) > 0 else ""
                msg += f"\n\nThe samples in the pep table but not in the meta table: {diff_pep}" if len(diff_pep) > 0 else ""
                QtWidgets.QMessageBox.warning(None, "Warning", msg)
                return False
        
    def run_filter(self):
        if self.pep_table is None:
            QtWidgets.QMessageBox.warning(None, "Warning", "Please load the pep table first.")
            return None
        
        self.read_params()
        
        if self.check_meta_match() is False:
            return
        
        try:
            if self.filter_meta == 'MS/MS Only':
                pep_df = self.filter_only_MSMS()
            else:
                pep_df = self.filter_by_meta()
            
            if pep_df is None:
                QtWidgets.QMessageBox.warning(None, "Warning", "Filtering is failed.")
                return
            
        except Exception as e:
            QtWidgets.QMessageBox.warning(None, "Warning", f"Filtering is failed.\n{str(e)}")
            return
        
        msg = f'Filtering is done.\n\n[{self.pep_table.shape[0] - pep_df.shape[0]}] rows are removed due to all the intensities are Zero.\n\n[{pep_df.shape[0]}] rows were remained.'
        print(msg)
        # save the filtered table
        pep_df.to_csv(self.save_path, sep='\t', index=False)
        # QMessageBox
        QtWidgets.QMessageBox.information(None, "Information", msg + "\n\n" + "The filtered table is saved as " + self.save_path)
        
        


class SplashScreen(QtWidgets.QDialog):
    def __init__(self):
        super().__init__(None, QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # 确保窗口背景透明
        self.setFixedSize(500, 500)

        layout = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel(self)
        self.label.setPixmap(QPixmap(":/icon/icon.png").scaled(500, 500, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        # 设置QLabel背景为透明
        self.label.setStyleSheet("background-color: transparent;")

        layout.addWidget(self.label)
        self.setLayout(layout)



class FileDragDropLineEdit(QLineEdit):
    def __init__(self, parent=None, mode='file', default_filename=''):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.mode = mode  # 'file' 或 'folder'
        self.default_filename = default_filename

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0].toLocalFile()
            
            if self.mode == 'folder':
                if self.default_filename == '':
                    url = os.path.dirname(url)
                else:
                    # if url is a folder, append default file name
                    if os.path.isdir(url):
                        url = os.path.join(url, self.default_filename)

                    # if url is a file, append default file name to its parent folder
                    elif os.path.isfile(url):
                        url = os.path.join(os.path.dirname(url), self.default_filename)
                    

            self.setText(url)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    if 'qdarktheme' in sys.modules:
        qdarktheme.setup_theme(theme='auto')

    splash = SplashScreen()
    splash.show()
    app.processEvents()  # make sure the splash screen is displayed

    mainwindow = QtWidgets.QWidget()
    ui = MBR_filter(mainwindow)

    # close the splash screen
    splash.close()
    mainwindow.show()

    sys.exit(app.exec_())

