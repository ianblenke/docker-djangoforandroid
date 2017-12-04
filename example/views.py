from django.views.generic.base import View
from django.shortcuts import render
from django.contrib.auth import authenticate, login


########################################################################
class Home(View):
    template = "home.html"

    #----------------------------------------------------------------------
    def get(self, request):
        """"""
        user = authenticate(username='user', password='djangoforandroid')
        login(request, user)

        return render(request, self.template, locals())