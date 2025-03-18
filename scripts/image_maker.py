from PIL import Image, ImageDraw, ImageFont
import json ,  requests , os , re , datetime
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

API_KEY = os.environ.get('API_KEY')
SCHOOL_CODE = os.environ.get('SCHOOL_CODE')
SCHOOL_EDU_OFFICE_CODE = os.environ.get('SCHOOL_EDU_OFFICE_CODE')

def loadfont(fontsize):
    ttf = './assets/fonts/NanumSquareRoundEB.ttf'
    return ImageFont.truetype(font=ttf, size=fontsize)


def school_meal():
    try:
        now = datetime.now()
        year = now.year
        month = now.month
        day = now.day
        weekdays = ['월', '화', '수', '목', '금','토','일']
        weekday = weekdays[now.weekday()]
        DATE = now.strftime("%Y%m%d") 
        print(f'{year}년 {month}월 {day}일 {weekday}요일')
        #DATE = datetime.now().strftime("20240507") 
        url = f"http://open.neis.go.kr/hub/mealServiceDietInfo?KEY={API_KEY}&Type=json&pIndex=1&pSize=5&ATPT_OFCDC_SC_CODE={SCHOOL_EDU_OFFICE_CODE}&SD_SCHUL_CODE={SCHOOL_CODE}&MLSV_YMD={DATE}"
        response = requests.get(url)
        if response.status_code == 200:
            meal_data_loaded = {"meals": None, "CAL_INFO": None}
            try:
                meal_info = response.json()
                try:
                    meals = meal_info['mealServiceDietInfo'][1]['row']
                    
                    # 초식 메뉴만을 저장할 리스트
                    vegetarian_meals = []

                    for meal in meals:
                        if meal['MMEAL_SC_CODE'] == '1':  # 조식인 경우만 처리
                            # 메뉴 정보에서 괄호와 괄호 안의 내용 제거
                            cleaned_menus = re.sub(r'\([^)]*\)', '', meal['DDISH_NM'])
                            cleaned_menus = cleaned_menus.replace("<br/>", "\n").strip()
                            # 개별 메뉴를 리스트에 추가
                            vegetarian_meals.extend(cleaned_menus.split('\n'))
                            CAL_INFO= meal['CAL_INFO']
                    
                    if not vegetarian_meals:
                        print("조식에 대한 급식이 없습니다.")
                        vegetarian = {"meals":None,"CAL_INFO":None}
                        with open('./json/morning.json', 'w', encoding='utf-8') as json_file:
                            json.dump(vegetarian, json_file, ensure_ascii=False, indent=4)
                    else:
                        print("조식 급식 메뉴를 성공적으로 가져왔습니다.")
                        vegetarian = {"meals":vegetarian_meals,"CAL_INFO":CAL_INFO}
                        with open('./json/morning.json', 'w', encoding='utf-8') as json_file:
                            json.dump(vegetarian, json_file, ensure_ascii=False, indent=4)

                        with open('./json/morning.json', 'r', encoding='utf-8') as json_file:
                            meal_data_loaded = json.load(json_file)

                        print("조식 메뉴 리스트가 morning.json 파일에 저장되었습니다.")
                        
                        # meal_data_loaded 사용 예시

                        W = 1080
                        H = 1080
                        image_path = './assets/images/001.jpg'
                        image = Image.open(image_path)
                        draw = ImageDraw.Draw(image)

                        font = loadfont(36)

                        date_font_color = 'rgb(32, 169, 2235)'
                        b = 'rgb(0, 0, 0)'

                        text = f'{year}년 {month}월 {day}일 {weekday}요일'
                        draw.text((W - 392 - 90, 75), text, fill=date_font_color, font=font)
                        draw.text((W - 245 - 90, 120), '조식 급식 목록', fill=b, font=font)
                                        
                        gddg = f'칼로리: {meal_data_loaded["CAL_INFO"]}'

                        draw.text((W - 245 - 150, 999), gddg, fill=0x6A6A6A, font=loadfont(36))
                                        
                        meal_font = loadfont(60)
                        meal_font_color = 'rgb(32, 169, 223)'

                        text_l = 70

                        for l in reversed(meal_data_loaded["meals"]):
                            draw.text((75, H - 75 - text_l), l, font=meal_font, fill=meal_font_color)
                            text_l += 85

                        image.convert('RGB').save('./build/morning.jpg', quality=95)
                        print('조식 이미지 생성 완료!')

                except KeyError:
                    print("급식 정보를 처리하는 중 오류가 발생했습니다.")
                    vegetarian = {"meals":None,"CAL_INFO":None}
                    with open('./json/morning.json', 'w', encoding='utf-8') as json_file:
                        json.dump(vegetarian, json_file, ensure_ascii=False, indent=4)
            except Exception as e:
                print("API 요청 또는 처리 중 오류가 발생했습니다:", str(e))
                vegetarian = {"meals":None,"CAL_INFO":None}
                with open('./json/morning.json', 'w', encoding='utf-8') as json_file:
                    json.dump(vegetarian, json_file, ensure_ascii=False, indent=4)
    except Exception as e:
        print("에러 발생:", str(e))
        vegetarian = {"meals":None,"CAL_INFO":None}
        with open('./json/morning.json', 'w', encoding='utf-8') as json_file:
            json.dump(vegetarian, json_file, ensure_ascii=False, indent=4)
        return meal_data_loaded


        

