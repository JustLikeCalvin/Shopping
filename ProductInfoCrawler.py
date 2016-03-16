# -*- coding: utf-8 -*
import csv
import sys
import urllib

from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding('utf-8')


# 웹 사이트에 접속하여 상품코드에 해당하는 상품 정보를 조회 후 HTML을 파싱하여 관련 정보를 추출한다.
# 추출 된 정보를 화면에 출력 후 CSV 형태 파일로 저장한다.
def get_product_info(code):
	print "---------------------------------------------"
	print "상품코드 [%s]" % unicode(code)

	goods_detail_url = "http://www.lotteimall.com/goods/viewGoodsDetail.lotte?goods_no=" + code

	url = urllib.urlopen(goods_detail_url)
	url_stream = url.read()

	bs = BeautifulSoup(url_stream, "html.parser")

	try:
		close_product = bs.find_all('p', attrs={'class': 'msg_txt'})[0].text
	except IndexError as ie:
		close_product = ""

	if len(close_product) > 0:
		print "판매불가여부 [%s]" % unicode(close_product)
		write_csv(code, "판매불가 상품", ["" for i in range(10)], "", "", "", "", "", "")
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
	for _category in category_info:
		if str(_category).find('<a href="#" onclick=') == -1:
			category_name = category_name + _category.text + " > "
			category_list[category_count] = _category.text
			category_count = category_count + 1
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
	except AttributeError as ae:
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
		except AttributeError as ae:
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
			if is_brand == True:
				brand_name = _additional.text
				is_brand = False
			if str(_additional).find('<dt>브랜드</dt>') >= 0:
				is_brand = True
			# 제조사/원산지 태그를 찾았다면 그 다음 값은 제조사/원산지 명
			if is_maker == True:
				maker_name = _additional.text
				is_maker = False
			if str(_additional).find('<dt>제조사') >= 0:
				is_maker = True
	except AttributeError as ae:
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

	# TODO 상품만족도 고객평가 점수 추출
	# TODO 상품평 등록 건수 및 상품 Q&A 건수 추출

	print "상품명 [%s]" % unicode(product_name)
	print "카테고리명 [%s]" % unicode(category_name)
	print "브랜드 [%s]" % unicode(brand_name)
	print "제조사 / 원산지 [%s] [%s]" % (maker[0], maker[1])
	print "판매가 [%s] 최대혜택가 [%s] 카드청구할인가 [%s]" % (unicode(price_1), unicode(price_2), unicode(price_3))

	write_csv(code, product_name, category_list, brand_name, maker[0], maker[1], price_1, price_2, price_3)


# print product_name.prettify()

def write_csv(product_code, product_name, category_list, brand_name, maker, origin, price_1, price_2, price_3):
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
	             price_3])


product_code_list = []
"""
product_code_list = ["12493530", \
                     "12495623", \
                     "12497880", \
                     "12497879", \
                     "12497949", \
                     "12497832", \
                     "12498646", \
                     "12466705", \
                     "12486714", \
                     "12495320", \
                     "12501930", \
                     "12479756", \
                     "12495335", \
                     "12499808", \
                     "1091345460", \
                     "12496801", \
                     "12502516", \
                     "12488113", \
                     "12496805", \
                     "12498317", \
                     "1132292116", \
                     "12502517", \
                     "12500906", \
                     "12497903", \
                     "12500929", \
                     "1132693827", \
                     "1132100050", \
                     "12499719", \
                     "1113694121", \
                     "1130932216", \
                     "1131465444", \
                     "12499902", \
                     "12499722", \
                     "12499720", \
                     "1133953177", \
                     "1132284106", \
                     "1132119107", \
                     "12499662", \
                     "1132705418", \
                     "1132502627", \
                     "12491546", \
                     "12491545", \
                     "12502597", \
                     "12496556", \
                     "1133931145", \
                     "1130944889", \
                     "1132285367", \
                     "12503713", \
                     "12501838", \
                     "12503862", \
                     "12502746", \
                     "1132083053", \
                     "12501426", \
                     "1132108713", \
                     "1127967061", \
                     "1132341105", \
                     "1113966591", \
                     "1129835643", \
                     "12504012", \
                     "12501933", \
                     "1132705348", \
                     "1130766695", \
                     "12449987", \
                     "12491130", \
                     "12503662", \
                     "12499092", \
                     "12502985", \
                     "12503833", \
                     "12465080", \
                     "1075165909", \
                     "1098134542", \
                     "1094215830", \
                     "12490821", \
                     "1130966711", \
                     "12504229", \
                     "1105878930", \
                     "1133931067", \
                     "12504002", \
                     "1084380151", \
                     "12462814", \
                     "12499644", \
                     "12503830", \
                     "12501958", \
                     "12491548", \
                     "12491544", \
                     "12499943", \
                     "1120392999", \
                     "1063285689", \
                     "1132292121", \
                     "1132692571", \
                     "1132501799", \
                     "1134262365", \
                     "12503863", \
                     "1131507718", \
                     "1123094424", \
                     "1132491611", \
                     "1129201206", \
                     "12496715", \
                     "12492555", \
                     "12503068"]
"""

category_list = ["category_0", "category_1", "category_2", "category_3", "category_4", "category_5", "category_6", \
                 "category_7", "category_8", "category_9"]
write_csv("product_code", "product_name", category_list, "brand_name", "maker", "origin", "price_1", "price_2",
          "price_3")

input_file = open('TOP5MGOODS.csv', 'r')
csv_reader = csv.reader(input_file)
row_count = 0
for row in csv_reader:
	if row_count > 0:
		product_code_list.append(row[0])
	row_count = row_count + 1
	if row_count > 100:
		break

input_file.close()

for product_code in product_code_list:
	get_product_info(product_code)
