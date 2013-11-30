# -*- coding: utf-8 -*-
import requests, lxml.html
    
abc = u'АБВГДЕЗИЙКЛМНОПРСТУФХЦЧШЭЮЯ'
    
def download_table(char):
    url = "http://pctel.ru/pages/tarifs/" + char.encode('utf8') + "/exchange:1/plan:1"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0",
        "Referer": "http://pctel.ru/pages/tarifs",
        "Cookie": "CAKEPHP=sh4hhtm1ffgcsveukdjmtaqn21"
    }
    
    res = requests.get(url, headers=headers)
    content = res.content.decode('cp1251')
    doc = lxml.html.fromstring(content)
    
    tarif_trs = doc.xpath("//table[@class='tariftable']/tr")
    
    
    out = []
    for tr in tarif_trs:
        tds = tr.xpath("./td/text()")
        out.append(tds)
    
    f = open('tarif.csv','a')
    for i in out:
        if len(i) < 4: 
            out.remove(i)
            continue
        a = i[0] + ';' + i[1] + ';' + i[2] + ';' + i[3] + '\n'
        f.write(a.encode('utf8'))
    
    f.close()
    
    
    #    for td in tds:
    #        print td
    
    #import pdb; pdb.set_trace() 

for i in abc:
    download_table(i)

