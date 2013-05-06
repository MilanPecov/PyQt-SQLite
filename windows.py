# coding=utf-8
from PyQt4 import QtGui,QtCore,Qt
from base import Article

def d2u(text):
    "konverzija vo UTF-8"
    return text.decode('utf-8')

class Login(QtGui.QDialog):
    def __init__(self,Parent):
        QtGui.QDialog.__init__(self,Parent)

        mainLayout = QtGui.QVBoxLayout(self)
        loginButtons = QtGui.QVBoxLayout()

        self.textName = QtGui.QLineEdit(self)
        self.textName.setPlaceholderText(d2u('Корисничко име'))
        self.textName.setFixedWidth(200)

        self.textPass = QtGui.QLineEdit(self)
        self.textPass.setPlaceholderText(d2u('Лозинка'))
        self.textPass.setEchoMode(QtGui.QLineEdit.Password)
        self.textPass.setFixedWidth(200)

        self.buttonLogin = QtGui.QPushButton(d2u('Најави се'), self)
        self.buttonLogin.setFixedWidth(200)
        self.buttonLogin.clicked.connect(self.handleLogin)

        self.picture = QtGui.QLabel()
        self.picture.setPixmap(QtGui.QPixmap("icons/drinks.jpg" ))
        self.picture.setAlignment(QtCore.Qt.AlignCenter)
 
        #za crna pozadina
        self.setAutoFillBackground(True)
        self.setBackgroundRole(QtGui.QPalette.ToolTipText)

        mainLayout.addWidget(self.picture)
        loginButtons.addWidget(self.textName)
        loginButtons.addWidget(self.textPass)
        loginButtons.addWidget(self.buttonLogin)
        loginButtons.setAlignment(QtCore.Qt.AlignCenter)

        mainLayout.addLayout(loginButtons)
        self.setLayout(mainLayout)

    def handleLogin(self):
        if (self.textName.text() == 'admin' and
            self.textPass.text() == 'milan'):
            self.accept()
        else:
            QtGui.QMessageBox.warning(
                self, d2u('Грешка'), d2u('Погрешно корисничко име или лозинка'))

class CalendarDialog(QtGui.QDialog):
    def __init__(self,Parent):
        QtGui.QDialog.__init__(self,Parent)
        self.setWindowTitle(d2u('Календар'))
        self.setWindowIcon(QtGui.QIcon("icons/Add.ico"))
        self.resize(300,100)
        
        vbox = QtGui.QVBoxLayout()
        
        self.cal = QtGui.QCalendarWidget()
        vbox.addWidget(self.cal)

        self.buttonOK = QtGui.QPushButton(d2u("Изврши"))
        self.connect(self.ButtonOK,QtCore.SIGNAL("clicked()"),self.OKClicked)
        self.buttonCancel = QtGui.QPushButton(d2u("Излез"))
        self.connect(self.ButtonCancel,QtCore.SIGNAL("clicked()"),self.reject)

        OKCancelLayout = QtGui.QHBoxLayout()
        OKCancelLayout.addStretch()
        OKCancelLayout.addWidget(self.ButtonOK)
        OKCancelLayout.addWidget(self.ButtonCancel)

        vbox.addLayout(OKCancelLayout)
        self.setLayout(vbox)        

        self.selectedDate=self.cal.selectedDate()

    def OKClicked(self):
        self.selectedDate = self.cal.selectedDate()
        self.accept()

class InactivityFilter(QtCore.QTimer):
    """
    Tajmer sto se restartira sekojpat koga
    korisnikot ima nekoja aktivnost vo glavnata aplikacija
    """
    def __init__(self, parent=None):
        super(InactivityFilter, self).__init__(parent)
        self.setInterval(50000) #milliseconds
        self.start()

    def eventFilter(self, object, event):
        if event.type() in (QtCore.QEvent.MouseMove, QtCore.QEvent.MouseButtonPress, QtCore.QEvent.HoverMove, QtCore.QEvent.KeyPress, QtCore.QEvent.KeyRelease, ):
            self.emit(QtCore.SIGNAL("activity"))
            self.start(5000)
        return QtCore.QObject.eventFilter(self, object, event)

