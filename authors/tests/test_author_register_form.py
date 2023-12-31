from unittest import TestCase

from authors.forms import RegisterForm
from django.test import TestCase as DjangoTestCase
from django.urls import reverse
from parameterized import parameterized


class AuthorRegisterFormUnitTest(TestCase):
    # testa se os placesholders dos campos estão ok
    @parameterized.expand([
        ('username', 'Digite seu nome de usuário'),
        ('email', 'Digite seu e-mail'),
        ('first_name', 'Digite seu primeiro nome'),
        ('last_name', 'Digite seu sobrenome'),
        ('password', 'Sua senha'),
        ('password2', 'Digite novamente sua senha'),
    ])
    def test_fields_placeholder_is_correct(self, field, placeholder):
        form = RegisterForm()
        current_placeholder = form[field].field.widget.attrs['placeholder']
        self.assertEqual(current_placeholder, placeholder)

# Teste que verifica se help_text corresponde aos campos
    @parameterized.expand([
        ('username', (
            'Obrigatório. 150 caracteres ou menos. '
            'Letras, números e @/./+/-/_ apenas.')),
        ('email', 'O e-mail deve ser válido.'),
        ('password', (
            'Senha deve ter pelo menos um caracter maiúsculo, '
            'um caracter minúsculo e um número. A senha deve '
            'possuir pelo menos 8 caracteres.')),
    ])
    def test_fields_help_text(self, field, needed):
        form = RegisterForm()
        current = form[field].field.help_text
        self.assertEqual(current, needed)

# Teste que verifica se os labels correspondem aos campos
    @parameterized.expand([
        ('username', 'Nome do usuário'),
        ('first_name', 'Nome'),
        ('last_name', 'Sobrenome'),
        ('email', 'E-mail'),
        ('password', 'Digite sua senha'),
        ('password2', 'Confirme sua senha'),
    ])
    def test_fields_label(self, field, needed):
        form = RegisterForm()
        current = form[field].field.label
        self.assertEqual(current, needed)

# Classe de teste de integração do form


class AuthorRegisterFormIntegrationTest(DjangoTestCase):

    def setUp(self, *args, **kwargs):
        self.form_data = {
            'username': 'user',
            'first_name': 'first',
            'last_name': 'last',
            'email': 'email@anyemail.com',
            'password': 'Str0ngP@ssword1',
            'password2': 'Str0ngP@ssword1',
        }
        return super().setUp(*args, **kwargs)

# Teste que verifica quando o campo está vazio
    @parameterized.expand([
        ('first_name', 'Este campo não pode estar vazio'),
        ('last_name', 'Este campo não pode estar vazio'),
        ('username', 'Este campo não pode estar vazio'),
        ('email', 'E-mail é obrigatório'),
        ('username', 'Este campo não pode estar vazio'),
        ('password', 'A senha não pode estar vazia'),
        ('password2', 'A senha não pode estar vazia'),

    ])
    def test_fields_cannot_be_empty(self, field, msg):
        self.form_data[field] = ''
        url = reverse('authors:register_create')
        response = self.client.post(url, data=self.form_data, follow=True)
        self.assertIn(msg, response.content.decode('utf-8'))
        self.assertIn(msg, response.context['form'].errors.get(field))

# Testa o tamanho mínimo do nome de usuário
    def test_username_field_min_lenght_should_be_4(self):
        self.form_data['username'] = 'jao'
        url = reverse('authors:register_create')
        response = self.client.post(url, data=self.form_data, follow=True)

        msg = ('O nome de usuário deve conter '
               'no mínimo 4 caracteres')

        self.assertIn(msg, response.content.decode('utf-8'))
        self.assertIn(msg, response.context['form'].errors.get('username'))

# Testa o tamanho máximo do nome de usuário
    def test_username_field_max_length_should_be_150(self):
        self.form_data['username'] = 'A' * 151
        url = reverse('authors:register_create')
        response = self.client.post(url, data=self.form_data, follow=True)

        msg = ('O nome de usuário deve conter '
               'no máximo 150 caracteres')

        self.assertIn(msg, response.context['form'].errors.get('username'))
        self.assertIn(msg, response.content.decode('utf-8'))

# Testa se o inverso e o correto se a senha possui maisc, minsc e numeros
    def test_password_field_have_lower_upper_case_letters_and_numbers(self):
        self.form_data['password'] = 'abc123'
        url = reverse('authors:register_create')
        response = self.client.post(url, data=self.form_data, follow=True)

        msg = (
            'A senha deve ter no mínimo uma letra maiúscula, '
            'Uma letra minúscula e um número. A senha deve '
            'possuir pelo menos 8 caracteres.'
        )

        self.assertIn(msg, response.context['form'].errors.get('password'))
        self.assertIn(msg, response.content.decode('utf-8'))

        self.form_data['password'] = '@A123abc123'
        url = reverse('authors:register_create')
        response = self.client.post(url, data=self.form_data, follow=True)

        self.assertNotIn(msg, response.context['form'].errors.get('password'))

# Testa se as duas senhas sao iguais no inverso e no correto
    def test_password_and_password_confirmation_are_equal(self):
        self.form_data['password'] = '@A123abc123'
        self.form_data['password2'] = '@A123abc1235'

        url = reverse('authors:register_create')
        response = self.client.post(url, data=self.form_data, follow=True)

        msg = 'As senhas devem ser iguais'

        self.assertIn(msg, response.context['form'].errors.get('password'))
        self.assertIn(msg, response.content.decode('utf-8'))

        self.form_data['password'] = '@A123abc123'
        self.form_data['password2'] = '@A123abc123'

        url = reverse('authors:register_create')
        response = self.client.post(url, data=self.form_data, follow=True)

        self.assertNotIn(msg, response.content.decode('utf-8'))

    # Teste que retorna 404 se nao foi feito request POST
    def test_send_get_request_to_registration_create_view_returns_404(self):
        url = reverse('authors:register_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    # Teste que cria um usuario com email ja existente
    def test_email_field_must_be_unique(self):
        url = reverse('authors:register_create')

        self.client.post(url, data=self.form_data, follow=True)
        response = self.client.post(url, data=self.form_data, follow=True)

        msg = 'Esse e-mail já está em uso'
        self.assertIn(msg, response.context['form'].errors.get('email'))
        self.assertIn(msg, response.content.decode('utf-8'))

# Teste que verifica se o usuario pode logar
    def test_author_created_can_login(self):
        url = reverse('authors:register_create')

        self.form_data.update({
            'username': 'testuser',
            'password': '@Bc123456',
            'password2': '@Bc123456',
        })

        self.client.post(url, data=self.form_data, follow=True)

        is_authenticated = self.client.login(
            username='testuser',
            password='@Bc123456'
        )

        self.assertTrue(is_authenticated)
