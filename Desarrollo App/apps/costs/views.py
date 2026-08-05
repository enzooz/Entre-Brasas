from django.shortcuts import render


def costs_view(request):
    return render(request, 'costs/costs_view.html')
