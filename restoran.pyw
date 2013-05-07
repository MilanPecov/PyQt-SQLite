# coding=utf-8
'''
@author: Milan
'''

import sys
import threading
from PyQt4 import QtGui, QtCore, Qt, QtSql
from windows import Login, CalendarDialog, InactivityFilter, AddEditArticle, UsersDialog
from base import Article, Transaction, User

inactivity_timeout=1 #dali da ima log

def d2u(text):
    "konverzija vo UTF-8"
    return text.decode('utf-8')


class MainWindow(QtGui.QMainWindow):
    def __init__(self,Parent=None):
        QtGui.QMainWindow.__init__(self,Parent)
        self.setWindowTitle(d2u("Ресторан"))
        self.setWindowIcon(QtGui.QIcon("icons/Restoran.ico"))
        
        self.DatabaseName = "db/Base.adb"
        self.Database = QtSql.QSqlDatabase.addDatabase("QSQLITE");

        self.CreateCentralWidget()
        self.CreateActions()
        self.CreateToolbar()
        #self.CreateMenu()
        self.DatabaseDefaultOpen()

        if (inactivity_timeout): 
            self.event_filter = InactivityFilter()
            QtCore.QCoreApplication.instance().installEventFilter(self.event_filter)
            self.connect(self.event_filter, QtCore.SIGNAL("timeout()"), self.TriggeredTimeOut)
        else:
            self.event_filter = None
        
        #self.TriggeredTimeOut() #da se prikaze log-screen na prvoto vklucuvanje

    def CreateCentralWidget(self):
        LayoutCentral = QtGui.QGridLayout()

        #DRVO na aktivni naracki
        self.ListaNaracki = QtGui.QTreeWidget()
        self.ListaNaracki.setColumnCount(4)
        self.ListaNaracki.setHeaderLabels([d2u('Активни Нарачки'),d2u('бр.Сметка'),d2u('Време'),d2u('Датум')])
        self.ListaNaracki.setSortingEnabled(True)
        #self.ListaNaracki.hideColumn(1)
        self.ListaNaracki.setColumnWidth(2, 80)
        self.ListaNaracki.setColumnWidth(3, 80)
        self.ListaNaracki.header().setResizeMode(0, QtGui.QHeaderView.Stretch)
        self.connect(self.ListaNaracki,QtCore.SIGNAL("itemSelectionChanged()"),self.TriggeredTreeSelection)

        #DRVO na artikli
        self.TreeArticleList = QtGui.QTreeWidget()
        self.TreeArticleList.setHeaderLabel(d2u("Мени"))
        self.TreeArticleList.setSortingEnabled(True)
        self.TreeArticleList.setColumnCount(6)
        self.TreeArticleList.sortByColumn(0,Qt.Qt.AscendingOrder)
        self.TreeArticleList.hideColumn(1) #ID
        self.TreeArticleList.hideColumn(2) #Parent
        self.TreeArticleList.hideColumn(3) #Name
        self.TreeArticleList.hideColumn(4) #Price
        self.TreeArticleList.hideColumn(5) #Tax
        self.TreeArticleList.doubleClicked.connect(self.TriggeredTableAdd)
        
        #TABELA za prikaz na aktivna narackata
        self.TableNarackaPrikaz = QtGui.QTableWidget()
        self.TableNarackaPrikaz.setColumnCount(4)
        self.TableNarackaPrikaz.setHorizontalHeaderLabels([d2u("Артикл"),d2u("Цена"),d2u("Количина"),d2u("Вкупно")])
        self.TableNarackaPrikaz.setRowCount(0)
        self.TableNarackaPrikaz.verticalHeader().setVisible(False)
        self.TableNarackaPrikaz.setColumnWidth(1,60)
        self.TableNarackaPrikaz.setColumnWidth(2,60)
        self.TableNarackaPrikaz.setColumnWidth(3,60)
        self.TableNarackaPrikaz.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
        
        #TABELA za kreiranje nova naracka
        self.TableNaracka = QtGui.QTableWidget()
        self.TableNaracka.setColumnCount(4)
        self.TableNaracka.setHorizontalHeaderLabels([d2u("Артикл"),d2u("Цена"),d2u("Данок"),d2u("Количина")])
        self.TableNaracka.setRowCount(0)
        self.TableNaracka.verticalHeader().setVisible(False)
        self.TableNaracka.setColumnWidth(3,60)
        self.TableNaracka.setColumnHidden(1, True)
        self.TableNaracka.setColumnHidden(2, True)
        self.TableNaracka.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)

        #displej za vkupno suma
        self.LCDNumberSum = QtGui.QLCDNumber()
        self.LCDNumberSum.setSegmentStyle(2)
        self.LCDNumberSum.setFixedHeight(50)

        #labela za prikazuvanje na greski
        self.LabelError = QtGui.QLabel("")
        self.LabelError.hide()
        self.LabelError.setObjectName('Error')
        self.LabelError.setStyleSheet('QLabel#Error {color: red; font-weight: bold; background: white; padding-left: 5px}')

        #BUTTONS naracaj, komentar + layout
        self.ButtonNaracaj = QtGui.QPushButton(d2u("Нарачај"))
        self.connect(self.ButtonNaracaj,QtCore.SIGNAL("clicked()"),self.OrderClicked)
        self.ButtonIzbrisi = QtGui.QPushButton(d2u("Избриши"))
        self.connect(self.ButtonIzbrisi,QtCore.SIGNAL("clicked()"),self.ClearClicked)
        self.TextComment  = QtGui.QLineEdit()
        self.TextComment.setFixedWidth(30)

        MakeTransaction = QtGui.QHBoxLayout()
        MakeTransaction.addStretch()
        MakeTransaction.addWidget(QtGui.QLabel(d2u("Маса број: ")))
        MakeTransaction.addWidget(self.TextComment)
        MakeTransaction.addWidget(self.ButtonNaracaj)
        MakeTransaction.addWidget(self.ButtonIzbrisi)

        #GRID
        LayoutCentral.addWidget(self.LCDNumberSum,0,2,1,1)
        LayoutCentral.addWidget(self.ListaNaracki,1,0,1,1)
        LayoutCentral.addWidget(self.TableNarackaPrikaz,1,1,1,2)
        LayoutCentral.addWidget(self.TreeArticleList,2,0,1,1)
        LayoutCentral.addWidget(self.TableNaracka,2,1,1,2)
        LayoutCentral.addWidget(self.LabelError,3,0,1,1)
        LayoutCentral.addLayout(MakeTransaction,3,1,1,2)

        CentralWidget = QtGui.QWidget()
        CentralWidget.setLayout(LayoutCentral)
        self.setCentralWidget(CentralWidget)

    def OrderClicked(self):
        """
        Ja zapisuva vnesenata naracka vo baza(tabela) za transakcii i aktivni transakcii
        Avtomatski generira broj na smetka 
        Azurira prikaz na aktivni transakcii
        """
        if self.TextComment.text(): #ako e vnesen brojot na masa
            Query = self.Database.exec_("SELECT * FROM Trans")
            if Query.last(): #posledna naracka
                self.CountNumber = Query.value(6).toInt()[0] + 1 
            else: #prva naracka
                self.CountNumber = 1

            quantity_valid=True
            for i in range(self.TableNaracka.rowCount()): #dali ima vneseno kolicina vo site polinja od tabelata
                if not self.TableNaracka.item(i,3): 
                    quantity_valid=False

            if quantity_valid and self.TableNaracka.rowCount(): #ako za sekoj artikl ima vneseno kolicina
                for i in range(self.TableNaracka.rowCount()):
                    self.myTransaction = Transaction()
                    self.myTransaction.Type  = unicode(QtCore.QString(d2u('материјално')))
                    self.myTransaction.Name  = unicode(self.TableNaracka.item(i,0).text())
                    self.myTransaction.Price = unicode(self.TableNaracka.item(i,1).text())
                    self.myTransaction.Tax   = unicode(self.TableNaracka.item(i,2).text())
                    self.myTransaction.Quantity = unicode(self.TableNaracka.item(i,3).text())
                    self.myTransaction.Count = unicode(QtCore.QString(str(self.CountNumber)))
                    self.myTransaction.Comment = unicode(self.TextComment.text())

                    #zapisuvanje vo dvete tabeli
                    self.DatabaseActiveTransactionAdd(self.myTransaction)
                    self.DatabaseTransactionAdd(self.myTransaction)

                self.TableClear()
                #azurira drvo na aktivni naracki
                Comment = d2u("Маса број: %s") % self.TextComment.text()
                Date = unicode(QtCore.QDate.currentDate().toPyDate().strftime('%Y-%m-%d'))
                Time = unicode(QtCore.QTime.currentTime().toPyTime().strftime('%H:%M:%S')) 
                lista=[Comment, unicode(self.CountNumber),Time,Date]

                QtGui.QTreeWidgetItem(self.ListaNaracki,lista)
                self.TextComment.clear()
                self.LabelError.hide()
            else:
                self.LabelError.setText(d2u("ГРЕШКА: НЕМАТЕ ВНЕСЕНО КОЛИЧИНА НА АРТИКЛ"))
                self.LabelError.show()

        else:
            self.LabelError.setText(d2u("ГРЕШКА: НЕМАТЕ ВНЕСЕНО БРОЈ НА МАСА"))
            self.LabelError.show()

    def ClearClicked(self):
        self.TableClear()

