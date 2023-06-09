from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QTextEdit, QPushButton, QProgressBar, QFileDialog, QMessageBox, QVBoxLayout, QWidget
from PyQt6.QtCore import QThread, pyqtSignal
import sys
import os

input_files = []
output_file = ""
progress_value = 0
progress_max = 100


class FileBinder(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("File Binder")
        self.setFixedSize(400, 450)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.file_label = QLabel("Input Files:", self)
        layout.addWidget(self.file_label)

        self.file_list = QTextEdit(self)
        layout.addWidget(self.file_list)

        self.select_files_button = QPushButton("Select Files", self)
        layout.addWidget(self.select_files_button)
        self.select_files_button.clicked.connect(self.select_files)

        self.output_label = QLabel("Output File:", self)
        layout.addWidget(self.output_label)

        self.output_file_entry = QTextEdit(self)
        self.output_file_entry.setFixedHeight(30)
        layout.addWidget(self.output_file_entry)

        self.select_output_button = QPushButton("Select Output File", self)
        layout.addWidget(self.select_output_button)
        self.select_output_button.clicked.connect(self.select_output_file)

        layout.addStretch()

        self.progress_label = QLabel("Progress:", self)
        layout.addWidget(self.progress_label)

        self.progress = QProgressBar(self)
        layout.addWidget(self.progress)

        self.bind_button = QPushButton("Bind", self)
        layout.addWidget(self.bind_button)
        self.bind_button.clicked.connect(self.start_binding)

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", "Executable Files (*.exe);;Batch Files (*.bat)")
        input_files.extend(files)
        self.file_list.setPlainText("\n".join(input_files))

    def select_output_file(self):
        file, _ = QFileDialog.getSaveFileName(self, "Select Output File", "", "Executable Files (*.exe)")
        if file:
            global output_file
            output_file = file
            self.output_file_entry.setPlainText(output_file)

    def start_binding(self):
        self.bind_button.setEnabled(False)
        self.select_files_button.setEnabled(False)
        self.select_output_button.setEnabled(False)

        self.worker_thread = WorkerThread()
        self.worker_thread.progress_updated.connect(self.update_progress)
        self.worker_thread.binding_completed.connect(self.binding_completed)
        self.worker_thread.message_generated.connect(self.print_message)
        self.worker_thread.start()

    def update_progress(self, value):
        self.progress.setValue(value)

    def binding_completed(self):
        self.bind_button.setEnabled(True)
        self.select_files_button.setEnabled(True)
        self.select_output_button.setEnabled(True)

        QMessageBox.information(self, "File Binder", "File binding process completed.")

    def print_message(self, message):
        print(message)

class WorkerThread(QThread):
    progress_updated = pyqtSignal(int)
    binding_completed = pyqtSignal()
    message_generated = pyqtSignal(str)

    def run(self):
        global progress_value, progress_max
        progress_value = 0
        progress_max = len(input_files)
        self.progress_updated.emit(progress_value)

        try:
            if not output_file:
                raise Exception("Output file is not selected.")

            with open(output_file, "wb") as output:
                for i, file in enumerate(input_files, start=1):
                    if not os.path.isfile(file):
                        raise Exception(f"Input file not found: {file}")

                    with open(file, "rb") as input_file:
                        output.write(input_file.read())
                    progress_value = int(i / progress_max * 100)
                    self.progress_updated.emit(progress_value)
        except Exception as e:
            self.message_generated.emit(f"Error: {str(e)}")
        else:
            self.binding_completed.emit()


app = QApplication(sys.argv)
window = FileBinder()
window.show()
sys.exit(app.exec())
