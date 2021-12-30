import requests
import urllib.request
import pymysql
from bs4 import BeautifulSoup
from openpyxl import Workbook


mainUrl = "https://www.saramin.co.kr"


def mariadbConnect():
    db = pymysql.connect(
        host="127.0.0.1",
        user="root",
        passwd="crawl",
        database="test",
        port=3307,
        charset="utf8",
    )
    cursor = db.cursor()
    return db, cursor


def createWorkBook():
    write_wb = Workbook()
    write_ws = write_wb.create_sheet("생성시트")


def crawling(maxPage, cursor, db):
    for pagenumber in range(0, maxPage):
        if pagenumber == 0:
            url = (
                mainUrl
                + f"/zf_user/jobs/list/domestic?page=1&loc_mcd=101000&isAjaxRequest=0&page_count=50&sort=RL&type=domestic&is_param=1&isSearchResultEmpty=1&isSectionHome=0&searchParamCount=1#searchTitle"
            )
        url = (
            mainUrl
            + f"/zf_user/jobs/list/domestic?page={pagenumber + 1}&loc_mcd=101000&isAjaxRequest=0&page_count=50&sort=RL&type=domestic&is_param=1&isSearchResultEmpty=1&isSectionHome=0&searchParamCount=1#searchTitle"
        )
        response = requests.get(url)
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, "html.parser")
            homepage = soup.find_all("a", {"class": "str_tit"})
            indexing = 0
            for idxx, val in enumerate(homepage):
                if idxx % 2 == 0:
                    continue
                openUrl = urllib.request.urlopen(mainUrl + homepage[idxx]["href"])
                newUrl = openUrl.geturl()
                newResponse = requests.get(newUrl)
                newHtml = newResponse.text
                newsoup = BeautifulSoup(newHtml, "html.parser")
                splitList = newsoup.find_all(attrs={"name": "description"})[0][
                    "content"
                ].split(",")
                print(splitList)
                index = 0
                indexing += 1
                for idx, val in enumerate(splitList):
                    if idx == 0:
                        checksql = "SELECT * FROM company WHERE name = %s"
                        res = cursor.execute(checksql, val)
                        name = val
                        cursor.fetchall()
                        print(res)
                    if res == 1:
                        break
                    if val.find(":") == -1:
                        continue
                    else:
                        if "홈페이지" in val:
                            tt = val.split(":", 1)
                            cursor.execute(
                                "INSERT INTO company(name, homepage) VALUES (%s, %s)",
                                (name, tt[1]),
                            )
                            cursor.fetchall()
                            db.commit()
                            print(tt[1])
                        index += 1

    else:
        print(response.status_code)


def is_comapny(res):
    for i in res:
        for j in i:
            if j == "company":
                return True
    return False


def start():
    try:
        db, cursor = mariadbConnect()
        cursor.execute("show tables")
        result = cursor.fetchall()
    except:
        return "데이터베이스를 실행시켜주세요"

    if is_comapny(result) == False:
        cursor.execute(
            "CREATE TABLE company (id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(50) NOT NULL, homepage VARCHAR(100))"
        )
        print("테이블이 생성됐습니다.")

    action = input(
        """
    숫자 1 : 크롤링 실행
    숫자 2 : 데이터베이스 조회
    숫자 3 : 데이터베이스 엑셀로 저장
    
    입력해주세요 : """
    )

    if action == "1":
        maxPage = input("크롤링할 페이지 수를 입력해주세요 : ")
        crawling(int(maxPage), cursor, db)
        return "finish"
    if action == "2":
        cursor.execute("SELECT * from company")
        result = cursor.fetchall()
        for row in result:
            print(row)
    if action == "3":
        cursor.execute("SELECT * from company")
        result = cursor.fetchall()
        write_wb = Workbook()
        write_st = write_wb.active

        for idx, data in enumerate(result):
            write_st.cell(row=1 + idx, column=1).value = data[1]
            write_st.cell(row=1 + idx, column=2).value = data[2]
            write_wb.save("test.xlsx")


start()


# Get Cursor


# for i in range(0, 50):
#     print(i)
#     if i == 0:
#         url = (
#             mainUrl
#             + f"/zf_user/jobs/list/domestic?page=1&loc_mcd=101000&isAjaxRequest=0&page_count=50&sort=RL&type=domestic&is_param=1&isSearchResultEmpty=1&isSectionHome=0&searchParamCount=1#searchTitle"
#         )
#     url = (
#         mainUrl
#         + f"/zf_user/jobs/list/domestic?page={i + 1}&loc_mcd=101000&isAjaxRequest=0&page_count=50&sort=RL&type=domestic&is_param=1&isSearchResultEmpty=1&isSectionHome=0&searchParamCount=1#searchTitle"
#     )
#     response = requests.get(url)
#     if response.status_code == 200:
#         html = response.text
#         soup = BeautifulSoup(html, "html.parser")
#         homepage = soup.find_all("a", {"class": "str_tit"})
#         print(homepage)
#         indexing = 0
#         for idxx, val in enumerate(homepage):

#             if idxx % 2 == 0:
#                 continue
#             openUrl = urllib.request.urlopen(mainUrl + homepage[idxx]["href"])
#             newUrl = openUrl.geturl()
#             newResponse = requests.get(newUrl)
#             newHtml = newResponse.text
#             newsoup = BeautifulSoup(newHtml, "html.parser")
#             splitList = newsoup.find_all(attrs={"name": "description"})[0][
#                 "content"
#             ].split(",")
#             print(splitList)
#             index = 0
#             indexing += 1
#             for idx, val in enumerate(splitList):

#                 if idx == 0:
#                     print(val)
#                     write_ws.cell(
#                         row=1 + indexing + len(homepage) / 2 * i, column=1 + index
#                     ).value = val

#                 if val.find(":") == -1:
#                     continue
#                 else:
#                     tt = val.split(":", 1)
#                     write_ws.cell(
#                         row=1 + indexing + len(homepage) / 2 * i, column=2 + index
#                     ).value = tt[1]
#                     index += 1
#             write_wb.save("ㅅㅅ.xlsx")
#     else:
#         print(response.status_code)
