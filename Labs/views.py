from RestrictedPython import compile_restricted, safe_globals
from django.shortcuts import render
from RestrictedPython.PrintCollector import PrintCollector
from django.core.paginator import Paginator
from Labs.models import *
from RestrictedPython.Guards import safe_builtins



def MainPage(request):
    return render(request, "Labs/html/mainpage.html")


def Exercises(request):
    ex_list = list(i["id"] for i in Exercise.objects.all().values("id"))
    paginator = Paginator(ex_list, 1)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    print(page_obj)
    exercise = Exercise.objects.filter(id=page_number).values()[0]
    if request.method == "POST":
        safe_globals["_print_"] = PrintCollector
        safe_globals["_getattr_"] = getattr
        restricted_globals = dict(__builtins__=safe_builtins)
        user_code = request.POST.get("codefield")
        tests = Test.objects.filter(id=page_number)
        failed = False
        for test in tests:
            input_wrapper = f"""def input(*args,**kwargs):
    input.number=input.numbers+1
    return input.inputs[input.number] 
input.inputs={test.test_input.split(',')}
input.number=-1
      \n"""
            src = "def code():\n\t" + "\n\t".join(input_wrapper.split("\n")) + "\n\t".join(
                user_code.split("\n")) + "\n\treturn printed\nresult=code()"
            print(src)
            code = compile_restricted(src, '<string>', 'exec')
            exec(code, safe_globals)
            print(result)
            try:
                if str(code()) == test.expected_output:
                    continue
                else:
                    print(f'FAILED TEST result:{code()} expected: {test.expected_output}')
                    failed = True
                    break
            except Exception as exc:
                if test.is_exception and exc.__class__.__name__ == test.expected_result:
                    continue
                else:
                    print(f'FAILED TEST result:{exc.__class__.__name__} expected: {test.expected_output}')
                    print(exc)
                    failed = True
                    break
        return render(
            request, "Labs/html/exercises.html",
            context={"result": failed, "page_obj": page_obj, "title": exercise['title'], "text": exercise['task_text'],
                     "page": ex_list, "next_page": page_obj}
        )
    return render(request, "Labs/html/exercises.html",
                  context={"page_obj": page_obj, "title": exercise['title'], "text": exercise['task_text'],
                           "page": ex_list, "next_page": page_obj})
