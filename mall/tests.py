from django.contrib.auth.models import User
from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Product, Category

# Create your tests here.
class TestView(TestCase):
    def setUp(self):
        self.client = Client()

        self.user_trump = User.objects.create_user(username='trump', password='somepassword')

        self.category_instax = Category.objects.create(name='instax', slug='instax')
        self.category_fujifilm = Category.objects.create(name='fujifilm', slug='fujifilm')

        self.product_001 = Product.objects.create(
            name='첫 번째',
            price=1000,
            content='첫 번째 상품입니다.',
            product_color='Red',
            product_size='100*100*30',
            category=self.category_instax,
            author=self.user_trump,
        )
        self.product_002 = Product.objects.create(
            name='두 번째',
            price=7000,
            content='두 번째 상품입니다.',
            product_color='Yello',
            product_size='200*80*30',
            category=self.category_fujifilm,
            author=self.user_trump,
        )
        self.product_003 = Product.objects.create(
            name='세 번째',
            price=20000,
            content='세 번째 상품입니다.',
            product_color='black',
            product_size='130*130*90',
            author=self.user_trump,
        )

    def category_card_test(self, soup):
        categories_card = soup.find('div', id='categories-card')
        self.assertIn('Categories', categories_card.text)
        self.assertIn(f'{self.category_instax.name} ({self.category_instax.product_set.count()})', categories_card.text)
        self.assertIn(f'{self.category_fujifilm.name} ({self.category_instax.product_set.count()})',
                      categories_card.text)
        self.assertIn(f'미분류 (1)', categories_card.text)

    def navbar_test(self, soup):
        # 네비게이션 바 존재
        navbar = soup.nav
        # Product, About Company라는 문구가 내비게이션 바에 존재
        self.assertIn('Product', navbar.text)
        self.assertIn('About Company', navbar.text)

    def test_category_page(self):
        response = self.client.get(self.category_instax.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.category_instax.name, soup.h1.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.category_instax.name, main_area.text)
        self.assertIn(self.product_001.name, main_area.text)
        self.assertNotIn(self.product_002.name, main_area.text)
        self.assertNotIn(self.product_003.name, main_area.text)

    def test_product_list(self):
        self.assertEqual(Product.objects.count(), 3)

        response = self.client.get('/mall/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        main_area = soup.find('div', id='main-area')
        self.assertNotIn('아직 상품이 없습니다', main_area.text)

        product_001_card = main_area.find('div', id='product-1')
        self.assertIn(self.product_001.name, product_001_card.text)
        self.assertIn(self.product_001.category.name, product_001_card.text)

        product_002_card = main_area.find('div', id='product-2')
        self.assertIn(self.product_002.name, product_002_card.text)
        self.assertIn(self.product_002.category.name, product_002_card.text)

        product_003_card = main_area.find('div', id='product-3')
        self.assertIn('미분류', product_003_card.text)
        self.assertIn(self.product_003.name, product_003_card.text)

        # 포스트 없는 경우
        Product.objects.all().delete()
        self.assertEqual(Product.objects.count(), 0)
        response = self.client.get('/mall/')
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 상품이 없습니다', main_area.text)

    def test_product_detail(self):
        # 이 상품의 url은 'mall/1'이다
        self.assertEqual(self.product_001.get_absolute_url(), '/mall/1/')

        # 첫 번째 상품의 url로 접근하면 정상적으로 작동
        response = self.client.get(self.product_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        # 상품의 상품명이 타이틀에 있다
        self.assertIn(self.product_001.name, soup.title.text)

        # 상품의 상품명이 상품 영역에 있다
        main_area = soup.find('div', id='main-area')
        product_area = main_area.find('div', id='product-area')
        self.assertIn(self.product_001.name, product_area.text)
        self.assertIn(self.category_instax.name, product_area.text)

        # 상품의 상품 설명이 상품 영역에 있다
        self.assertIn(self.product_001.content, product_area.text)







