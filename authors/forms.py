import re

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


# funcao para modificar algum atributo
def add_attr(field, attr_name, attr_new_val):
    existing = field.widget.attrs.get(attr_name, '')
    field.widget.attrs[attr_name] = f'{existing} {attr_new_val}'.strip()


# funcao para adicionar placeholder
def add_placeholder(field, placeholder_val):
    add_attr(field, 'placeholder', placeholder_val)


# criação de senha forte
def strong_password(password):
    regex = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9]).{8,}$')

    if not regex.match(password):
        raise ValidationError((
            'A senha deve ter no mínimo uma letra maiúscula, '
            'Uma letra minúscula e um número. A senha deve '
            'possuir pelo menos 8 caracteres.'
        ),
            code='invalid'
        )


class RegisterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_placeholder(self.fields['username'], 'Digite seu nome de usuário')
        add_placeholder(self.fields['first_name'], 'Digite seu primeiro nome')
        add_placeholder(self.fields['last_name'], 'Digite seu sobrenome')
        add_placeholder(self.fields['email'], 'Digite seu e-mail')

    # Primeiro nome
    first_name = forms.CharField(
        error_messages={
            'required': 'Este campo não pode estar vazio'
        },
        label='Nome'
    )

    # Sobrenome
    last_name = forms.CharField(
        error_messages={'required': 'Este campo não pode estar vazio'},
        label='Sobrenome'
    )

    # Nome do usuário
    username = forms.CharField(
        error_messages={
            'required': 'Este campo não pode estar vazio'
        },
        label='Nome do usuário',
        help_text='Obrigatório.'
        ' 150 caracteres ou menos. '
        'Letras, números e @/./+/-/_ apenas.'
    )

    # Email
    email = forms.EmailField(
        error_messages={
            'required': 'E-mail é obrigatório'
        },
        label='E-mail',
        help_text='O e-mail deve ser válido.',
    )

    # Senha principal
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Sua senha'
        }),
        error_messages={
            'required': 'A senha não pode estar vazia'
        },
        help_text=(
            'Senha deve ter pelo menos um caracter maiúsculo, '
            'um caracter minúsculo e um número. A senha deve '
            'possuir pelo menos 8 caracteres.'
        ),
        label='Digite sua senha',
        validators=[strong_password]
    )

    # Senha confirmacao
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Digite novamente sua senha'
        }),
        error_messages={
            'required': 'A senha não pode estar vazia'
        },
        label='Confirme sua senha',
    )

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'password',
        ]

    # metodo para verificar se os campos de senhas sao iguais
    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')

        if password != password2:
            password_confirmation_error = ValidationError(
                'As senhas devem ser iguais ',
                code='invalid'
            )
            raise ValidationError({
                'password': password_confirmation_error,
                'password2': [
                    password_confirmation_error,
                ],
            })
