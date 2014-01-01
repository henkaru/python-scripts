#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для создания отчетов по вхоядщему трафику.
Работает по cron 1 числа каждого месяца
"""

import MySQLdb,  datetime
from decimal import *
import subprocess

dbuser="traf"
dbname="traf"
dbhost="localhost"
limit = 500 # Ограничение трафика на один адрес клиента в Мб
cost = 0.3 # Стоимость в рублях одного Мб за первышение лимита

# Конвертирование даты начала и конца отчетного периода в unix_time
cur_month = str(datetime.datetime.now().month)
prev_month = str(datetime.datetime.now().month - 1)
cur_year = str(datetime.datetime.now().year)
year = str(datetime.datetime.now().year)
time_end = datetime.datetime.strptime(cur_year + '-' + cur_month + '-1',"%Y-%m-%d").strftime("%s")

if cur_month == "1":
    prev_month = "12"
    year = str(datetime.datetime.now().year - 1)
    time_start = datetime.datetime.strptime(year + '-' + prev_month + '-1',"%Y-%m-%d").strftime("%s")
else:
    time_start = datetime.datetime.strptime(year + '-' + prev_month + '-1',"%Y-%m-%d").strftime("%s")

#print time_start, time_end
# Создание курсора для подключения к базе traf
try:
    con = MySQLdb.connect(host=dbhost, user=dbuser, db=dbname)
    cur = con.cursor()
except MySQLdb.Error:
    print(db.error())

# Создание отчета по трафику
sql1 = """create temporary table `tmp` select dstaddr,doctets from `raw`
    use index(addr) where dstaddr like '192.168.1.%' and srcaddr not like '192.168.%' 
    and prot not in (2,139) and unix_secs >= """ + \
     time_start + """ and unix_secs < """ + time_end 

sql2 = """select user,dstaddr,sum(tmp.doctets)/1048576 as a from `tmp` 
    left join user on tmp.dstaddr = user.ip group by dstaddr order by a desc """


cur.execute(sql1)
cur.execute(sql2)

# Добавление вычисляемых столбцов к выборке из базы данных
res = list(cur.fetchall())
res2 = []
for i in res:
    y = list(i)
    y.append(''); y.append('')
    res2.append(y)

# Генерация отчета 
filename = '/tmp/stats_' + prev_month + '-' + cur_year + '.csv'

f = open(filename,'wa')
f.write('Статистика по входящему интернет-трафику за ' + prev_month + '-' + cur_year + '\n')
f.write('Пользователь;IP-адрес;Входящий трафик, Мб;Превышение, Мб; Стоимость, руб.\n')

for user,ip,traffic,overflow,cost2 in res2:
    overflow = traffic - limit
    if overflow <= 500:
        overflow = 0
    cost2 = float(overflow) * cost
#    f.write(str(user).decode('utf-8') + ';' + ip + ';' + str(traffic) + ';' + str(overflow) + ';' + str(cost2) + '\n')
    f.write(str(user) + ';' + ip + ';' + str(traffic) + ';' + str(overflow) + ';' + str(cost2) + '\n')

f.close()
con.close()

# Отправка отчета
msg = """Отчет об входящем трафике во вложенном файле.
Файл сохранен в кодировке UTF-8."""
subj = 'Интернет за ' + prev_month + '-' + year
admin = '123@gmail.com'
copyto1 = '123@mail.ru'
copyto2 = ''

p1 = subprocess.Popen(["echo",msg],stdout=subprocess.PIPE)
p2 = subprocess.Popen(["mutt","-s",subj,"-a",filename,"--",admin,copyto1],stdin=p1.stdout)
p1.stdout.close()
out = p2.communicate()[0]

