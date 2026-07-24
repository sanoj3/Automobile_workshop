from main_account.models import Fixigo

def fixigo_data(request):
    try:
        fixigo = Fixigo.objects.latest('id')
    except Fixigo.DoesNotExist:
        fixigo = None

    return {
        'fixigo': fixigo
    }