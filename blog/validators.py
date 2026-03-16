# blog/validators.py
import re
import html
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone

# Разрешённые домены email (Яндекс, Mail.ru, Gmail и официальные)
ALLOWED_EMAIL_DOMAINS = getattr(settings, 'ALLOWED_EMAIL_DOMAINS', [
    'yandex.ru',
    'yandex.com',
    'ya.ru',
    'mail.ru',
    'inbox.ru',
    'list.ru',
    'bk.ru',
    'gmail.com',
    'example.com',
    'company.org',
    'outlook.com',
    'hotmail.com',
    'icloud.com',
    'protonmail.com',
    'tutanota.com'
])

# Запрещённые паттерны (XSS, SQL-инъекции, template-инъекции)
FORBIDDEN_PATTERNS = [
    (r'<script[^>]*>.*?</script>', 'HTML-теги script'),
    (r'javascript:', 'JavaScript protocol'),
    (r'on\w+\s*=', 'Event handlers (onclick, onerror, etc.)'),
    (r'<iframe[^>]*>', 'iframe tags'),
    (r'<object[^>]*>', 'object tags'),
    (r'<embed[^>]*>', 'embed tags'),
    (r'union\s+select', 'SQL injection UNION'),
    (r'drop\s+table', 'SQL injection DROP'),
    (r'insert\s+into', 'SQL injection INSERT'),
    (r'delete\s+from', 'SQL injection DELETE'),
    (r'update\s+.*\s+set', 'SQL injection UPDATE'),
    (r'--\s*$', 'SQL comments'),
    (r';\s*$', 'SQL statement terminator'),
    (r'\bxor\b', 'SQL operators'),
    (r'\bbenchmark\b', 'SQL functions'),
    (r'\bsleep\b', 'SQL functions'),
    (r'\bload_file\b', 'SQL functions'),
    (r'<\?php', 'PHP tags'),
    (r'<%', 'ASP tags'),
    (r'{{.*}}', 'Template injection Django'),
    (r'{%.*%}', 'Template tags Django'),
    (r'\$\{.*\}', 'Expression injection'),
    (r'eval\s*\(', 'Code execution eval'),
    (r'exec\s*\(', 'Code execution exec'),
    (r'system\s*\(', 'Code execution system'),
]

# Распространённые пароли (запрещены)
COMMON_PASSWORDS = [
    'password', 'qwerty', '123456', '123456789', 'admin', 'letmein',
    'welcome', 'monkey', 'dragon', 'master', 'login', 'abc123',
    '111111', '123123', '12345678', 'iloveyou', 'sunshine', 'princess',
    'password123', 'admin123', 'root123', 'qwerty123'
]

# Запрещённые слова в username
FORBIDDEN_USERNAMES = ['admin', 'root', 'system', 'administrator', 'moderator', 'support']


def sanitize_input(value):
    """Очистка ввода от опасных символов"""
    if not value:
        return value
    value = str(value).strip()
    value = html.escape(value)
    value = ' '.join(value.split())
    return value


def validate_forbidden_patterns(value, field_name='Поле'):
    """Проверка на запрещённые паттерны (XSS, SQL-инъекции)"""
    if not value:
        return
    value_str = str(value).lower()
    for pattern, description in FORBIDDEN_PATTERNS:
        if re.search(pattern, value_str, re.IGNORECASE | re.DOTALL):
            raise ValidationError(f'{field_name} содержит недопустимые символы или код ({description}).')


def validate_password_strength(password):
    """
    Строгая проверка пароля
    - Минимум 10 символов
    - Минимум 1 заглавная буква
    - Минимум 1 строчная буква
    - Минимум 1 цифра
    - Минимум 2 спецсимвола
    - Запрет распространённых паролей
    - Запрет последовательностей
    """
    errors = []
    
    if len(password) < 10:
        errors.append(_('Пароль должен содержать минимум 10 символов.'))
    
    if not re.search(r'[A-Z]', password):
        errors.append(_('Пароль должен содержать хотя бы одну заглавную букву.'))
    
    if not re.search(r'[a-z]', password):
        errors.append(_('Пароль должен содержать хотя бы одну строчную букву.'))
    
    if not re.search(r'\d', password):
        errors.append(_('Пароль должен содержать хотя бы одну цифру.'))
    
    special_chars = re.findall(r'[!@#$%^&*(),.?":{}|<>_\-=+\[\]\\;\'`~]', password)
    if len(special_chars) < 2:
        errors.append(_('Пароль должен содержать минимум 2 специальных символа.'))
    
    if password.lower() in COMMON_PASSWORDS:
        errors.append(_('Этот пароль слишком распространён. Выберите более уникальный.'))
    
    # Проверка на последовательности
    sequences = [
        '012', '123', '234', '345', '456', '567', '678', '789',
        'abc', 'bcd', 'cde', 'def', 'efg', 'fgh', 'ghi', 'hij',
        'ijk', 'jkl', 'klm', 'lmn', 'mno', 'nop', 'opq', 'pqr',
        'qrs', 'rst', 'stu', 'tuv', 'uvw', 'vwx', 'wxy', 'xyz',
        'qwerty', 'asdfgh', 'zxcvbn'
    ]
    
    for seq in sequences:
        if seq in password.lower():
            errors.append(_('Пароль не должен содержать последовательные символы.'))
            break
    
    # Проверка на повторяющиеся символы
    if re.search(r'(.)\1{2,}', password):
        errors.append(_('Пароль не должен содержать повторяющиеся символы (aaa, 111).'))
    
    if errors:
        raise ValidationError(errors)
    
    return password


