from django.db import models
from django.contrib.auth.models import User


class Exercise(models.Model):
    task_number = models.IntegerField(verbose_name="Номер задачи")
    title = models.CharField(max_length=100, verbose_name="Название задачи")
    task_text = models.CharField(max_length=1000, verbose_name="Текст задачи")

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"


class Test(models.Model):
    test_input = models.CharField(max_length=255)
    for_task = models.ForeignKey(to='Exercise', on_delete=models.CASCADE, verbose_name="К задаче")
    expected_output = models.CharField(max_length=255, verbose_name="Ожидаемый ввод")
    is_exception = models.BooleanField(default=False, verbose_name="Ошибка")

    class Meta:
        verbose_name = "Тест"
        verbose_name_plural = "Тесты"


class CompletedTasks(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    exercise = models.ForeignKey(to='Exercise', verbose_name='Задача', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Выполненая задача"
        verbose_name_plural = "Выполненые задачи"