def school_meal2():
    try:
        now = datetime.now()
        year = now.year
        month = now.month
        day = now.day
        weekdays = ['월', '화', '수', '목', '금']
        weekday = weekdays[now.weekday()]
        DATE = now.strftime("%Y%m%d") 
        print(f'{year}년 {month}월 {day}일 {weekday}요일')
        # DATE = datetime.now().strftime("20240507") 
        url = f"http://open.neis.go.kr/hub/mealServiceDietInfo?KEY={API_KEY}&Type=json&pIndex=1&pSize=5&ATPT_OFCDC_SC_CODE={SCHOOL_EDU_OFFICE_CODE}&SD_SCHUL_CODE={SCHOOL_CODE}&MLSV_YMD={DATE}"
        response = requests.get(url)
        if response.status_code == 200:
            meal_data_loaded = {"meals": None, "CAL_INFO": None}
            try:
                meal_info = response.json()
                try:
                    meals = meal_info['mealServiceDietInfo'][1]['row']
                    
                    # 초식 메뉴만을 저장할 리스트
                    vegetarian_meals = []

                    for meal in meals:
                        if meal['MMEAL_SC_CODE'] == '2':  # 석식인 경우만 처리
                            # 메뉴 정보에서 괄호와 괄호 안의 내용 제거
                            cleaned_menus = re.sub(r'\([^)]*\)', '', meal['DDISH_NM'])
                            cleaned_menus = cleaned_menus.replace("<br/>", "\n").strip()
                            # 개별 메뉴를 리스트에 추가
                            vegetarian_meals.extend(cleaned_menus.split('\n'))
                            CAL_INFO= meal['CAL_INFO']
                    
                    if not vegetarian_meals:
                        print("중식에 대한 급식이 없습니다.")
                        vegetarian = {"meals":None,"CAL_INFO":None}
                        with open('./json/lunch.json', 'w', encoding='utf-8') as json_file:
                            json.dump(vegetarian, json_file, ensure_ascii=False, indent=4)
                    else:
                        print("중식 급식 메뉴를 성공적으로 가져왔습니다.")
                        vegetarian = {"meals":vegetarian_meals,"CAL_INFO":CAL_INFO}
                        with open('./json/lunch.json', 'w', encoding='utf-8') as json_file:
                            json.dump(vegetarian, json_file, ensure_ascii=False, indent=4)

                        with open('./json/lunch.json', 'r', encoding='utf-8') as json_file:
                            meal_data_loaded = json.load(json_file)

                        print("중식 메뉴 리스트가 lunch.json 파일에 저장되었습니다.")
                        # meal_data_loaded 사용 예시

                        W = 1080
                        H = 1080
                        image_path = './assets/images/001.jpg'
                        image = Image.open(image_path)
                        draw = ImageDraw.Draw(image)

                        font = loadfont(36)

                        date_font_color = 'rgb(32, 169, 223)'
                        b = 'rgb(0, 0, 0)'

                        text = f'{year}년 {month}월 {day}일 {weekday}요일'
                        draw.text((W - 392 - 90, 75), text, fill=date_font_color, font=font)
                        draw.text((W - 245 - 90, 120), '중식 급식 목록', fill=b, font=font)
                                        
                        gddg = f'칼로리: {meal_data_loaded["CAL_INFO"]}'

                        draw.text((W - 245 - 150, 999), gddg, fill=0x6A6A6A, font=loadfont(36))
                                        
                        meal_font = loadfont(60)
                        meal_font_color = 'rgb(129, 203, 196)'

                        text_l = 70

                        for l in reversed(meal_data_loaded["meals"]):
                            draw.text((75, H - 75 - text_l), l, font=meal_font, fill=meal_font_color)
                            text_l += 85

                        image.convert('RGB').save('./build/lunch.jpg', quality=95)
                        print('중식 이미지 생성 완료!')

                except KeyError:
                    print("급식 정보를 처리하는 중 오류가 발생했습니다.")
                    meal_data_loaded = {"meals": None, "CAL_INFO": None}
                    with open('./json/lunch.json', 'w', encoding='utf-8') as json_file:
                        json.dump(meal_data_loaded, json_file, ensure_ascii=False, indent=4)
            except Exception as e:
                print("API 요청 또는 처리 중 오류가 발생했습니다:", str(e))
                meal_data_loaded = {"meals": None, "CAL_INFO": None}
                with open('./json/lunch.json', 'w', encoding='utf-8') as json_file:
                    json.dump(meal_data_loaded, json_file, ensure_ascii=False, indent=4)
    except Exception as e:
        print("에러 발생:", str(e))
        meal_data_loaded = {"meals": None, "CAL_INFO": None}
        with open('./json/lunch.json', 'w', encoding='utf-8') as json_file:
            json.dump(meal_data_loaded, json_file, ensure_ascii=False, indent=4)

    

    
