from RestrictedPython import compile_restricted, safe_globals
from django.shortcuts import render
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from Labs.models import *
from RestrictedPython.Guards import safe_builtins
from django.contrib.auth.forms import AuthenticationForm


def MainPage(request):
    return render(request, "Labs/html/mainpage.html")


@login_required
def Exercises(request):
    ex_list = list(i["id"] for i in Exercise.objects.all().values("id"))
    paginator = Paginator(ex_list, 1)
    page_number = request.GET.get('page')
    tasks_done=CompletedTasks.objects.filter(user=request.user).values("exercise")
    page_obj = paginator.get_page(page_number)
    print(page_obj)
    exercise = Exercise.objects.get(id=page_number)
    if request.method == "POST":
        safe_globals["_getattr_"] = getattr
        restricted_globals = dict(__builtins__=safe_builtins)
        user_code = request.POST.get("codefield")
        tests = Test.objects.filter(for_task=page_number)
        success = True
        for test in tests:
            src = user_code
            print(src)
            exec(src)
            try:
                print(f'args={eval(test.test_input)}')
                if str(locals()['f'](eval(
                        test.test_input))) == test.expected_output:
                    continue
                else:
                    print(
                        f'FAILED TEST result:{str(locals()["f"](eval(test.test_input)))} expected: {test.expected_output}'
                    )
                    success = False
                    break
            except Exception as exc:
                if test.is_exception and exc.__class__.__name__ == test.expected_output:
                    print(
                        f'ran test, got expected exception {test.expected_output}'
                    )
                    continue
                else:
                    print(
                        f'FAILED TEST result:{exc.__class__.__name__} expected: {test.expected_output}'
                    )
                    print(exc)
                    success = False
                    break
        if success:
            completed_task = CompletedTasks.objects.create(user_id=request.user.id, exercise_id=exercise.id)
            completed_task.save()
        return render(request,
                      "Labs/html/exercises.html",
                      context={
                          "result": success,
                          "page_obj": page_obj,
                          "title": exercise.title,
                          "text": exercise.task_text,
                          "page": ex_list,
                          "next_page": page_obj,
                          "completed_tasks":tasks_done
                        })
    return render(request,
                  "Labs/html/exercises.html",
                  context={
                      "page_obj": page_obj,
                      "title": exercise.title,
                      "text": exercise.task_text,
                      "page": ex_list,
                      "next_page": page_obj,
                      "completed_tasks":[i['exercise'] for i in tasks_done]
                  })


from django.contrib.auth.views import LoginView


class LoginUser(LoginView):
    template_name = 'Labs/html/login.html'
    form_class = AuthenticationForm
