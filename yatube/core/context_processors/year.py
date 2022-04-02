from datetime import datetime


now = datetime.now()


def year(request):
    return {
        'year': now.year
    }
