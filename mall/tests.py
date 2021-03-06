from django.contrib.auth.models import User
from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Product, Category, Comment

# Create your tests here.
class TestView(TestCase):
    def setUp(self):
        self.client = Client()

        self.user_trump = User.objects.create_user(username='trump', password='somepassword')
        self.user_james = User.objects.create_user(username='james', password='somepassword')
        self.user_james.is_staff = True
        self.user_james.save()

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

        self.comment_001 = Comment.objects.create(
            product=self.product_001,
            author=self.user_trump,
            content='상품이 아주 멋지네요!'
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

    def test_create_product(self):
        response = self.client.get('/mall/create_product/')
        self.assertNotEqual(response.status_code, 200)

        self.client.login(username='trump', password='somepassword')
        response = self.client.get('/mall/create_product/')
        self.assertNotEqual(response.status_code, 200)

        self.client.login(username='james', password='somepassword')
        response = self.client.get('/mall/create_product/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Create Product', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Create New Product', main_area.text)

        self.client.post(
            '/mall/create_product/',
            {
                'name': '카메라1',
                'price': 2000,
                'content': "카메라1 입니다.",
                'product_color': 'black',
                'product_size': '130 x 100 x 30',
            }
        )
        last_product = Product.objects.last()
        self.assertEqual(last_product.name, '카메라1')
        self.assertEqual(last_product.author.username, 'james')

    def test_update_product(self):
        update_product_url = f'/mall/update_product/{self.product_001.pk}/'

        response = self.client.get(update_product_url)
        self.assertNotEqual(response.status_code, 200)

        self.assertNotEqual(self.product_001.author, self.user_james)
        self.client.login(
            username=self.user_james.username,
            password='somepassword'
        )
        response = self.client.get(update_product_url)
        self.assertEqual(response.status_code, 403)

        self.client.login(
            username=self.product_001.author.username,
            password='somepassword'
        )
        response = self.client.get(update_product_url)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Edit Product', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Edit Product', main_area.text)

        response = self.client.post(
            update_product_url,
            {
                'name':'첫 번째 상품 수정',
                'price':20000,
                'content':'첫 번째 상품 수정입니다.',
                'product_color':'Red',
                'product_size':'100*100*30',
                'category':self.category_instax,
            },
            follow=True
        )
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('첫 번째 상품 수정', main_area.text)
        self.assertIn('첫 번째 상품 수정입니다.', main_area.text)
        self.assertIn(self.category_instax.name, main_area.text)


    def test_category_page(self):
        response = self.client.get(self.category_instax.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        # self.assertIn(self.category_instax.name, soup.h1.text)

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

        # comment
        comments_area = soup.find('div', id='comment-area')
        comment_001_area = comments_area.find('div', id='comment-1')
        self.assertIn(self.comment_001.author.username, comment_001_area.text)
        self.assertIn(self.comment_001.content, comment_001_area.text)

    def test_comment_form(self):
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(self.product_001.comment_set.count(), 1)

        response = self.client.get(self.product_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertIn('Log in and leave a comment', comment_area.text)
        self.assertFalse(comment_area.find('form', id='comment-form'))

        self.client.login(username='trump', password='somepassword')
        response = self.client.get(self.product_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertNotIn('Log in and leave a comment', comment_area.text)

        comment_form = comment_area.find('form', id='comment-form')
        self.assertTrue(comment_form.find('textarea', id='id_content'))
        response = self.client.post(
            self.product_001.get_absolute_url()+'new_comment/',
            {
                'content': "트럼프의 댓글입니다.",
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(self.product_001.comment_set.count(), 2)
        new_comment = Comment.objects.last()

        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertIn(new_comment.product.name, soup.title.text)

        comment_area = soup.find('div', id='comment-area')
        new_comment_div = comment_area.find('div', id=f'comment-{new_comment.pk}')
        self.assertIn('trump', new_comment_div.text)
        self.assertIn('트럼프의 댓글입니다.', new_comment_div.text)

    def test_comment_update(self):
        comment_by_trump = Comment.objects.create(
            product=self.product_001,
            author=self.user_trump,
            content='트럼프의 댓글입니다.'
        )
        response = self.client.get(self.product_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertFalse(comment_area.find('a', id='comment-1-update-btn'))
        self.assertFalse(comment_area.find('a', id='comment-2-update-btn'))

        self.client.login(id='trump', password='somepassword')
        response = self.client.get(self.product_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertFalse(comment_area.find('a', id='comment-2-update-btn'))
        comment_001_update_btn = comment_area.find('a', id='comment-1-update-btn')
        # self.assertIn('edit', comment_001_update_btn.text)
        # self.assertEqual(comment_001_update_btn.attrs['href'], '/mall/update_comment/1/')

        response = self.client.get('/mall/update_comment/1/')
        # self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Edit Comment', soup.title.text)
        update_comment_form = soup.find('form', id='comment-form')
        content_textarea = update_comment_form.find('textarea', id='id_content')
        self.assertIn(self.comment_001.content, content_textarea.text)

        response = self.client.post(
            f'/mall/update_comment/{self.comment_001.pk}/',
            {
                'content': "트럼프의 댓글 수정",
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        comment_001_div = soup.find('div', id='comment-1')
        self.assertIn('트럼프의 댓글 수정', comment_001_div.text)
        self.assertIn('Updated: ', comment_001_div.text)

    def test_delete_comment(self):
        comment_by_trump = Comment.objects.create(
            product= self.product_001,
            author=self.user_trump,
            content='트럼프의 댓글'
        )
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(self.product_001.comment_set.count(), 2)

        response = self.client.get(self.product_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertFalse(comment_area.find('a', id='comment-1-delete-btn'))
        self.assertFalse(comment_area.find('a', id='comment-2-delete-btn'))

        self.client.login(username='trump', password='somepassword')
        response = self.client.get(self.product_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        comment_001_delete_modal_btn = comment_area.find('a', id='comment-1-delete-modal-btn')
        comment_002_delete_modal_btn = comment_area.find('a', id='comment-2-delete-modal-btn')
        self.assertIn('delete', comment_002_delete_modal_btn.text)
        self.assertEqual(
            comment_002_delete_modal_btn.attrs['data-target'],
            '#deleteCommentModal-2'
        )

        delete_comment_modal_002 = soup.find('div', id='deleteCommentModal-2')
        self.assertIn('Are You Sure?', delete_comment_modal_002.text)
        really_delete_btn_002 = delete_comment_modal_002.find('a')
        self.assertIn('Delete', really_delete_btn_002.text)
        self.assertEqual(
            really_delete_btn_002.attrs['href'],
            '/mall/delete_comment/2/'
        )

        response = self.client.get('/mall/delete_comment/2/', follow=True)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertIn(self.product_001.name, soup.title.text)
        comment_area = soup.find('div', id='comment-area')
        self.assertNotIn('트럼프의 댓글', comment_area.text)

        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(self.product_001.comment_set.count(), 1)





