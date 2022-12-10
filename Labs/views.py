from django.shortcuts import render
from django.core.paginator import Paginator
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from Labs.models import *
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.http import HttpResponseServerError
from django.contrib.auth.forms import AuthenticationForm,UserCreationForm
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from Labs.forms import RegistrationForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.decorators.debug import sensitive_post_parameters
from django.utils.decorators import method_decorator


def MainPage(request):
    return render(request, "Labs/html/mainpage.html")


@login_required
def Exercises(request):
    ex_list = list(i["id"] for i in Exercise.objects.all().values("id"))
    paginator = Paginator(ex_list, 1)
    page_number = request.GET.get("page") or 1
    tasks_done = CompletedTasks.objects.filter(user=request.user).values("exercise")
    tasks_wrong = CompletedTasks.objects.filter(user=request.user, correct=False).values("exercise")
    page_obj = paginator.get_page(page_number)
    print(page_obj)
    exercise = Exercise.objects.get(id=page_number)
    if request.method == "POST":
        user_code = request.POST.get("codefield")
        tests = Test.objects.filter(for_task=page_number)
        success = True
        for test in tests:
            src = user_code
            print(src)
            try:
                exec(src)
            except Exception as exc:
                success = False
                print(f"compilation exception {exc}")
                break
            try:
                print(f"args={eval(test.test_input)}")
                if str(locals()["f"](eval(test.test_input))) == test.expected_output:
                    continue
                else:
                    print(
                        f'FAILED TEST result:{str(locals()["f"](eval(test.test_input)))} expected: {test.expected_output}'
                    )
                    success = False
                    break
            except Exception as exc:
                if test.is_exception and exc.__class__.__name__ == test.expected_output:
                    print(f"ran test, got expected exception {test.expected_output}")
                    continue
                else:
                    print(
                        f"FAILED TEST result:{exc.__class__.__name__} expected: {test.expected_output}"
                    )
                    print(exc)
                    success = False
                    break
        try:
            completed_task = CompletedTasks.objects.get(
                user=request.user, exercise_id=exercise.id
            )
        except CompletedTasks.DoesNotExist:
            completed_task = CompletedTasks.objects.create(
                user_id=request.user.id, exercise_id=exercise.id, correct=success
            )
        completed_task.correct = success
        completed_task.save()
        tasks_done = CompletedTasks.objects.filter(user=request.user, correct=True).values("exercise")
        tasks_wrong = CompletedTasks.objects.filter(user=request.user, correct=False).values("exercise")
        return render(
            request,
            "Labs/html/exercises.html",
            context={
                "result": success,
                "page_obj": page_obj,
                "title": exercise.title,
                "text": exercise.task_text,
                "page": ex_list,
                "next_page": page_obj,
                "completed_tasks": [i["exercise"] for i in tasks_done],
                "incompleted_tasks": [i["exercise"] for i in tasks_wrong],
            },
        )
    return render(
        request,
        "Labs/html/exercises.html",
        context={
            "page_obj": page_obj,
            "title": exercise.title,
            "text": exercise.task_text,
            "page": ex_list,
            "next_page": page_obj,
            "completed_tasks": [i["exercise"] for i in tasks_done],
            "incompleted_tasks": [i["exercise"] for i in tasks_wrong],
        },
    )


@login_required
def clear_solved_tasks(request):
    try:
        CompletedTasks.objects.filter(user=request.user).delete()
    except Exception:
        return HttpResponseServerError()
    return redirect(reverse_lazy("tasks"))


class LoginUser(LoginView):
    template_name = "Labs/html/login.html"
    next_page = reverse_lazy("mainpage")





class RegisterUser(CreateView):
    form_class = RegistrationForm
    template_name = "Labs/html/register.html"

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(reverse_lazy("mainpage"))
    
    @method_decorator(sensitive_post_parameters('password1', 'password2'))
    def dispatch(self, request, *args, **kwargs):
        """
        Check that user signup is allowed before even bothering to
        dispatch or do other processing.

        """
        if request.user.is_authenticated:
            return redirect(reverse_lazy("mainpage"))
        return super(RegisterUser, self).dispatch(request, *args, **kwargs)