#------------------------------- /Akcii ----------------------------------------

    def CreateAction(self,text,slot=None,shortcut=None,icon=None,tip=None,checkable=False,signal="triggered()"):
        action=QtGui.QAction(text,self)
        if icon is not None:
            action.setIcon(QtGui.QIcon("%s.ico"%icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action,QtCore.SIGNAL(signal),slot)
        if checkable:
            action.setCheckable(True)
        return action
    
    def CreateActions(self):
        self.ActionDatabaseNew = self.CreateAction("Nova Baza...",self.TriggeredDatabaseNew,"Ctrl+T","icons/New",d2u("Направи нова база (артикли,трансакции)"))
        self.ActionDatabaseOpen = self.CreateAction("Otvori Basa...",self.TriggeredDatabaseOpen,"Ctrl+O","icons/Open",d2u("Отвори постоечка база"))
        self.ActionArticleAdd = self.CreateAction("Vnesi Artikl...",self.TriggeredArticleAdd,"Ctrl+A","icons/Add",d2u("Внеси артикл"))
        self.ActionArticleEdit = self.CreateAction("Promeni Artikl...",self.TriggeredArticleEdit,"Ctrl+E","icons/Edit",d2u("Промени артикл"))
        self.ActionArticleDelete = self.CreateAction("Izbrisi Artikl",self.TriggeredArticleDelete,"Ctrl+D","icons/Delete",d2u("Избриши артикл"))
        
        self.ActionUsers = self.CreateAction("Korisnici", self.TriggeredUsers,"Ctrl+U", "icons/User",d2u("Корисници"))
        self.ActionDailyReport = self.CreateAction("Dneven Izvestaj", self.TriggeredDailyReport,"F9","icons/Report",d2u("Дневен извештај (F9)"))
        self.ActionMakePaymant = self.CreateAction("Naplati", self.TriggeredMakePaymant,"F5","icons/Check", d2u("Наплати (F5)"))
        self.ActionExit = self.CreateAction("Izlez",self.TriggeredExit,"Esc","icons/Exit",d2u("Излез"))

        self.UpdateActionStatus()

    #koga da bidat ovozmozeni klikovite
    def UpdateActionStatus(self):
        self.ActionArticleAdd.setEnabled(self.Database.isOpen()) 
        self.ActionArticleEdit.setEnabled(self.Database.isOpen())
        self.ActionArticleDelete.setEnabled(self.Database.isOpen())

    def CreateToolbar(self):
        Toolbar = QtGui.QToolBar()
        Toolbar.addAction(self.ActionDatabaseNew)
        Toolbar.addAction(self.ActionDatabaseOpen)
        Toolbar.addSeparator()
        Toolbar.addAction(self.ActionArticleAdd)
        Toolbar.addAction(self.ActionArticleEdit)
        Toolbar.addAction(self.ActionArticleDelete)
        Toolbar.addSeparator()
        Toolbar.addAction(self.ActionUsers)
        Toolbar.addAction(self.ActionMakePaymant)
        Toolbar.addAction(self.ActionDailyReport)
        Toolbar.addSeparator()
        Toolbar.addAction(self.ActionExit)

        self.addToolBar(Qt.Qt.BottomToolBarArea,Toolbar)

#------------------------------- /Trigeri ----------------------------------------

    def TriggeredDatabaseNew(self):
        self.DatabaseNew()

    def TriggeredDatabaseOpen(self):
        self.DatabaseOpen()

    def TriggeredArticleAdd(self):
        AddArticleDialog = AddEditArticle(self)
        if AddArticleDialog.exec_():
            ID = self.DatabaseArticleAdd(AddArticleDialog.myArticle)                                   
            AddArticleDialog.myArticle.ID=ID
            self.TreeArticleAdd(AddArticleDialog.myArticle)
        
    def TriggeredArticleEdit(self):
        EditArticleDialog = AddEditArticle(self,Article([self.TreeArticleList.selectedItems()[0].text(i) for i in range(1,7)]))
        if EditArticleDialog.exec_():
            SelectedItem=self.TreeArticleList.selectedItems()[0]
            ArticlesToEdit=[]
            for ChildIndex in range(SelectedItem.childCount()): #ako editira Root
                ChildArticle=Article([self.TreeArticleList.selectedItems()[0].child(ChildIndex).text(i) for i in range(1,7)])
                if EditArticleDialog.myArticle.Parent!="0":
                    ChildArticle.Parent=EditArticleDialog.myArticle.Parent
                ArticlesToEdit.append(ChildArticle)
            ArticlesToEdit.append(EditArticleDialog.myArticle)
            for aArticle in ArticlesToEdit:
                self.DatabaseArticleEdit(aArticle)
                self.TreeArticleEdit(aArticle)
    
    def TriggeredArticleDelete(self):
        DeleteConfirmBox = QtGui.QMessageBox()
        DeleteConfirmBox.setIcon(QtGui.QMessageBox.Warning)
        DeleteConfirmBox.setWindowTitle(d2u("Избриши артикл"))
        DeleteConfirmBox.setWindowIcon(QtGui.QIcon("icons/Delete.ico"))
        DeleteConfirmBox.setText(d2u("Дали сакате да го избришете селектираниот артикл?"))
        DeleteConfirmBox.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        #print [self.TreeArticleList.selectedItems()[0].text(i) for i in range(1,6)]
        if DeleteConfirmBox.exec_()==QtGui.QMessageBox.Ok:
            self.TableClear()
            self.DatabaseArticleDelete(Article([self.TreeArticleList.selectedItems()[0].text(i) for i in range(1,6)]))
            # DeleteFromTree?
            self.TreeArticleDelete(Article([self.TreeArticleList.selectedItems()[0].text(i) for i in range(1,6)]))

    def TriggeredTreeSelection(self):
        self.UpdateActionStatus()
        if self.ListaNaracki.selectedItems():
            self.InfoUpdate()        

    def TriggeredTableAdd(self):
        self.UpdateActionStatus()
        if int(self.TreeArticleList.selectedItems()[0].text(2)): #site so ne nulti parent
            self.TableAdd()

    def TriggeredExit(self):
        self.DatabaseClose()
        self.close()

    def TriggeredTimeOut(self):
        self.disconnect(self.event_filter, QtCore.SIGNAL("timeout()"), self.TriggeredTimeOut)  
        users = self.DatabaseGetUsers()
        Log = Login(self,users)
        Log.showFullScreen()
        if Log.exec_():
            self.connect(self.event_filter, QtCore.SIGNAL("timeout()"), self.TriggeredTimeOut)
              

    def TriggeredMakePaymant(self):
        """
        ako ima selektirano masa, ja brise od aktivni transakcii i azurira prikaz
        *treba da se voveded funkcija za pecatenje
        """
        if(self.ListaNaracki.selectedItems()):
            count = self.ListaNaracki.selectedItems()[0].text(1)
            self.DatabaseActiveTransactionDelete(count)
            self.TreeActiveTransactionPopulate()
            self.TableNarackaClear()
            self.LabelError.hide()
        else:
            self.LabelError.setText(d2u("ГРЕШКА: НЕМАТЕ СЕЛЕКТИРАНО МАСА"))
            self.LabelError.show()

    def TriggeredDailyReport(self):
        """
        Prikazuva dneven izvestaj za selektiraniot den od kalendarot
        Treba da se implementira nacinot na vizuelizacija
        """
        Calendar = CalendarDialog(self)
        if Calendar.exec_():
            date = Calendar.selectedDate.toPyDate()
            Query = self.Database.exec_("SELECT * FROM Trans WHERE date_created='%s'" % str(date))
            count_dict={}   #key: broj_na_smetka ; value: ceh
            article_dict={} #key: artikl; value: ceh
            while Query.next():
                name  = str(Query.value(2).toString().toUtf8())
                price = Query.value(3).toInt()[0]
                quantity = Query.value(5).toInt()[0]
                count = str(Query.value(6).toString())
                #print name,price,quantity,count
                if count not in count_dict:
                    count_dict[count] = quantity * price
                elif count in count_dict:
                    count_dict[count] = count_dict.get(count) + quantity * price
                if name not in article_dict:
                    article_dict[name] = quantity * price
                elif name in article_dict:
                    article_dict[name] = article_dict.get(name) + quantity * price
           
            print count_dict
            print article_dict
            print "Vkupno po smetka: %s " % sum(count_dict.values())
            print "Vkupno po artikl: %s " % sum(article_dict.values())

 
    def TriggeredUsers(self):
        """
        Dodavanje na novi korisnici
        ili brisenje na stari
        """
        Query = self.Database.exec_("SELECT * FROM Users")
        Users = UsersDialog(self,Query)
        if Users.exec_():
            if Users.delete:
                self.DatabaseUserDelete(Users.User.Name)
            if Users.sign:
                if self.DatabaseUserExist(Users.User.Name):
                    QtGui.QMessageBox.warning(
                    self, d2u('Грешка'), d2u('Корисникот веќе постои'))
                else:
                    self.DatabaseUserAdd(Users.User)

#------------------------------- /Bazi ----------------------------------------

    def DatabaseDefaultOpen(self):
        if self.DatabaseName == 'db/Base.adb':
            self.DatabaseConnect()

    def DatabaseNew(self):
        self.DatabaseName = unicode(QtGui.QFileDialog.getSaveFileName(self,"New Database",".","Milan Databases (*.adb)"))
        if self.DatabaseName:
            self.DatabaseCreate()
        else:
            pass # Cancel
    
    def DatabaseOpen(self):
        self.DatabaseName = unicode(QtGui.QFileDialog.getOpenFileName(self,"Open Database",".","Milan Databases (*.adb)"))
        if self.DatabaseName:
            self.DatabaseConnect()
        else:
            pass # Cancel
    
    def DatabaseConnect(self):
        self.DatabaseClose()
        self.Database.setDatabaseName(self.DatabaseName)
        self.Database.open()
        if self.Database.isOpen():
            self.TreePopulate()
            self.TreeActiveTransactionPopulate()
            self.UpdateActionStatus()
        else:
            print "Problem?"
            
    def DatabaseClose(self):
        if self.Database.isOpen():
            self.Database.close()

    def DatabaseCreate(self):
        self.DatabaseClose()
        self.Database.setDatabaseName(self.DatabaseName)
        self.Database.open()
        if self.Database.isOpen():
            self.Database.exec_("""CREATE TABLE Article (
                                id INTEGER PRIMARY KEY,
                                parent INTEGER,
                                name TEXT,
                                price TEXT,
                                tax TEXT)""")
            self.Database.exec_("""CREATE TABLE Trans (
                                id INTEGER PRIMARY KEY,
                                type TEXT,
                                name TEXT,
                                price INTEGER,
                                tax INTEGER,
                                quantity INTEGER,
                                count INTEGER,
                                date_created DATE,
                                time_created TEXT)""")
            self.Database.exec_("""CREATE TABLE Active (
                                id INTEGER PRIMARY KEY,
                                type TEXT,
                                name TEXT,
                                price INTEGER,
                                tax INTEGER,
                                quantity INTEGER,
                                count INTEGER,
                                date_created DATE,
                                time_created TEXT,
                                comment TEXT)""")
            self.Database.exec_("""CREATE TABLE Users (
                                id INTEGER PRIMARY KEY,
                                name TEXT,
                                pass TEXT,
                                date_created DATE)""")
            self.DatabaseClose()
            self.DatabaseConnect()
        else:
            print "Problem?!"

    def DatabaseArticleAdd(self,aArticle):
        InsertQuery = QtSql.QSqlQuery()
        InsertQuery.prepare("INSERT INTO Article (parent, name, price, tax) "
                            "VALUES (:parent, :name, :price, :tax)")
        InsertQuery.bindValue(":parent",QtCore.QVariant(aArticle.Parent))
        InsertQuery.bindValue(":name",QtCore.QVariant(aArticle.Name))
        InsertQuery.bindValue(":price",QtCore.QVariant(aArticle.Price))
        InsertQuery.bindValue(":tax",QtCore.QVariant(aArticle.Tax))
        InsertQuery.exec_()
        Query = self.Database.exec_("SELECT * FROM Article")
        Query.last()
        return Query.value(0).toString()

    def DatabaseArticleEdit(self,aArticle):
        InsertQuery = QtSql.QSqlQuery()
        InsertQuery.prepare("UPDATE Article "
                            "SET parent=:parent, name=:name, price=:price, tax=:tax "
                            "WHERE id=:id")
        InsertQuery.bindValue(":id",QtCore.QVariant(aArticle.ID))
        InsertQuery.bindValue(":parent",QtCore.QVariant(aArticle.Parent))
        InsertQuery.bindValue(":name",QtCore.QVariant(aArticle.Name))
        InsertQuery.bindValue(":price",QtCore.QVariant(aArticle.Price))
        InsertQuery.bindValue(":tax",QtCore.QVariant(aArticle.Tax))
        InsertQuery.exec_()
    
    def DatabaseArticleDelete(self,aArticle):
        InsertQuery = QtSql.QSqlQuery()
        InsertQuery.prepare("UPDATE Article "
                            "SET parent='0'"
                            "WHERE parent=:id")
        InsertQuery.bindValue(":id",QtCore.QVariant(aArticle.ID))
        InsertQuery.exec_()
        InsertQuery.prepare("DELETE FROM Article "
                            "WHERE id=:id")
        InsertQuery.bindValue(":id",QtCore.QVariant(aArticle.ID))
        InsertQuery.exec_()

    def DatabaseTransactionAdd(self,aTransaction):
        InsertQuery = QtSql.QSqlQuery()
        InsertQuery.prepare("INSERT INTO Trans (type, name, price, tax, quantity, count, date_created, time_created) " 
                            "VALUES (:type, :name, :price, :tax, :quantity, :count, :date_created, :time_created)")
        InsertQuery.bindValue(":type",QtCore.QVariant(aTransaction.Type))
        InsertQuery.bindValue(":name",QtCore.QVariant(aTransaction.Name))
        InsertQuery.bindValue(":price",QtCore.QVariant(aTransaction.Price))
        InsertQuery.bindValue(":tax",QtCore.QVariant(aTransaction.Tax))
        InsertQuery.bindValue(":quantity",QtCore.QVariant(aTransaction.Quantity))
        InsertQuery.bindValue(":count",QtCore.QVariant(aTransaction.Count))
        InsertQuery.bindValue(":date_created",QtCore.QVariant(aTransaction.DateCreated))
        InsertQuery.bindValue(":time_created",QtCore.QVariant(aTransaction.TimeCreated))
        InsertQuery.exec_()

    def DatabaseActiveTransactionAdd(self,aTransaction):
        InsertQuery = QtSql.QSqlQuery()
        InsertQuery.prepare("INSERT INTO Active (type, name, price, tax, quantity, count, date_created, time_created, comment) " 
                            "VALUES (:type, :name, :price, :tax, :quantity, :count, :date_created, :time_created, :comment)")
        InsertQuery.bindValue(":type",QtCore.QVariant(aTransaction.Type))
        InsertQuery.bindValue(":name",QtCore.QVariant(aTransaction.Name))
        InsertQuery.bindValue(":price",QtCore.QVariant(aTransaction.Price))
        InsertQuery.bindValue(":tax",QtCore.QVariant(aTransaction.Tax))
        InsertQuery.bindValue(":quantity",QtCore.QVariant(aTransaction.Quantity))
        InsertQuery.bindValue(":count",QtCore.QVariant(aTransaction.Count))
        InsertQuery.bindValue(":date_created",QtCore.QVariant(aTransaction.DateCreated))
        InsertQuery.bindValue(":time_created",QtCore.QVariant(aTransaction.TimeCreated))
        InsertQuery.bindValue(":comment",QtCore.QVariant(aTransaction.Comment))
        InsertQuery.exec_()
        #print InsertQuery.lastError().text()
      
    def DatabaseActiveTransactionDelete(self,count):
        self.Database.exec_("DELETE FROM Active WHERE count='%s'" % count)

    def DatabaseUserAdd(self,User):
        InsertQuery = QtSql.QSqlQuery()
        InsertQuery.prepare("INSERT INTO Users (name, pass) "
                            "VALUES (:name, :password)")
        InsertQuery.bindValue(":name",QtCore.QVariant(User.Name))
        InsertQuery.bindValue(":password",QtCore.QVariant(User.Pass))
        InsertQuery.exec_()

    def DatabaseGetUsers(self):
        Query = self.Database.exec_("SELECT * FROM Users")
        usr=[]
        while Query.next():
            name = Query.value(1).toString()
            password = Query.value(2).toString()
            usr.append([name,password]) 
        return usr

    def DatabaseUserExist(self,name):
        return self.Database.exec_("SELECT * FROM Users WHERE name='%s'" % name).first()
        
    def DatabaseUserDelete(self,name):
        self.Database.exec_("DELETE FROM Users WHERE name='%s'" % name)


#---------------- Popolnuvanje na drva i tabeli ---------

    def TreePopulate(self):
        self.TreeArticleList.clear()
        # Fill Root
        Query = self.Database.exec_("SELECT * FROM Article WHERE parent='0'")
        while Query.next():
            self.TreeArticleAdd(Article([Query.value(i).toString() for i in range(5)]))
        # Fill Childs
        # Fill Root
        Query = self.Database.exec_("SELECT * FROM Article WHERE parent<>'0'")
        while Query.next():
            self.TreeArticleAdd(Article([Query.value(i).toString() for i in range(5)]))

    def TreeActiveTransactionPopulate(self):
        self.ListaNaracki.clear()
        Query = self.Database.exec_("SELECT * FROM Active")
        count=[]
        while Query.next():
            if Query.value(6).toString() not in count:
                count.append(Query.value(6).toString())
                date = Query.value(7).toString()
                time = Query.value(8).toString()
                comment = Query.value(9).toString()
                QtGui.QTreeWidgetItem(self.ListaNaracki,[d2u("Маса број: %s") % comment, count[-1],time,date])

    def TreeArticleAdd(self,aArticle):
        ArticleAsList = aArticle.get_list()
        ArticleAsList.insert(0,aArticle.Name.split("\n")[0])
        
        if aArticle.Parent=="0": # Root
            QtGui.QTreeWidgetItem(self.TreeArticleList,ArticleAsList)
        else:
            QtGui.QTreeWidgetItem(self.TreeArticleList.findItems(aArticle.Parent,Qt.Qt.MatchExactly,1)[0],ArticleAsList)

    def TreeArticleEdit(self,aArticle):
        EditedItem = self.TreeArticleList.findItems(aArticle.ID,Qt.Qt.MatchRecursive,1)[0]
        if EditedItem.text(2)=="0": #Root
            self.TreeArticleList.takeTopLevelItem(self.TreeArticleList.indexOfTopLevelItem(EditedItem))
        else:
            EditedItem.parent().takeChild(EditedItem.parent().indexOfChild(EditedItem))
        self.TreeArticleAdd(aArticle)
    
    def TreeArticleDelete(self,aArticle):
        EditedItem = self.TreeArticleList.findItems(aArticle.ID,Qt.Qt.MatchRecursive,1)[0]
        if EditedItem.text(2)=="0": #Root
            for ChildIndex in range(EditedItem.childCount()):
                ChildItem=EditedItem.takeChild(ChildIndex)
                ChildItem.setText(2,"0")
                QtGui.QTreeWidgetItem(self.TreeArticleList,[ChildItem.text(i) for i in range(5)])
            self.TreeArticleList.takeTopLevelItem(self.TreeArticleList.indexOfTopLevelItem(EditedItem))
        else:
            EditedItem.parent().takeChild(EditedItem.parent().indexOfChild(EditedItem))

    def InfoUpdate(self):
        self.TableNarackaClear()
        count = self.ListaNaracki.selectedItems()[0].text(1)
        self.Sum = 0

        Query = self.Database.exec_("SELECT * FROM Active WHERE count='%s'" % count)
        while Query.next():
            itemName  = QtGui.QTableWidgetItem(Query.value(2).toString())
            itemName.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            itemPrice = QtGui.QTableWidgetItem(Query.value(3).toString())
            itemPrice.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            itemQuant = QtGui.QTableWidgetItem(Query.value(5).toString())
            itemQuant.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            itemSum   = QtGui.QTableWidgetItem(QtCore.QString(str(Query.value(3).toInt()[0] * Query.value(5).toInt()[0])))
            itemSum.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

            self.TableNarackaPrikazLastRow = self.TableNaracka.rowCount()
            self.TableNarackaPrikaz.insertRow(self.TableNarackaPrikazLastRow)

            self.TableNarackaPrikaz.setItem(self.TableNarackaPrikazLastRow,0,itemName)
            self.TableNarackaPrikaz.setItem(self.TableNarackaPrikazLastRow,1,itemPrice)
            self.TableNarackaPrikaz.setItem(self.TableNarackaPrikazLastRow,2,itemQuant)
            self.TableNarackaPrikaz.setItem(self.TableNarackaPrikazLastRow,3,itemSum)
            
            self.Sum += Query.value(3).toInt()[0] * Query.value(5).toInt()[0]

        self.LCDNumberSum.display(self.Sum)

    def TableAdd(self):
        self.TableNarackaLastRow = self.TableNaracka.rowCount()
        self.TableNaracka.insertRow(self.TableNarackaLastRow)

        itemName  = QtGui.QTableWidgetItem(self.TreeArticleList.selectedItems()[0].text(3))
        itemName.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        itemPrice = QtGui.QTableWidgetItem(self.TreeArticleList.selectedItems()[0].text(4))
        itemTax   = QtGui.QTableWidgetItem(self.TreeArticleList.selectedItems()[0].text(5))

        self.TableNaracka.setItem(self.TableNarackaLastRow,0,itemName)
        self.TableNaracka.setItem(self.TableNarackaLastRow,1,itemPrice)
        self.TableNaracka.setItem(self.TableNarackaLastRow,2,itemTax)

    def TableClear(self):
        self.TableNaracka.clear()
        self.TableNaracka.setRowCount(0)
        self.TableNaracka.setHorizontalHeaderLabels([d2u("Артикл"),d2u("Цена"),d2u("Данок"),d2u("Количина")])

    def TableNarackaClear(self):
        self.TableNarackaPrikaz.clear()
        self.TableNarackaPrikaz.setRowCount(0)
        self.TableNarackaPrikaz.setHorizontalHeaderLabels([d2u("Артикл"),d2u("Цена"),d2u("Количина"),d2u("Вкупно")])


if __name__=="__main__":
    myApp = QtGui.QApplication(sys.argv)
    
    myProgram = MainWindow()
    myProgram.showFullScreen()
    #"windows", "motif", "cde", "plastique" and "cleanlooks", platform: "windowsxp", "windowsvista" and "macintosh"
    myApp.setStyle(QtGui.QStyleFactory.create("cleanlooks")) 
    
    #new stylesheet
    #import os
    #styleFile=os.path.join(os.path.split(__file__)[0],"darkorange.stylesheet")
    #with open(styleFile,"r") as fh:
    #    myApp.setStyleSheet(fh.read())
    #fh.close()
    myApp.exec_()

