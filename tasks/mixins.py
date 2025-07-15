from django.core.exceptions import PermissionDenied

# Міксин для перевірки чи є користувач власником тієї чи іншої таски
# object - загальний вбудований клас, який відповідає за всі об'єкти
class UserIsOwnerMixin(object):
    # якщо хочемо щоб міксина виконуваласяя автоматично то використовуємо назву dispatch
    def dispatch(self, request, *args, **kwargs):
        # спробуємо отримати наш об'єкт
        # self - об'єкт який передається в цю міксину
        instance = self.get_object()
        # перевіряємо чи користувач, який створив таску, та користувач, який робить запит - це один і той самий користувач
        if instance.creator != self.request.user:
            raise PermissionDenied
        
        return super().dispatch(request, *args, **kwargs)
