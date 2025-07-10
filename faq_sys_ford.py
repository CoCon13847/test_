import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys # Keys는 더 이상 사용되지 않지만, 임포트 목록에서 제거하지 않음 (사용자 요청에 따라)
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import json
import mysql.connector
from mysql.connector import Error

# --- MySQL 연결 설정 ---
db_config = {
    'host': 'localhost',
    'user': 'sehee',
    'password': 'sehee', # TODO: 실제 'sehee' 유저의 비밀번호를 확인하여 입력해주세요.
    'database': 'project1db' 
}

# --- 크롤링 설정 ---
FRONTIER_FORD_FAQ_URL = "https://www.frontierford.com/faq/ford-electric-lineup.htm?srsltid=AfmBOooBqN_a6WwQzWidD_fI7v7RV0FVtLepfbByBUO7VGRhPYe_fvdT"
CHROME_DRIVER_PATH = r"C:\Users\Playdata\OneDrive\바탕 화면\skn_17\python_basic\z_Cocon\chromedriver.exe" # chromedriver.exe 파일 경로
TOTAL_FAQ_ITEMS = 9 # Ford FAQ 목록의 총 개수 (사용자 제공)

def setup_webdriver():
    """크롬 웹 드라이버를 설정하고 반환합니다."""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized") # 브라우저 최대화
    options.add_experimental_option("excludeSwitches", ["enable-logging"]) # 불필요한 로그 메시지 제거

    try:
        service = Service(CHROME_DRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
        print("사용자 지정 경로로 ChromeDriver를 시작합니다.")
    except Exception as e:
        print(f"사용자 지정 경로로 ChromeDriver 시작 실패: {e}. webdriver_manager를 사용합니다.")
        # webdriver_manager를 사용하여 드라이버 자동 설치 및 실행
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    return driver

def scroll_to_bottom(driver):
    """페이지의 끝까지 스크롤하여 동적으로 로드되는 콘텐츠를 가져옵니다.
    Ford FAQ 페이지에서는 필요 없을 수 있지만, 안전하게 유지합니다."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1) # 짧게 대기
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height: # 더 이상 스크롤할 내용이 없으면 중단
            break
        last_height = new_height
    print("페이지 끝까지 스크롤 완료.")

def save_to_json_file(data, filename="ford_electric_faq_data.json"):
    """크롤링한 데이터를 JSON 파일로 저장합니다."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4) # 한글 인코딩 및 들여쓰기
        print(f"크롤링 데이터가 '{filename}' 파일에 성공적으로 저장되었습니다.")
    except Exception as e:
        print(f"JSON 파일 저장 중 오류 발생: {e}")

def setup_database():
    """MySQL 데이터베이스에 연결하고 테이블을 생성합니다."""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # 테이블 생성 쿼리 (faq_id, title, content)
        # 테이블 이름을 'ford_faq'로 변경합니다.
        create_table_query = """
        CREATE TABLE IF NOT EXISTS ford_faq (
            faq_id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(512) NOT NULL,
            content TEXT NOT NULL,
            crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_query)
        conn.commit()
        print(f"MySQL 데이터베이스 '{db_config['database']}' 연결 및 'ford_faq' 테이블 설정 완료.")
        return conn, cursor
    except Error as err:
        print(f"MySQL 오류 발생: {err}")
        return None, None

def insert_data_to_db(cursor, conn, data):
    """크롤링한 데이터를 MySQL 데이터베이스에 삽입합니다."""
    insert_query = "INSERT INTO ford_faq (title, content) VALUES (%s, %s)"
    try:
        cursor.execute(insert_query, (data['title'], data['content']))
        conn.commit()
        print(f"DB에 데이터 삽입 완료: {data['title'][:30]}...") # 제목이 길면 일부만 출력
    except Error as err:
        print(f"DB 데이터 삽입 오류 발생: {err}")
        conn.rollback() # 오류 발생 시 롤백


def crawl_ford_faq():
    """Ford FAQ 페이지에서 질문과 답변을 크롤링합니다."""
    driver = None
    conn = None
    cursor = None
    faq_data = [] # JSON 파일 저장을 위한 리스트

    try:
        driver = setup_webdriver()
        driver.get(FRONTIER_FORD_FAQ_URL)
        time.sleep(5) # 페이지 로딩을 충분히 기다립니다.

        # Ford FAQ 페이지에는 검색창이 없으므로, 검색 관련 로직은 제거합니다.
        # 이전 코드의 검색 관련 부분 (search_input_xpath, search_input.send_keys 등)이 완전히 삭제되었습니다.

        # 모든 FAQ 항목이 DOM에 로드되도록 페이지를 스크롤합니다.
        # 9개 항목이 모두 초기 로드 시 보인다면 이 함수 호출은 제거해도 됩니다.
        scroll_to_bottom(driver)
        time.sleep(2) # 스크롤 후 DOM 안정화 대기

        # MySQL 데이터베이스 연결 설정
        conn, cursor = setup_database()
        if not conn or not cursor:
            print("데이터베이스 설정 실패로 DB 저장 기능을 건너뜜.")

        # --- XPATH 활용하여 질문과 답변 추출 ---
        # 사용자 제공 XPATH를 기반으로 동적 XPATH를 생성합니다.
        # XPath 인덱스는 1부터 시작하므로 range(1, TOTAL_FAQ_ITEMS + 1)
        for i in range(1, TOTAL_FAQ_ITEMS + 1):
            # Ford FAQ 페이지의 질문 제목 XPATH
            question_xpath = f'//*[@id="page-body"]/div[2]/div[1]/div[2]/div/h2[{i}]'
            # Ford FAQ 페이지의 답변 내용 XPATH
            answer_xpath = f'//*[@id="page-body"]/div[2]/div[1]/div[2]/div/p[{i}]'
            
            try:
                question_element = driver.find_element(By.XPATH, question_xpath)
                title = question_element.text.strip()
                
                # 답변 내용은 질문과 동일한 인덱스를 가진 <p> 태그에 바로 있다고 가정합니다.
                # 따라서 질문을 클릭하여 내용을 펼치는 로직은 필요 없습니다.
                answer_element = driver.find_element(By.XPATH, answer_xpath)
                content = answer_element.text.strip()

                # 수집된 데이터를 리스트에 추가 (JSON 파일 저장을 위함)
                faq_data.append({'title': title, 'content': content})
                print(f"데이터 수집 완료 ({len(faq_data)}/{TOTAL_FAQ_ITEMS}): {title[:30]}...")

                # MySQL DB에 저장
                if conn and cursor:
                    insert_data_to_db(cursor, conn, {'title': title, 'content': content})

            except NoSuchElementException:
                print(f"경고: {i}번째 질문 또는 답변 요소를 찾을 수 없습니다. (질문 XPATH: {question_xpath}, 답변 XPATH: {answer_xpath}). 다음으로 넘어갑니다.")
                continue # 해당 인덱스에 요소가 없으면 다음 루프로 넘어감
            except Exception as e:
                print(f"오류: {i}번째 FAQ 처리 중 예상치 못한 오류 발생: {e}")
                continue

    except TimeoutException:
        print("오류: 페이지 로딩 시간이 초과되었습니다.")
    except Exception as e:
        print(f"크롤링 중 전반적인 오류 발생: {e}")
    finally:
        if driver:
            driver.quit()
            print("웹 드라이버 종료.")
        
        # 크롤링 완료 후 수집된 데이터가 있다면 JSON 파일로 저장
        if faq_data:
            save_to_json_file(faq_data)
        
        # MySQL 연결 종료
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            print("MySQL 연결 종료.")

if __name__ == "__main__":
    crawl_ford_faq() # 함수 이름도 'crawl_ford_faq'로 변경