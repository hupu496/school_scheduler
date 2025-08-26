from datetime import datetime

def today_date(request):
    return {'today': datetime.now()}