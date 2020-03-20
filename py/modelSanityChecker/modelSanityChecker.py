"""

module docstring here
"""

from PySide2 import QtCore, QtWidgets
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya import cmds
from . import checker
from . import framelayout
reload(checker)
reload(framelayout)


def init():
    """
    Initialize plugins

    """

    if not cmds.pluginInfo("meshChecker", q=True, loaded=True):
        try:
            cmds.loadPlugin("meshChecker")
        except RuntimeError:
            raise RuntimeError("Failed to load plugin")

    if not cmds.pluginInfo("uvChecker", q=True, loaded=True):
        try:
            cmds.loadPlugin("uvChecker")
        except RuntimeError:
            raise RuntimeError("Failed to load plugin")

    if not cmds.pluginInfo("findUvOverlaps", q=True, loaded=True):
        try:
            cmds.loadPlugin("findUvOverlaps")
        except RuntimeError:
            raise RuntimeError("Failed to load plugin")



class CheckerWidget(QtWidgets.QWidget):

    def __init__(self, chk):
        # type: (checker.BaseChecker) -> (None)
        super(CheckerWidget, self).__init__()

        self.checker = chk
        self.createUI()

        # self.setMinimumHeight(50)

    def createUI(self):
        layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.LeftToRight)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(QtCore.Qt.AlignTop)

        self.frame = framelayout.FrameLayout(self.checker.name)
        if not self.checker.isEnabled:
            self.setEnabled(False)

        self.checkButton = QtWidgets.QPushButton("Check")
        # self.checkButton.setSizePolicy(
        #     QtWidgets.QSizePolicy.Maximum,
        #     QtWidgets.QSizePolicy.Expanding)
        # self.checkButton.setMinimumWidth(130)
        self.checkButton.clicked.connect(self.check)
        self.fixButton = QtWidgets.QPushButton("Fix")
        self.fixButton.setEnabled(False)

        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addWidget(self.checkButton)
        buttonLayout.addWidget(self.fixButton)

        self.errorList = QtWidgets.QListWidget()
        self.errorList.itemClicked.connect(self.errorSelected)

        self.frame.addWidget(self.errorList)
        self.frame.addLayout(buttonLayout)

        layout.addWidget(self.frame)

        self.setLayout(layout)

    def check(self):
        if not self.checker.isEnabled:
            return

        sel = cmds.ls(sl=True, fl=True, long=True)

        if not sel:
            cmds.warning("Nothing is selected")
            return

        children = cmds.listRelatives(
            sel[0], children=True, ad=True, fullPath=True, type="transform") or []
        children.append(sel[0])

        # Clear list items
        self.errorList.clear()

        errs = self.checker.checkIt(children)

        if errs:
            for err in errs:
                self.errorList.addItem(err)
                if self.checker.isWarning:
                    self.frame.setStatusIcon("warning")
                else:
                    self.frame.setStatusIcon("bad")
        else:
            self.frame.setStatusIcon("good")

    def errorSelected(self, *args):
        """
        Select error components

        """

        err = args[0]
        if err.components is None:
            cmds.select(err.longName, r=True)
        else:
            cmds.select(err.components, r=True)


class ModelSanityChecker(QtWidgets.QWidget):
    """ Main sanity checker class """

    def __init__(self, parent=None):
        super(ModelSanityChecker, self).__init__(parent)

        self.checkers = [CheckerWidget(i()) for i in checker.CHECKERS]
        self.createUI()

    def createUI(self):
        """
        GUI method

        """

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(1)

        scrollLayout = QtWidgets.QVBoxLayout()
        for widget in self.checkers:
            scrollLayout.addWidget(widget)

        content = QtWidgets.QWidget()
        content.setLayout(scrollLayout)

        scroll.setWidget(content)

        checkAllButton = QtWidgets.QPushButton("Check All")
        checkAllButton.clicked.connect(self.checkAll)
        checkAllButton.setMinimumHeight(40)

        mainLayout.addWidget(scroll)
        mainLayout.addWidget(checkAllButton)

        self.setLayout(mainLayout)

    def checkAll(self):
        """
        Check all

        """

        for widget in self.checkers:
            widget.check()


class CentralWidget(QtWidgets.QWidget):
    """ Central widget """

    def __init__(self, parent=None):
        """ Init """

        super(CentralWidget, self).__init__(parent)

        self.createUI()
        self.layoutUI()

    def createUI(self):
        """ Crete widgets """

        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.addTab(ModelSanityChecker(self), "SanityChecker")

    def layoutUI(self):
        """ Layout widgets """

        mainLayout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.TopToBottom)
        mainLayout.setContentsMargins(5, 5, 5, 5)
        mainLayout.addWidget(self.tabWidget)

        self.setLayout(mainLayout)


class MainWindow(MayaQWidgetDockableMixin, QtWidgets.QMainWindow):
    """
    Main window

    """

    def __init__(self, parent=None):
        """ init """

        super(MainWindow, self).__init__(parent)

        self.thisObjectName = "sanityCheckerWindow"
        self.winTitle = "Sanity Checker"
        self.workspaceControlName = self.thisObjectName + "WorkspaceControl"

        self.setObjectName(self.thisObjectName)
        self.setWindowTitle(self.winTitle)

        self.setWindowFlags(QtCore.Qt.Window)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # Create and set central widget
        self.cWidget = CentralWidget()
        self.setCentralWidget(self.cWidget)

        self.setupMenu()

    def setupMenu(self):
        """ Setup menu """

        menu = self.menuBar()

        # About
        aboutAction = QtWidgets.QAction("&About", self)
        aboutAction.setStatusTip('About this script')
        aboutAction.triggered.connect(self.showAbout)

        menu.addAction("File")
        helpMenu = menu.addMenu("&Help")
        helpMenu.addAction(aboutAction)

    def showAbout(self):
        """
        About message
        """

        QtWidgets.QMessageBox.about(
            self,
            'About ',
            'test\n')

    def run(self):
        try:
            cmds.deleteUI(self.workspaceControlName)
        except RuntimeError:
            pass

        self.show(dockable=True)
        cmds.workspaceControl(
            self.workspaceControlName,
            edit=True,
            dockToControl=['Outliner', 'right'])
        self.raise_()


def main():
    try:
        init()
    except RuntimeError:
        return

    w = MainWindow()
    w.run()


if __name__ == "__main__":
    main()
