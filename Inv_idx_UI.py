import json
import sys

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QMainWindow, QLineEdit, QApplication, QWidget, QGridLayout, QPushButton, QDialog, \
    QVBoxLayout, QTextEdit, QFileDialog
from pathlib import Path

import re
import string
from collections import defaultdict

# define a QDialog which will pop up once a button is clicked. It entails a QTextBox with the text of the story inside.
class TextDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setFixedSize(QSize(500,500))
        self.text=QTextEdit()
        self.layout=QVBoxLayout()
        self.layout.addWidget(self.text)
        self.setLayout(self.layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        #Window layout
        self.setWindowTitle("Word finder")
        self.setFixedSize(QSize(400,400))

        #Widget layout
        self.window_layout=QGridLayout()
        self.window_layout.setRowMinimumHeight(1,300)

            #define search line
        self.search_line=QLineEdit()
        self.search_line.setFixedSize(QSize(300,50))
        self.window_layout.addWidget(self.search_line,0,1,alignment=Qt.AlignmentFlag.AlignCenter)

            #define add file button
        self.add_file_button=QPushButton("Add File")
        self.add_file_button.clicked.connect(self.write_new_dict)
        self.window_layout.addWidget(self.add_file_button,0,2)

            #define buttons layout
        self.buttons_layout=QVBoxLayout()
        self.buttons_layout.addStretch()
        self.window_layout.addLayout(self.buttons_layout,1,1)

        #Widget functionality
        self.search_line.textChanged.connect(self.look_for_words)

        #Central widget
        self.widget=QWidget()
        self.widget.setLayout(self.window_layout)
        self.setCentralWidget(self.widget)

        # define words as a dict with 2 keys, values of equal length: "fileID" and "word"
        file = open("Words.json")
        json_str = file.read()
        self.words = json.loads(json_str)

        # define stories_list as list with names of stories
        self.stories_path = Path.cwd() / Path("stories")
        self.stories_list = []
        for i in self.stories_path.glob("*.txt") :
            self.stories_list.append(i.stem)

    def remove_widgets(self):
        """
        This function removes all widgets from a self.buttons_layout
        ("A widget is removed once its parent is removed"!)
        """
        for i in reversed(range(self.buttons_layout.count()-1)):
            self.buttons_layout.takeAt(i).widget().setParent(None)

    def find_files(self):
        """
        :return: A list with stories names that entail the word in search_line. Covers capitalization.
        """
        lookup = self.search_line.text().lower()
        if len(lookup)>0:
            if lookup in self.words:
                in_stories_ind=self.words[lookup]
                in_stories=[]
                for ind in in_stories_ind:
                    in_stories.append(self.stories_list[ind])
                return in_stories
            else:
                return True
        else :
            return True

    def look_for_words(self):
        """
        Removes the buttons in buttons_layout and re-adds each item in idx (strings)
        """
        idx=self.find_files()
        if idx==True:
            self.remove_widgets()
        else:
            self.remove_widgets()
            for i in range(len(idx)):
                button=QPushButton(f"{idx[i]}")
                self.buttons_layout.insertWidget(self.buttons_layout.count()-1,button)
                button.clicked.connect(self.open_file)

    def open_file(self):
        """
        Opens a TextDialog with text that has input in search_line
        """
        story_dialog=TextDialog(self)
        button_sender=self.sender()
        for i in self.stories_path.glob("*.txt"):
            if button_sender.text()==i.stem:
                story_name=i
                break
        text=story_name.open()
        text=text.read()
        story_dialog.text.setText(text)
        story_dialog.exec()
        #ok comment

    def read_text_file(self,file_path) :
        """
        :param file_path: path to a story (dtype = pathlib.Path)
        :return: story: a string of the story without punctuation.
        """
        # open file as string
        with Path(file_path).open() as file :
            story = file.read()

        story = " ".join(line.strip() for line in story.splitlines() if line.split())

        # remove punctuation
        regex_pattern = f"[{re.escape(string.punctuation)}]"
        story = re.sub(regex_pattern, "", story)
        return story

    def create_dict(self, text, word_idx, fileID) :
        """
        :param text: string of a story without punctuation
        :param word_idx: a dictionary of the words already present in different stories (or an empty defaultdict(list))
        :param fileID: the index of the file in the "stories" directory (retrieved top-to-bottom)
        :return: word_idx which now includes all the words present in text.
        """
        text = text.lower()
        text_list = set(text.split())
        print(len(text_list))
        for i in text_list :
            if fileID not in word_idx[i] :
                word_idx[i].append(fileID)
        return word_idx

    def write_new_dict(self) :
        # adds story to index for each story in directory
        file_names=self.open_file_dialog()
        if file_names!=None:
            words_idx = defaultdict(list)
            for idx,i in enumerate(file_names):
                text=self.read_text_file(i)
                words_idx=self.create_dict(text,words_idx,idx)

            print(len(words_idx))
            words_idx=json.dumps(words_idx)
            myjson = open("Words.json", "w")
            myjson.write(words_idx)
            myjson.close()
            myjson = open("Words.json")
            json_str = myjson.read()
            self.words = json.loads(json_str)
            print(len(self.words.keys()))
        else:
            print("Import failed")

    def open_file_dialog(self):
        file_dialog=QFileDialog.getOpenFileNames(None,"Select file","stories","*.txt")
        if len(file_dialog[0])>0:
            file_names=file_dialog[0]
            return file_names
        return None

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet("""
    QMainWindow {
    background-color:	#282b30;
    }
    QLineEdit {
    border-style:outset;
    border-color:#36393e;
    border-width:4px;
    background-color:#424549;
    border-radius:10px;
    color:white;
    }
    QPushButton {
    border-style:outset;
    border-color:#36393e;
    border-width:4px;
    background-color:#424549;
    border-radius:10px;
    color:white;
    }
    QDialog {
    background-color:	#282b30;
    }
    QTextEdit{
    border-style:outset;
    border-color:#36393e;
    border-width:4px;
    background-color:#424549;
    border-radius:10px;
    color:white;
    }
    """)
    window = MainWindow()
    window.show()
    app.exec()

if __name__=="__main__":
    main()