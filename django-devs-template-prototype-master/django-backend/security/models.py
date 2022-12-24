import os
import uuid
import requests
from crum import get_current_user
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group, Permission
from .managers import CustomUserManager
from crum import get_current_request
from .constants import CategoryModule, TypeModule

class ModelBase(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.CharField(max_length=100, blank=True, null=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    update_by = models.CharField(max_length=100, blank=True, null=True, editable=False)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True, editable=False)
    deleted_by = models.CharField(max_length=100, blank=True, null=True, editable=False)

    def save(self, *args, **kwargs):
        try:
            user = get_current_user()
            if self._state.adding:
                self.created_by = user.username
            else:
                self.update_by = user.username
        except:
            pass

        models.Model.save(self)

    class Meta:
        abstract = True

class ModelBaseAudited(models.Model):
    institution_id = models.IntegerField(verbose_name="Institución Code", blank=True, null=True, editable=False)
    detail = models.CharField(max_length=1024, verbose_name="Detalle", blank=True, null=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.CharField(max_length=100, blank=True, null=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    update_by = models.CharField(max_length=100, blank=True, null=True, editable=False)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True, editable=False)
    deleted_by = models.CharField(max_length=100, blank=True, null=True, editable=False)
    deleted_reason = models.CharField(max_length=191, blank=True, null=True, editable=False)

    def save(self, *args, **kwargs):
        try:
            user = get_current_user()
            if self._state.adding:
                self.created_by = user.username
            else:
                self.update_by = user.username
        except:
            pass

        models.Model.save(self)

    class Meta:
        abstract = True

class User(AbstractBaseUser, PermissionsMixin):
    pkid = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    username = models.CharField(verbose_name=_("Usuario"), max_length=191, unique=True)
    first_name = models.CharField(verbose_name=_("Nombres"), max_length=50, blank=True, null=True)
    last_name = models.CharField(verbose_name=_("Apellidos"), max_length=50, blank=True, null=True)
    email = models.EmailField(verbose_name=_("Email"), unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    foto = models.ImageField(
        upload_to='users/%Y/%m/%d/',
        verbose_name='Archive Photo',
        max_length=1024,
        blank=True, null=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return '{}'.format(self.username)

    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.username

    def get_foto_url(self):
        return self.foto.url

    def get_group_session(self):
        request = get_current_request()
        return Group.objects.filter(pk=request.session['group_id']).first()

    def set_group_session(self):
        try:
            request = get_current_request()
            if 'group' not in request.session:
                group = request.user.groups.all().first()
                if group is not None:
                    request.session['group_id'] = group.id
                    app_env = os.environ.get("APP_ENV", 'local')
                    if app_env != 'local':
                        request.session['infobyip'] = self.infobyip()
        except:
            pass

    def infobyip(self):
        response = {'ipaddress': '', 'location': '', 'isp': '', 'countrycode': ''}
        try:
            request = requests.get('https://wtfismyip.com/json').json()
            response = {
                'ipaddress': request['YourFuckingIPAddress'],
                'location': request['YourFuckingLocation'],
                'isp': request['YourFuckingISP'],
                'countrycode': request['YourFuckingCountryCode'],
            }
        except:
            pass
        return response

class Module(ModelBase):
    code = models.CharField(max_length=50, verbose_name="Código", blank=True, null=True)
    url = models.CharField(max_length=100, verbose_name="Enlace")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    category_module = models.CharField(max_length=20, verbose_name="Categoría módulo", blank=True, null=True, choices=CategoryModule.choices)
    type_module = models.CharField(max_length=20, verbose_name="Tipo módulo", blank=True, null=True, choices=TypeModule.choices)
    icon = models.CharField(max_length=100, verbose_name="Icono", blank=True, null=True)
    image = models.ImageField(upload_to='module/%Y/%m/%d', verbose_name='Imagen', null=True, blank=True)
    description = models.CharField(max_length=100, verbose_name="Descripción", blank=True, null=True)
    order = models.IntegerField(default=0, verbose_name="Orden", blank=True, null=True)
    visible = models.BooleanField(default=False, verbose_name="Visible")

    def __str__(self):
        return '{} ({})'.format(self.name, self.url)

    class Meta:
        verbose_name = 'Módulo'
        verbose_name_plural = 'Módulos'
        ordering = ['order']

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        if self.code:
            self.code = self.code.upper()

        ModelBase.save(self)

class ModuleGrupCategory(ModelBase):
    code = models.CharField(max_length=50, verbose_name="Código", blank=True, null=True)
    name = models.CharField(max_length=100, verbose_name="Nombre")
    order = models.IntegerField(default=0, verbose_name="Orden", blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        verbose_name = 'Categoria principal'
        verbose_name_plural = 'Categorias principal'
        ordering = ['created_at']

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        if self.code:
            self.code = self.code.upper()
        if self.name:
            self.name = self.name.upper()

        ModelBase.save(self)

class ModuleGrupPermissions(ModelBase):
    description = models.CharField(max_length=100, verbose_name="Descripción", blank=True, null=True)
    main_category = models.ForeignKey(ModuleGrupCategory, on_delete=models.CASCADE, verbose_name='Categoria principal', blank=True, null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name="Grupo", blank=True, null=True)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, verbose_name="Módulo", blank=True, null=True)
    permissions = models.ManyToManyField(Permission, verbose_name='Permisos', blank=True)
    priority = models.IntegerField(verbose_name="Prioridad", blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.description, self.priority)

    class Meta:
        verbose_name = 'Grupo de Módulos Permisos'
        verbose_name_plural = 'Grupos de Módulos Permisos'
        ordering = ['priority']

    def get_grup_category_modules(self):
        return self.group.modulegruppermissions_set.filter(
            module__visible=True,
            main_category = self.main_category
        )
