# -*- coding: utf-8 -*
import csv
import sys
import urllib

from bs4 import BeautifulSoup

# 한글 처리를 위해 기본 Charset encoding을 utf-8 로 처리
reload(sys)
sys.setdefaultencoding('utf-8')


# 웹 사이트에 접속하여 상품코드에 해당하는 상품 정보를 조회 후 HTML을 파싱하여 관련 정보를 추출한다.
# 추출 된 정보를 화면에 출력 후 CSV 형태 파일로 저장한다.
def get_product_info(code, total_index, current_index):
    print "---------------------- [ %s / %s ] -----------------------" % (current_index, total_index)
    print "상품코드 [%s]" % unicode(code)

    # 상품 상세 페이지 URL (상품코드가 파라미터로 전달 됨)
    goods_detail_url = "http://www.lotteimall.com/goods/viewGoodsDetail.lotte?goods_no=" + code

    url = urllib.urlopen(goods_detail_url)
    url_stream = url.read()

    bs = BeautifulSoup(url_stream, "html.parser")

    try:
        close_product = bs.find_all('p', attrs={'class': 'msg_txt'})[0].text
    except IndexError:
        close_product = ""

    if len(close_product) > 0:
        print "판매불가여부 [%s]" % unicode(close_product)
        write_csv(code, "판매불가 상품", ["" for i in range(10)], "", "", "", "", "", "", "", "")
        return

    # 상품명을 가져온다.
    product_name = bs.find_all('meta', attrs={'property': 'og:title'})[0]['content']
    """
    page_type = "0"
    try:
        product_name = bs.find_all('div', attrs={'class':'dinfo_tit'})[0].h3.span.text
        page_type = "1"
    except IndexError as ie:
        try:
            product_name = bs.find_all('div', attrs={'class':'dg_tit'})[0].h3.text
            page_type = "2"
        except IndexError as ie_1:
            product_name = bs.find_all('div', attrs={'class':'dinfo_tit'})[0].h3.text
            page_type = "3"
    except AttributeError as ae:
        product_name = bs.find_all('div', attrs={'class':'dinfo_tit'})[0].h3.text
        page_type = "4"
    product_name = unicode(product_name).strip()
    """

    # 카테고리 정보 상위 노드를 가져온다.
    category_info = bs.find('div', {'class': 'location'}).find_all('a')

    category_name = ""
    category_list = ["" for i in range(10)]
    category_count = 0
    # 외부 사이트 링크가 걸려 있는 경우를 조건으로 추가하여 제외 처리
    for _category in category_info:
        if str(_category).find('<a href="#" onclick=') == -1 & str(_category).find('<a href="http') == -1:
            category_name = category_name + _category.text + " > "
            category_list[category_count] = _category.text
            category_count += 1
    category_name = category_name.rstrip(" > ")

    # 가격 정보 상위 노드를 가져온다.
    price_1 = ""
    price_2 = ""
    price_3 = ""

    # 가격 정보 가져오는 방식 (첫번째 경우)
    try:
        price_info = bs.find('div', {'class': 'info_price'}).find_all('span')
        for _price in price_info:
            if str(_price).find('<span class="price"') >= 0:
                if len(price_1) == 0:
                    price_1 = _price.text
                else:
                    price_2 = _price.text
            elif str(_price).find('<span class="price2"') >= 0:
                price_3 = _price.text
    except AttributeError:
        price_1 = ""
        price_2 = ""
        price_3 = ""

    # 가격 정보 가져오는 방식 (두번째 경우)
    if len(price_1) == 0:
        try:
            price_info = bs.find('div', {'class': 'dg_price'}).find_all(['div', 'p'])
            for _price in price_info:
                if str(_price).find('<p class="price1"') >= 0:
                    price_1 = _price.text
                    price_1 = price_1[:price_1.find("원")].strip()
                elif str(_price).find('<div class="price2"') >= 0:
                    price_2 = _price.text
                    price_2 = price_2[:price_2.find("원")].strip()
        except AttributeError:
            price_1 = ""
            price_2 = ""
            price_3 = ""

    # 브랜드 정보 상위 노드를 가져온다.
    try:
        additional_info = bs.find('div', {'class': 'box tab_cont_selected'}).find_all(['dt', 'dd'])
        # 브랜드 태그를 찾았는지 여부
        is_brand = False
        # 제조사/원산지 태그를 찾았는지 여부
        is_maker = False
        brand_name = ""
        maker_name = ""
        for _additional in additional_info:
            # 브랜드 태그를 찾았다면 그 다음 값은 브랜드 명
            if is_brand is True:
                brand_name = _additional.text
                is_brand = False
            if str(_additional).find('<dt>브랜드</dt>') >= 0:
                is_brand = True
            # 제조사/원산지 태그를 찾았다면 그 다음 값은 제조사/원산지 명
            if is_maker is True:
                maker_name = _additional.text
                is_maker = False
            if str(_additional).find('<dt>제조사') >= 0:
                is_maker = True
    except AttributeError:
        brand_name = ""
        maker_name = ""

    if len(maker_name) > 0 & maker_name.find(" / ") != -1:
        maker = maker_name.split(" / ")
    else:
        maker = ["", ""]

    product_name = product_name.strip()
    category_name = category_name.strip()
    brand_name = brand_name.strip()
    maker[0] = maker[0].strip()
    maker[1] = maker[1].strip()
    price_1 = price_1.strip()
    price_2 = price_2.strip()
    price_3 = price_3.strip()

    # 상품만족도 고객평가 점수 추출
    evaluation_score = ""
    try:
        score_info = bs.find('div', {'class': 'grade_box bg2'}).find_all('dd')
        for _score in score_info:
            if str(_score).find('alt="점"') >= 0:
                evaluation_score = _score.text
    except AttributeError:
        evaluation_score = ""

    # 상품평 등록 건수 추출
    comment_count = ""
    try:
        comment_info = bs.find('span', {'id': 'gdasTotalCnt_1'})
        for _comment in comment_info:
            comment_count = _comment.strip("(").strip(")")
    except AttributeError:
        comment_count = ""

    # 상품정보를 처리하는 과정을 화면에 출력
    print "상품명 [%s]" % unicode(product_name)
    print "카테고리명 [%s]" % unicode(category_name)
    print "브랜드 [%s]" % unicode(brand_name)
    print "제조사 / 원산지 [%s] [%s]" % (maker[0], maker[1])
    print "판매가 [%s] 최대혜택가 [%s] 카드청구할인가 [%s]" % (unicode(price_1), unicode(price_2), unicode(price_3))
    print "고객평가점수 [%s]" % unicode(evaluation_score)
    print "상품평 [%s]" % unicode(comment_count)

    # 상품 정보를 CSV로 저장하는 메소드 호출
    write_csv(code, product_name, category_list, brand_name, maker[0], maker[1], price_1, price_2, price_3, evaluation_score,
              comment_count)


