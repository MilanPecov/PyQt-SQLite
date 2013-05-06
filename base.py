# coding=utf-8
from PyQt4 import QtGui

class Article(object):
    def __init__(self,List=None):
        if List is None:
            List = [""]*5
        self.ID=List[0]
        self.Parent=List[1]
        self.Name=List[2]
        self.Price=List[3]
        self.Tax=List[4]
        
    def get_list(self):
        return [self.ID,self.Parent,self.Name,self.Price,self.Tax]

class Transaction(object):
    def __init__(self,List=None):
        if List is None:
            List=[""]*7
        self.ID=List[0]
        self.Type=List[1]
        self.Name=List[2]
        self.Price=List[3]
        self.Tax=List[4]
        self.Quantity=List[5]
        self.Count=List[6]
        self.DateCreated = unicode(QtCore.QDate.currentDate().toPyDate().strftime('%Y-%m-%d'))
        self.TimeCreated = unicode(QtCore.QTime.currentTime().toPyTime().strftime('%H:%M:%S'))
        self.Comment = ""

    def get_list(self):
        return [self.ID,self.Type,self.Name,self.Price,self.Tax,self.Quantity,self.Count]