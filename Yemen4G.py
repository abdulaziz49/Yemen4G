import re
from bs4 import BeautifulSoup
import requests
import cv2
import numpy as np
import easyocr


class Yemen4G:
    def __init__(self):
        self.yemen4G_number = '123456789'
        self.session = requests.Session()
        self.reader = easyocr.Reader(['en'])  # Initialize EasyOCR reader
        self.ocrCode = ""
        self.patteren = r'<input\s+type=["\']hidden["\']\s+id=["\']querybillnew_field["\']\s+name=["\']querybillnew_field["\']\s+value=["\']([^"\']+)["\']'
        self.querybillnew_field = ""

    def first_requests(self):
        headers = {
            'Host': 'ptc.gov.ye',
            'Sec-Ch-Ua': '"Not?A_Brand";v="99", "Chromium";v="130"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Accept-Language': 'en-US,en;q=0.9',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.70 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Referer': 'https://www.google.com/',
            'Priority': 'u=0, i',
            'Connection': 'keep-alive',
        }
        params = {
            'page_id': '9017',
        }
        response = requests.get('https://ptc.gov.ye/', params=params, headers=headers, )

        match = re.search(self.patteren, response.text)
        if match:
            self.querybillnew_field = match.group(1)  # Get the captured value

    def fetch_captcha(self):
        headers = {
            'Host': 'ptc.gov.ye',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Accept-Language': 'en-US,en;q=0.9',
            'Sec-Ch-Ua': '"Not?A_Brand";v="99", "Chromium";v="130"',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.70 Safari/537.36',
            'Sec-Ch-Ua-Mobile': '?0',
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Dest': 'image',
            'Referer': 'https://ptc.gov.ye/?page_id=9017',
            'Priority': 'i',
            'Connection': 'keep-alive',
        }

        response = self.session.get(
            'https://ptc.gov.ye/wp-content/plugins/quarybillcbs-api-plug/securimage/securimage_show.php?0.7838750307787508',
            headers=headers,
        )

        # Check if the request was successful
        if response.status_code == 200:
            return response.content
        else:
            print("Failed to retrieve Captcha:", response.status_code)
            return None

    def solve_captcha(self):
        while (len(self.ocrCode) != 5):
            captcha_content = self.fetch_captcha()  # Return Image Content
            if captcha_content:
                # Convert the response content to a NumPy array
                image_array = np.frombuffer(captcha_content, np.uint8)

                # Decode the image array into an OpenCV format
                image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

                # Perform OCR on the image
                result = self.reader.readtext(image)

                # Extract and print the text from the result
                for (bbox, text, prob) in result:
                    self.ocrCode = text
            else:
                print("No content to process.")

    def send_finall_request(self, ocrCode):
        headers = {
            'Host': 'ptc.gov.ye',
            'Cache-Control': 'max-age=0',
            'Sec-Ch-Ua': '"Not?A_Brand";v="99", "Chromium";v="130"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://ptc.gov.ye',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.70 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Referer': 'https://ptc.gov.ye/?page_id=9017',
            'Priority': 'u=0, i',
            'Connection': 'keep-alive',
        }
        params = {
            'page_id': '9017',
        }

        data = {
            'querybillnew_field': self.querybillnew_field,
            '_wp_http_referer': '/?page_id=9017',
            'doqbillnew': 'querybillvaluenew',
            'phoneidnew': {self.yemen4G_number},
            'captcha_code_qbillnew': {ocrCode},
            'qsubmitnew': 'استعلام',
        }

        response = self.session.post('https://ptc.gov.ye/', params=params, headers=headers, data=data)
        # استخدام BeautifulSoup لتحليل الـ HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # استخراج المعلومات من الجدول
        data = {}
        table = soup.find('table', class_='transdetail')

        for row in table.find_all('tr'):
            cells = row.find_all(['th', 'td'])
            if len(cells) == 2:
                key = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)
                data[key] = value

        # طباعة الجدول باستخدام النجوم
        print("*" * 50)
        print(f"{'المعلومات':<40} {'القيمة':<10}")
        print("*" * 50)

        # إضافة البيانات إلى الجدول
        for key, value in data.items():
            print(f"{key:<40} {value:<10}")

        print("*" * 50)

    def run(self):
        self.first_requests()
        self.solve_captcha()
        self.send_finall_request(self.ocrCode)


# Usage
if __name__ == "__main__":
    captcha_solver = Yemen4G()
    captcha_solver.run()
