from django.shortcuts import render


def sales_reports(request):
    return render(request, 'reports/sales_reports.html')