# CSV 파일에 상품 관련 정보를 저장
# 엑셀에서 열 경우 한글이 깨지는 문제를 해결하기 위해 저장 시점에 euc-kr 로 한글 변환
def write_csv(product_code, product_name, category_list, brand_name, maker, origin, price_1, price_2, price_3, evaluation_score,
              comment_count):
    cw = csv.writer(file('product_info.csv', 'ab'))
    cw.writerow([product_code.encode('euc-kr'), \
                 product_name.encode('euc-kr'), \
                 category_list[0].encode('euc-kr'), \
                 category_list[1].encode('euc-kr'), \
                 category_list[2].encode('euc-kr'), \
                 category_list[3].encode('euc-kr'), \
                 category_list[4].encode('euc-kr'), \
                 category_list[5].encode('euc-kr'), \
                 category_list[6].encode('euc-kr'), \
                 category_list[7].encode('euc-kr'), \
                 category_list[8].encode('euc-kr'), \
                 category_list[9].encode('euc-kr'), \
                 brand_name.encode('euc-kr'), \
                 maker.encode('euc-kr'), \
                 origin.encode('euc-kr'), \
                 price_1, \
                 price_2, \
                 price_3, \
                 evaluation_score, \
                 comment_count])


# 상품코드를 CSV에서 읽은 후 보관하는 리스트
product_code_list = []

# CSV Header를 생성
write_csv("product_code", "product_name", \
          ["category_0", "category_1", "category_2", "category_3", "category_4", "category_5", "category_6", "category_7",
           "category_8", "category_9"], \
          "brand_name", "maker", "origin", "price_1", "price_2",
          "price_3", "evaluation_score", "comment_count")

# 상품코드가 저장되어 있는 CSV 파일을 읽은 후 product_code_list 변수에 저장
# 테스트 용도이므로 100건만 저장하고 있음
input_file = open('TOP5MGOODS.csv', 'r')
csv_reader = csv.reader(input_file)
row_count = 0
for row in csv_reader:
    if row_count > 0:
        product_code_list.append(row[0])
    row_count += 1
    # TODO 실제 데이터 저장을 위해서라면 아래 두 줄 삭제 필요
    """
    if row_count > 100:
        break
    """

# 상품코드를 읽은 후 해당 CSV 파일 닫기
input_file.close()

# 읽은 상품코드 리스트를 이용해서 상품정보를 웹에서 얻어온 후 별도 CSV 파일에 저장
total_index = len(product_code_list)
current_index = 1
for product_code in product_code_list:
    get_product_info(product_code, total_index, current_index)
    current_index += 1