def school_meal3():
    try:
        now = datetime.now()
        year = now.year
        month = now.month
        day = now.day
        weekdays = ['월', '화', '수', '목', '금']
        weekday = weekdays[now.weekday()]
        DATE = now.strftime("%Y%m%d") 
        print(f'{year}년 {month}월 {day}일 {weekday}요일')
        # DATE = datetime.now().strftime("20240507") 
        url = f"http://open.neis.go.kr/hub/mealServiceDietInfo?KEY={API_KEY}&Type=json&pIndex=1&pSize=5&ATPT_OFCDC_SC_CODE={SCHOOL_EDU_OFFICE_CODE}&SD_SCHUL_CODE={SCHOOL_CODE}&MLSV_YMD={DATE}"
        response = requests.get(url)
        if response.status_code == 200:
            meal_data_loaded = {"meals": None, "CAL_INFO": None}
            try:
                meal_info = response.json()
                try:
                    meals = meal_info['mealServiceDietInfo'][1]['row']
                    
                    # 초식 메뉴만을 저장할 리스트
                    vegetarian_meals = []

                    for meal in meals:
                        if meal['MMEAL_SC_CODE'] == '3':  # 석식인 경우만 처리
                            # 메뉴 정보에서 괄호와 괄호 안의 내용 제거
                            cleaned_menus = re.sub(r'\([^)]*\)', '', meal['DDISH_NM'])
                            cleaned_menus = cleaned_menus.replace("<br/>", "\n").strip()
                            # 개별 메뉴를 리스트에 추가
                            vegetarian_meals.extend(cleaned_menus.split('\n'))
                            CAL_INFO= meal['CAL_INFO']
                    
                    if not vegetarian_meals:
                        print("석식에 대한 급식이 없습니다.")
                        vegetarian = {"meals":None,"CAL_INFO":None}
                        with open('./json/dinner.json', 'w', encoding='utf-8') as json_file:
                            json.dump(vegetarian, json_file, ensure_ascii=False, indent=4)
                    else:
                        print("석식 급식 메뉴를 성공적으로 가져왔습니다.")
                        vegetarian = {"meals":vegetarian_meals,"CAL_INFO":CAL_INFO}
                        with open('./json/dinner.json', 'w', encoding='utf-8') as json_file:
                            json.dump(vegetarian, json_file, ensure_ascii=False, indent=4)

                        with open('./json/dinner.json', 'r', encoding='utf-8') as json_file:
                            meal_data_loaded = json.load(json_file)

                        print("석식 메뉴 리스트가 dinner.json 파일에 저장되었습니다.")
                        # meal_data_loaded 사용 예시
                        W = 1080
                        H = 1080
                        image_path = './assets/images/001.jpg'
                        image = Image.open(image_path)
                        draw = ImageDraw.Draw(image)

                        font = loadfont(36)

                        date_font_color = 'rgb(69, 122, 250)'
                        b = 'rgb(0, 0, 0)'

                        text = f'{year}년 {month}월 {day}일 {weekday}요일'
                        draw.text((W - 392 - 90, 75), text, fill=date_font_color, font=font)
                        draw.text((W - 245 - 90, 120), '석식 급식 목록', fill=b, font=font)
                                        
                        gddg = f'칼로리: {meal_data_loaded["CAL_INFO"]}'

                        draw.text((W - 245 - 150, 999), gddg, fill=0x6A6A6A, font=loadfont(36))
                                        
                        meal_font = loadfont(60)
                        meal_font_color = 'rgb(69, 122, 250)'

                        text_l = 70

                        for l in reversed(meal_data_loaded["meals"]):
                            draw.text((75, H - 75 - text_l), l, font=meal_font, fill=meal_font_color)
                            text_l += 85

                        image.convert('RGB').save('./build/dinner.jpg', quality=95)
                        print('석식 이미지 생성 완료!')
                
                except KeyError:
                    print("급식 정보를 처리하는 중 오류가 발생했습니다.")
                    meal_data_loaded = {"meals": None, "CAL_INFO": None}
                    with open('./json/dinner.json', 'w', encoding='utf-8') as json_file:
                        json.dump(meal_data_loaded, json_file, ensure_ascii=False, indent=4)
            except Exception as e:
                print("API 요청 또는 처리 중 오류가 발생했습니다:", str(e))
                # meal_data_loaded = {"meals": None, "CAL_INFO": None}
                # with open('./json/dinner.json', 'w', encoding='utf-8') as json_file:
                #     json.dump(meal_data_loaded, json_file, ensure_ascii=False, indent=4)
    except Exception as e:
        print("에러 발생:", str(e))
        meal_data_loaded = {"meals": None, "CAL_INFO": None}
        with open('./json/dinner.json', 'w', encoding='utf-8') as json_file:
            json.dump(meal_data_loaded, json_file, ensure_ascii=False, indent=4)
        
def main():
    school_meal()
    school_meal2()
    school_meal3()

main()