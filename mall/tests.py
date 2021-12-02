from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Product

# Create your tests here.
class TestView(TestCase):
    def setUp(self):
        self.client = Client()

    def test_product_list(self):
        # 상품 목록 페이지 가져오기
        response = self.client.get('/mall/')
        # 정상적으로 페이지 로드
        self.assertEqual(response.status_code, 200)
        # 페이지 타이틀 Camera Mall
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text, 'Camera Mall')
        # 네비게이션 바 존재
        navbar = soup.nav
        # Product, About Company라는 문구가 내비게이션 바에 존재
        self.assertIn('Product', navbar.text)
        self.assertIn('About Company', navbar.text)

        # 상품이 하나도 없을 경우
        self.assertEqual(Product.objects.count(), 0)
        # main-area에 '아직 상품이 없습니다'라는 문구가 나타난다.
        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 상품이 없습니다', main_area.text)

        # 상품이 2개 있다면
        product_001 = Product.objects.create(
            name='첫 번째',
            price=1000,
            content='첫 번째 상품입니다.',
            product_color='Red',
            product_size='100*100*30',
        )
        product_002 = Product.objects.create(
            name='두 번째',
            price=7000,
            content='두 번째 상품입니다.',
            product_color='Yello',
            product_size='200*80*30',
        )
        self.assertEqual(Product.objects.count(), 2)

        # 상품 목록 페이지를 새로고침했을 때
        response = self.client.get('/mall/')
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(response.status_code, 200)
        # main-area에 상품 2개의 상품명 존재
        main_area = soup.find('div', id='main-area')
        self.assertIn(product_001.name, main_area.text)
        self.assertIn(product_002.name, main_area.text)
        # '아직 게시물이 없습니다'라는 문구 나타나지 않음
        self.assertNotIn('아직 상품이 없습니다', main_area.text)