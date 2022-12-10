from django.contrib import admin
from Labs.models import *


class ExerciseAdmin(admin.ModelAdmin):
    list_display = (
        "task_number",
        "title",
        "task_text",
    )


class TestAdmin(admin.ModelAdmin):
    list_dispaly = ("test_input", "input_type", "for_task", " is_exception")


class CompletedTasksAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "exercise",
    )


admin.site.register(Exercise, ExerciseAdmin)
admin.site.register(Test, TestAdmin)
admin.site.register(CompletedTasks, CompletedTasksAdmin)