def validate_email_domain(email):
    """Проверка домена email (Яндекс, Mail.ru, Gmail и официальные)"""
    try:
        domain = email.split('@')[1].lower()
    except (IndexError, AttributeError):
        raise ValidationError(_('Некорректный формат email.'))
    
    if domain not in [d.lower() for d in ALLOWED_EMAIL_DOMAINS]:
        raise ValidationError(
            _('Регистрация возможна только с разрешённых доменов: %(domains)s') % 
            {'domains': ', '.join(ALLOWED_EMAIL_DOMAINS[:5]) + ' и др.'}
        )
    
    return email


def validate_username_business_rule(username):
    """Валидация имени пользователя"""
    errors = []
    
    if len(username) < 4:
        errors.append(_('Имя пользователя должно быть не менее 4 символов.'))
    
    if len(username) > 30:
        errors.append(_('Имя пользователя не должно превышать 30 символов.'))
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        errors.append(_('Имя пользователя может содержать только буквы, цифры и подчёркивание.'))
    
    if username[0].isdigit():
        errors.append(_('Имя пользователя не может начинаться с цифры.'))
    
    username_lower = username.lower()
    for forbidden in FORBIDDEN_USERNAMES:
        if forbidden in username_lower:
            errors.append(_('Имя пользователя не может содержать слово "%(word)s".') % {'word': forbidden})
            break
    
    if errors:
        raise ValidationError(errors)
    
    return username


def validate_first_name_cyrillic(first_name):
    """Проверка: имя только на кириллице"""
    if not first_name or not first_name.strip():
        return first_name
    
    first_name = first_name.strip()
    
    if not re.match(r'^[а-яА-ЯёЁ\s-]+$', first_name):
        raise ValidationError(_('Имя должно быть написано только кириллицей.'))
    
    if len(first_name) < 2:
        raise ValidationError(_('Имя должно быть не менее 2 символов.'))
    
    if len(first_name) > 50:
        raise ValidationError(_('Имя не должно превышать 50 символов.'))
    
    return first_name


def validate_post_title(title):
    """Валидация заголовка поста"""
    if not title or not title.strip():
        raise ValidationError(_('Заголовок не может быть пустым.'))
    
    title = title.strip()
    
    if len(title) < 5:
        raise ValidationError(_('Заголовок должен быть не менее 5 символов.'))
    
    if len(title) > 200:
        raise ValidationError(_('Заголовок не должен превышать 200 символов.'))
    
    validate_forbidden_patterns(title, 'Заголовок')
    
    return title


def validate_post_content(content):
    """
    Валидация содержания поста
    - Проверка на осмысленность (минимум 20% гласных)
    - Нет XSS/SQL
    - Длина 50-10000 символов
    """
    if not content or not content.strip():
        raise ValidationError(_('Содержание не может быть пустым.'))
    
    content = content.strip()
    
    if len(content) < 50:
        raise ValidationError(_('Содержание должно быть не менее 50 символов.'))
    
    if len(content) > 10000:
        raise ValidationError(_('Содержание не должно превышать 10000 символов.'))
    
    validate_forbidden_patterns(content, 'Содержание')
    
    # Проверка на осмысленность (минимум 20% гласных букв)
    vowels = sum(1 for c in content.lower() if c in 'аеёиоуыэюяaeiou')
    if len(content) > 0 and vowels / len(content) < 0.2:
        raise ValidationError(_('Содержание должно содержать осмысленный текст (слишком много согласных или спецсимволов).'))
    
    # Проверка на повторяющийся текст (спам)
    words = content.split()
    if len(words) > 10:
        unique_words = set(words)
        if len(unique_words) / len(words) < 0.3:
            raise ValidationError(_('Содержание содержит слишком много повторяющихся слов.'))
    
    return content


def validate_comment_content(content):
    """Валидация комментария"""
    if not content or not content.strip():
        raise ValidationError(_('Комментарий не может быть пустым.'))
    
    content = content.strip()
    
    if len(content) < 10:
        raise ValidationError(_('Комментарий должен быть не менее 10 символов.'))
    
    if len(content) > 1000:
        raise ValidationError(_('Комментарий не должен превышать 1000 символов.'))
    
    validate_forbidden_patterns(content, 'Комментарий')
    
    return content


def validate_category_name(name):
    """Валидация названия категории"""
    if not name or not name.strip():
        raise ValidationError(_('Название категории не может быть пустым.'))
    
    name = name.strip()
    
    if len(name) < 3:
        raise ValidationError(_('Название категории должно быть не менее 3 символов.'))
    
    if len(name) > 50:
        raise ValidationError(_('Название категории не должно превышать 50 символов.'))
    
    validate_forbidden_patterns(name, 'Название категории')
    
    from .models import Category
    if Category.objects.filter(name__iexact=name).exists():
        raise ValidationError(_('Категория с таким названием уже существует.'))
    
    return name


def check_login_attempts(username):
    """Проверка попыток входа (блокировка после 5 неудачных за 15 мин)"""
    from .models import LoginAttempt
    
    fifteen_min_ago = timezone.now() - timezone.timedelta(minutes=15)
    
    failed_attempts = LoginAttempt.objects.filter(
        username__iexact=username,
        success=False,
        created_at__gte=fifteen_min_ago
    ).count()
    
    if failed_attempts >= 5:
        return False
    return True


def log_login_attempt(username, success, ip_address=None):
    """Логирование попытки входа"""
    from .models import LoginAttempt
    
    LoginAttempt.objects.create(
        username=username,
        success=success,
        ip_address=ip_address
    )