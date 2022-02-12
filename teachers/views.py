from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import BulkUploadForm
from django.conf import settings
from django.http import Http404
from django.db.models import Q
from .models import *
import csv
import zipfile
import os

from django.views.generic import View
from django.views.generic import DetailView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin


def set_default_profile_pic(obj_teacher):
    try:
        with open(os.path.join(settings.MEDIA_ROOT,
                               'profilepic',
                               'default.png'),
                  'rb') as profile_picture_file:
            obj_teacher.profile_pic.save('default.png',
                                         profile_picture_file,
                                         True)
            return True
    except Exception as e:
        return False


def upload_teachers_from_csv(profiles_csv_file, images_zip_file):
    try:
        bytes_csv_content = profiles_csv_file.file.read()
        text_csv_content = bytes_csv_content.decode('UTF-8').splitlines()
        reader = csv.DictReader(text_csv_content)
        if images_zip_file is not None and zipfile.is_zipfile(images_zip_file):
            with zipfile.ZipFile(images_zip_file) as zfile:
                for t in reader:
                    if not t['Email Address']:
                        continue
                    lst_subject_obj = []
                    for data in t['Subjects taught'].title().split(','):
                        if len(lst_subject_obj) >= 5:
                            continue
                        if not Subjects.objects.filter(subject_name=data.title().strip()):
                            Subjects(subject_name=data.title().strip()).save()
                            get_subject = Subjects.objects.filter(subject_name=data.title().strip()).first()
                            lst_subject_obj.append(get_subject)
                        else:
                            get_subject = Subjects.objects.filter(subject_name=data.title().strip()).first()
                            lst_subject_obj.append(get_subject)
                    obj_teacher = Teachers(
                        first_name=t['First Name'],
                        last_name=t['Last Name'],
                        email_address=t['Email Address'],
                        phone_number=t['Phone Number'],
                        room_number=t['Room Number'],
                    )
                    obj_teacher.save()
                    for item in lst_subject_obj:
                        obj_teacher.subjects_taught.add(item)

                    if t['Profile picture'] not in zfile.namelist():
                        set_default_profile_pic(obj_teacher)
                    else:
                        with zfile.open(
                                t['Profile picture']) as profile_picture_file:
                            obj_teacher.profile_pic.save(t['Profile picture'],
                                                         profile_picture_file,
                                                         True)
                return True
    except Exception as e:
        return False


def base(request):
    return render(request, 'index.html')


class ViewAll(ListView):
    model = Teachers
    template_name = 'viewall.html'
    context_object_name = 'data'


class FileUploadView(LoginRequiredMixin, View):
    form_class = BulkUploadForm
    success_url = 'teachers:viewall'
    template_name = 'createrecord.html'
    login_url = "teachers:loginview"

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'bulk_upload_form': form})

    def post(self, request):

        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            Teachers.objects.all().delete()
            if upload_teachers_from_csv(request.FILES['csv_file'],
                                        request.FILES['images_archive']):
                messages.success(request, "Data uploaded successfully")
                return redirect(self.success_url)

        messages.error(request, "Invalid File, Please upload the required file")
        return render(request, self.template_name, {'bulk_upload_form': form})


class GetProfile(DetailView):
    model = Teachers
    template_name = 'viewprofile.html'
    context_object_name = 'data'


class SearchView(ListView):
    allow_empty = False
    template_name = 'searchpage.html'
    context_object_name = 'data'

    def get_queryset(self):
        search_query = self.request.GET.get('search_field')
        if search_query != "":
            subjects_available = Subjects.objects.filter(subject_name=search_query.title()).first()
            data = Teachers.objects.filter(
                Q(last_name__startswith=search_query) | Q(subjects_taught=subjects_available)).distinct()
            if not data:
                messages.warning(self.request, "No results found")
            return data
        messages.warning(self.request, "Please enter a valid query")

    def dispatch(self, *args):
        try:
            return super().dispatch(*args)
        except Http404:
            return redirect('teachers:base')


class CreateProfile(LoginRequiredMixin, View):
    template_name = 'home.html'
    success_url = 'teachers:viewall'
    login_url = "teachers:loginview"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        phonenumber = request.POST.get('phonenumber')
        roomnumber = request.POST.get('roomnumber')
        subjects = request.POST.get('subjects')
        profile_pic = request.FILES.get('myfile')

        check_teacher = Teachers.objects.filter(email_address=email)
        if check_teacher:
            messages.error(request, "user with same email id already exists")
            return render(request, self.template_name)
        subject_lst = []
        for data in subjects.title().split(','):
            subject_lst.append(data)
            if len(subject_lst) > 5:
                messages.warning(request, "Max 5 Subjects alloted for teachers")
                return render(request,self.template_name)
        obj_teacher = Teachers(first_name=fname, last_name=lname, email_address=email, phone_number=phonenumber,
                               room_number=roomnumber)
        for data in subject_lst:
            get_subject, created = Subjects.objects.get_or_create(subject_name=data)
            obj_teacher.save()
            obj_teacher.subjects_taught.add(get_subject)
        if not profile_pic:
            set_default_profile_pic(obj_teacher)
        else:
            obj_teacher.profile_pic = profile_pic
            obj_teacher.save()
        messages.success(request, "Succesfully uploaded")
        return redirect(self.success_url)
