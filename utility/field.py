from django.db import models
import time

class UnixTimestampField(models.IntegerField):
    def __init__(self, auto_now=False, auto_now_add = False,*args, **kwargs):
        self.auto_now = auto_now
        self.auto_now_add = auto_now_add
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add, *args, **kwargs):
        # Check if the object is being created
        if add and self.auto_now_add:
            setattr(model_instance, self.attname, int(time.time()))
        elif self.auto_now:
            setattr(model_instance, self.attname, int(time.time()))
        return super().pre_save(model_instance, add, *args, **kwargs)