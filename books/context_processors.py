def user_role(request):
    """Добавляет информацию о роли пользователя в контекст всех шаблонов"""
    is_admin = False
    user_role_name = None
    
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            is_admin = profile.is_admin()
            user_role_name = profile.role.name if profile.role else 'Пользователь'
        except:
            is_admin = request.user.is_superuser
            user_role_name = 'Администратор' if request.user.is_superuser else 'Пользователь'
    
    return {
        'is_admin': is_admin,
        'user_role_name': user_role_name,
    }