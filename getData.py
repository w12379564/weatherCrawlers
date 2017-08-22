# -*- coding:utf-8 -*-
import urllib
import urllib2
import re
import dbconnect
import MySQLdb

class weatherHis:
    def __init__(self):
        self.headers={'User-Agent' :'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)' ,
                      'Referer': 'https://www.wunderground.com',
                      }
        self.file=None
        self.title=None


    def getPage(self):
        try:
            url='https://www.wunderground.com/history/airport/ZSSS/'+str(self.date)+'/DailyHistory.html?req_city=Shanghai&req_statename=China'
            request = urllib2.Request(url, headers=self.headers)
            response = urllib2.urlopen(request)
            return response.read().decode('utf-8')
        except urllib2.URLError,e:
            if hasattr(e,"reason"):
                print u"Connecting failed, ERROR:",e.reason
                return None

    def getContent(self,page):
        titlePattern = re.compile('<div id="observations_details".*?<tr>(.*?)</tr>', re.S)
        colPattern = re.compile('.*?<th>(.*?)<', re.S)

        titleContent =re.search(titlePattern,page).group(1)
        colNames=re.findall(colPattern,titleContent)
        for i in range(0,len(colNames)):
            colNames[i]=colNames[i].strip()
        #print colNames
        index=[colNames.index('Time'),colNames.index('Temp.'),colNames.index('Humidity'),colNames.index('Pressure'),colNames.index('Wind Dir'),colNames.index('Wind Speed'),colNames.index('Conditions')]
        #print index

        pattern1 = re.compile('<tr class="no-metars">(.*?)</tr>',re.S)
        pattern2 = re.compile('<td.*?>(.*?)</td>', re.S)
        pattern3 = re.compile('<.*?"wx-value">(.*?)</span>', re.S)
        dayData=re.findall(pattern1,page)
        day = []
        #self.file = open(self.title + ".txt", "w+")
        for hourlyData in dayData:
            hour=[]
            items=re.findall(pattern2,hourlyData)
            for item in items:
                #print item
                value=re.search(pattern3,item)
                if value:
                    #print value.group(1)
                    modified_value=re.sub(r'\s',"",value.group(1))
                    hour.append(modified_value.encode('utf-8'))
                    #hour.append(modified_value)
                else:
                    modified_item=re.sub(r'\s',"",item)
                    hour.append(modified_item.encode('utf-8'))
                    #hour.append(modified_item)
            day.append(hour)
        return day,index

    def dataProcess(self,dayData,index):
        dayDataNew=[]
        for hourlyData in dayData:
            if not re.match(r'\d',hourlyData[index[5]]):
                hourlyData[index[5]]="0"
            timeAM = re.search(r'(.*?)AM',hourlyData[index[0]])
            timePM = re.search(r'(.*?)PM', hourlyData[index[0]])
            if timeAM:
                hourlyData[0]=self.title+'-'+re.sub(r'12',"00",timeAM.group(1))
            if timePM:
                sp=timePM.group().split(':')
                hour=int(sp[0])
                if hour!=12:
                    hour+=12
                hourlyData[0]=self.title+'-'+str(hour)+':'+sp[1][:-2]
            hourlyData[index[2]]=re.sub(r'%',"",hourlyData[index[2]])
            #print hourlyData
            dayDataNew.append([hourlyData[i] for i in index])
        return dayDataNew


    def setFileTitle(self):
        self.file = open(self.title + ".txt", "w+")

    def writeData(self,dayData):
        for hourlyData in dayData:
            for item in hourlyData:
                self.file.write(item)
                self.file.write(" ")
            self.file.write("\n")

    def writeDatabase(self,dayData):
        conn,cursor=dbconnect.connInit()
        for hourlyData in dayData:
            try:
                cursor.execute('insert into data2015 values (%s, %s, %s, %s, %s, %s, %s)', hourlyData)
                conn.commit()
            except MySQLdb.Error,e:
                print "MySQL Error:" + str(e)

    def start(self):
        page=self.getPage()
        (dataRaw,index)=self.getContent(page)
        data=self.dataProcess(dataRaw,index)
        #self.setFileTitle()
        #self.writeData(data)
        self.writeDatabase(data)

    def getMonthData(self,month):
        monthDays=[31,28,31,30,31,30,31,31,30,31,30,31]
        for i in range(1,monthDays[month-1]+1):
            date='2017/'+str(month)+'/'+str(i)
            self.date = date
            self.title=re.sub(r'/',"-",date)
            page = self.getPage()
            (dataRaw, index) = self.getContent(page)
            data = self.dataProcess(dataRaw, index)
            self.writeDatabase(data)
            print 'Data of '+self.date+' got!'

    def getYearData(self,year):
        monthDays = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        for month in range(1,13):
            for day in range(1, monthDays[month - 1] + 1):
                date = str(year) + '/' + str(month) + '/' + str(day)
                self.date = date
                self.title=re.sub(r'/',"-",date)
                page = self.getPage()
                (dataRaw, index) = self.getContent(page)
                data = self.dataProcess(dataRaw, index)
                self.writeDatabase(data)
                print 'Data of '+self.date+' got!'