class AddEditArticle(QtGui.QDialog):
    def __init__(self,Parent=None,aArticle=None):
        QtGui.QDialog.__init__(self,Parent)
        self.myArticle=Article()
        if not aArticle:
            self.setWindowTitle(d2u("Внеси Артикл"))
            self.setWindowIcon(QtGui.QIcon("icons/Add.ico"))
        else:
            self.setWindowTitle(d2u("Промени Артикл"))
            self.setWindowIcon(QtGui.QIcon("icons/Edit.ico"))
            self.myArticle=aArticle
        self.CreateCentralWidget()
        self.FillArticleWidgets()
    
    def CreateCentralWidget(self):
        MainLayout = QtGui.QGridLayout()
        OKCancelLayout = QtGui.QHBoxLayout()
        
        self.TreeArticle = QtGui.QTreeWidget()
        self.TreeArticle.setColumnCount(2)
        #0 Article First Line
        #1 ID
        self.TreeArticle.setSortingEnabled(True)
        self.TreeArticle.sortByColumn(0)
        self.TreeArticle.setHeaderHidden(True)
        self.TreeArticle.hideColumn(1)
        
        self.TextName  = QtGui.QLineEdit()
        self.TextPrice = QtGui.QLineEdit()
        self.TextTax   = QtGui.QLineEdit()
        
        self.ButtonOK = QtGui.QPushButton(d2u("Изврши"))
        self.connect(self.ButtonOK,QtCore.SIGNAL("clicked()"),self.OKClicked)
        self.ButtonCancel = QtGui.QPushButton(d2u("Излез"))
        self.connect(self.ButtonCancel,QtCore.SIGNAL("clicked()"),self.reject)
        
        OKCancelLayout.addStretch()
        OKCancelLayout.addWidget(self.ButtonOK)
        OKCancelLayout.addWidget(self.ButtonCancel)
        
        MainLayout.addWidget(QtGui.QLabel(d2u("Категорија")),0,0)
        MainLayout.addWidget(self.TreeArticle,1,0,3,1)
        MainLayout.addWidget(QtGui.QLabel(d2u("Име")),1,2)
        MainLayout.addWidget(self.TextName,1,3)
        MainLayout.addWidget(QtGui.QLabel(d2u("Цена")),2,2)
        MainLayout.addWidget(self.TextPrice,2,3)
        MainLayout.addWidget(QtGui.QLabel(d2u("Данок")),3,2)
        MainLayout.addWidget(self.TextTax,3,3)
        MainLayout.addLayout(OKCancelLayout,4,0,1,5)
        
        self.setLayout(MainLayout)

    def FillArticleWidgets(self):
        self.TextName.setText(self.myArticle.Name)
        self.TextPrice.setText(self.myArticle.Price)
        self.TextTax.setText(self.myArticle.Tax)
        
        #Fill tree
        RootWidget = QtGui.QTreeWidgetItem(self.TreeArticle,[d2u("Основа"),"0"])
        self.TreeArticle.setCurrentItem(RootWidget)
        for aArticle in self.parent().TreeArticleList.findItems("0",Qt.Qt.MatchExactly,2):
            if str(aArticle.text(1))==self.myArticle.ID:
                continue
            QtGui.QTreeWidgetItem(RootWidget,[aArticle.text(0),aArticle.text(1)])
        self.TreeArticle.expandAll()
        if self.myArticle.ID!='':
            self.TreeArticle.setCurrentItem(self.TreeArticle.findItems(self.myArticle.Parent,Qt.Qt.MatchRecursive,1)[0])
        
    def OKClicked(self):
        self.myArticle.Parent=unicode(self.TreeArticle.selectedItems()[0].text(1))
        self.myArticle.Name=unicode(self.TextName.text())
        self.myArticle.Price=unicode(self.TextPrice.text())
        self.myArticle.Tax=unicode(self.TextTax.text())
 
        self.accept()