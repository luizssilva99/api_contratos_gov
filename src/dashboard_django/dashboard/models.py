from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Perfil estendido do usuário para exibir cargo e departamento no header."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    cargo = models.CharField('Cargo', max_length=100, blank=True, default='Analista')
    departamento = models.CharField('Departamento', max_length=100, blank=True, default='Sinfra-MT')

    class Meta:
        verbose_name = 'Perfil de Usuário'
        verbose_name_plural = 'Perfis de Usuários'

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} - {self.cargo}'

    def get_initials(self):
        """Retorna as iniciais do nome do usuário para o avatar."""
        name = self.user.get_full_name()
        if name:
            parts = name.split()
            if len(parts) >= 2:
                return (parts[0][0] + parts[-1][0]).upper()
            return parts[0][0].upper()
        return self.user.username[0:2].upper()

    def get_display_name(self):
        """Retorna o nome de exibição para o header."""
        return self.user.get_full_name() or self.user.username
